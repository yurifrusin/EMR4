"""Pure verification of supervisor-anchored local execution captures.

The caller supplies an anchor authenticated through the existing controller
checkpoint/receipt boundary. Neither a worker result nor this module establishes
that trust root. A digest proves byte identity only. This local component never
certifies hidden model context, settles usage or authorises execution/effects.
"""
from __future__ import annotations

import base64
import hashlib
import json
import re

from .verdict import ArtifactKind, ReviewVerdict, parse_artifact_verdict

VERSION = "ariadne.local_execution_capture.v1"
ANCHOR_VERSION = "ariadne.execution_capture_anchor.v1"
PROFILE = "reviewed_local_process_v1"
MAX_BUNDLE = 2 * 1024 * 1024
MAX_BLOB = 128 * 1024
ROLES = ("generator", "verifier", "red")
SEVERITIES = {"critical", "high", "medium", "low", "dev-only"}


class ProvenanceError(ValueError):
    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)


def need(value, reason):
    if not value:
        raise ProvenanceError(reason)


def keys(value, expected, reason="record_schema"):
    need(type(value) is dict and set(value) == set(expected.split()), reason)
    return value


def integer(value, minimum=0, maximum=(1 << 63) - 1):
    return type(value) is int and minimum <= value <= maximum


def label(value):
    return type(value) is str and re.fullmatch(r"[A-Za-z0-9_.-]{1,128}", value) is not None


def digest(value):
    return type(value) is str and re.fullmatch(r"sha256:[0-9a-f]{64}", value) is not None


def sha(raw):
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def canonical(value):
    def visit(item, depth=0):
        need(depth <= 32, "record_depth")
        if type(item) is dict:
            need(all(type(k) is str for k in item), "record_key_type")
            for part in item.values():
                visit(part, depth + 1)
        elif type(item) is list:
            need(len(item) <= 256, "record_list_limit")
            for part in item:
                visit(part, depth + 1)
        else:
            need(item is None or type(item) in (str, int, bool), "record_value_type")
    visit(value)
    try:
        raw = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    except (ValueError, UnicodeError, RecursionError) as error:
        raise ProvenanceError("record_encoding") from error
    need(len(raw) <= MAX_BUNDLE, "record_size")
    return raw


def document(raw):
    def pairs(rows):
        result = {}
        for key, value in rows:
            need(key not in result, "duplicate_record_key")
            result[key] = value
        return result
    need(type(raw) is bytes and len(raw) <= MAX_BUNDLE, "record_size")
    try:
        value = json.loads(raw, object_pairs_hook=pairs)
        need(type(value) is dict and canonical(value) == raw, "record_not_canonical")
        return value
    except (ValueError, TypeError, UnicodeError, RecursionError) as error:
        if isinstance(error, ProvenanceError):
            raise
        raise ProvenanceError("record_encoding") from error


def blob(raw):
    need(type(raw) is bytes and len(raw) <= MAX_BLOB, "blob_size")
    return {"sha256": sha(raw), "base64": base64.b64encode(raw).decode()}


def unblob(value):
    keys(value, "sha256 base64", "blob_schema")
    need(digest(value["sha256"]) and type(value["base64"]) is str
         and len(value["base64"]) <= 4 * ((MAX_BLOB + 2) // 3), "blob_size")
    try:
        raw = base64.b64decode(value["base64"], validate=True)
    except (ValueError, UnicodeError) as error:
        raise ProvenanceError("blob_encoding") from error
    need(blob(raw) == value, "blob_digest_mismatch")
    return raw


def _labels(value, maximum=64):
    need(type(value) is list and len(value) <= maximum
         and all(label(v) for v in value) and len(set(value)) == len(value), "label_list")


def validate_assignment(value):
    keys(value, "assignment_id operation_id attempt_id scope_sha256 controller_reference "
         "observer_source_sha256 executable_sha256 created_ns not_after_ns policy scope workers spec")
    need(all(label(value[k]) for k in ("assignment_id", "operation_id", "attempt_id")), "assignment_identity")
    need(all(digest(value[k]) for k in ("scope_sha256", "controller_reference", "observer_source_sha256",
                                      "executable_sha256")), "assignment_digest")
    need(integer(value["created_ns"]) and integer(value["not_after_ns"])
         and 0 < value["not_after_ns"] - value["created_ns"] <= 300_000_000_000, "assignment_deadline")
    policy = keys(value["policy"], "source_sha256 security_triggers external_triggers required_checks live_model_required")
    need(type(policy["source_sha256"]) is dict and set(policy["source_sha256"]) ==
         {"operating_model", "verifier_execution_policy", "security_review_protocol"}
         and all(label(k) and digest(v) for k, v in policy["source_sha256"].items()), "policy_sources")
    for name in ("security_triggers", "external_triggers", "required_checks"):
        _labels(policy[name])
        need(bool(policy[name]), "policy_requirements_missing")
    need(type(policy["live_model_required"]) is bool, "policy_model_requirement")
    scope = keys(value["scope"], "action domain triggers classification_evidence non_material_rationale")
    need(scope["action"] in {"read", "repair_edit", "recovery_publish"}
         and scope["domain"] in {"artifact", "controller", "configuration", "security"}, "scope_classification")
    _labels(scope["triggers"])
    need(set(scope["triggers"]) <= set(policy["security_triggers"]) | set(policy["external_triggers"]),
         "unknown_risk_trigger")
    need(digest(scope["classification_evidence"]), "classification_evidence_missing")
    need(type(scope["non_material_rationale"]) is str and len(scope["non_material_rationale"]) <= 4096,
         "classification_rationale")
    tier = required_tier(value)
    if tier == "routine_delta":
        need(bool(scope["non_material_rationale"].strip()), "classification_evidence_missing")
    workers = value["workers"]
    needed = {"generator", "verifier", "red"} if tier == "dual_review" else {"generator", "verifier"}
    need(type(workers) is dict and set(workers) == needed, "required_worker_roles")
    for role, worker in workers.items():
        keys(worker, "worker_id principal_id lineage_id source_sha256")
        need(all(label(worker[k]) for k in ("worker_id", "principal_id", "lineage_id"))
             and digest(worker["source_sha256"]), "worker_assignment")
    for name in ("worker_id", "principal_id", "lineage_id", "source_sha256"):
        need(len({w[name] for w in workers.values()}) == len(workers), "worker_lineage_not_independent")
    need(len(unblob(value["spec"])) <= 32768, "spec_size")
    return tier


def required_tier(assignment):
    scope, policy = assignment["scope"], assignment["policy"]
    sensitive = scope["action"] == "recovery_publish" or scope["domain"] != "artifact"
    sensitive = sensitive or bool(set(scope["triggers"]) &
                                  (set(policy["security_triggers"]) | set(policy["external_triggers"])))
    return "dual_review" if sensitive else "routine_delta"


def packet_for(assignment, role, candidate=None):
    """The supervisor assembles these bytes; reviewer output cannot choose inputs."""
    need(role in assignment["workers"], "unassigned_role")
    inputs = [{"name": "spec", "content": assignment["spec"]}]
    if role != "generator":
        need(type(candidate) is bytes, "candidate_missing")
        inputs.append({"name": "candidate", "content": blob(candidate)})
    return canonical({"schema_version": "ariadne.local_worker_packet.v1", "profile": PROFILE,
        "assignment_id": assignment["assignment_id"], "operation_id": assignment["operation_id"],
        "attempt_id": assignment["attempt_id"], "scope_sha256": assignment["scope_sha256"],
        "assignment_sha256": sha(canonical(assignment)), "role": role,
        "worker_id": assignment["workers"][role]["worker_id"],
        "required_checks": assignment["policy"]["required_checks"] if role == "verifier" else [],
        "inputs": inputs})


def _worker_artifact(raw, role):
    result = document(raw)
    names = "candidate decision findings" if role == "generator" else "decision findings checks"
    keys(result, names, "worker_artifact_schema")
    need(type(result["decision"]) is str and len(result["decision"]) <= 16384, "decision_encoding")
    findings = result["findings"]
    need(type(findings) is list and len(findings) <= 64, "findings_schema")
    ids = set()
    for finding in findings:
        keys(finding, "finding_id severity resolved", "finding_schema")
        need(label(finding["finding_id"]) and finding["finding_id"] not in ids
             and finding["severity"] in SEVERITIES and type(finding["resolved"]) is bool, "finding_schema")
        ids.add(finding["finding_id"])
        # A worker's own resolved flag cannot clear a blocking finding.
        need(finding["severity"] not in {"critical", "high"}, "blocking_finding_requires_resolution")
    assessment = parse_artifact_verdict(result["decision"], ArtifactKind.DECISION)
    need(assessment.artifact_valid, "invalid_review_verdict")
    need(assessment.review_verdict is ReviewVerdict.PASS, "required_review_negative")
    if role == "generator":
        unblob(result["candidate"])
    else:
        need(type(result["checks"]) is dict and len(result["checks"]) <= 64
             and all(label(k) and integer(v, -255, 255) for k, v in result["checks"].items()), "checks_schema")
    return result


def inspect_capture(bundle_raw, anchor_raw, *, expected_anchor_sha256, expected_assignment_id,
                    expected_scope_sha256, expected_controller_reference, now_ns):
    """Expected anchor identity comes from trusted controller state, never the bundle."""
    need(type(anchor_raw) is bytes and digest(expected_anchor_sha256), "trusted_anchor_required")
    need(sha(anchor_raw) == expected_anchor_sha256, "controller_anchor_mismatch")
    anchor = document(anchor_raw)
    keys(anchor, "schema_version assignment_id assignment_sha256 bundle_sha256 observer_source_sha256 "
         "controller_reference scope_sha256 sealed_ns profile", "anchor_schema")
    need(anchor["schema_version"] == ANCHOR_VERSION and anchor["profile"] == PROFILE, "anchor_profile")
    need(anchor["assignment_id"] == expected_assignment_id and anchor["scope_sha256"] == expected_scope_sha256
         and anchor["controller_reference"] == expected_controller_reference, "anchor_assignment_mismatch")
    need(sha(bundle_raw) == anchor["bundle_sha256"], "capture_digest_mismatch")
    bundle = document(bundle_raw)
    keys(bundle, "schema_version profile assignment observations candidate sealed_ns complete", "capture_schema")
    need(bundle["schema_version"] == VERSION and bundle["profile"] == PROFILE and bundle["complete"] is True,
         "incomplete_capture")
    assignment = bundle["assignment"]
    tier = validate_assignment(assignment)
    need(sha(canonical(assignment)) == anchor["assignment_sha256"]
         and assignment["assignment_id"] == anchor["assignment_id"]
         and assignment["scope_sha256"] == anchor["scope_sha256"]
         and assignment["controller_reference"] == anchor["controller_reference"]
         and assignment["observer_source_sha256"] == anchor["observer_source_sha256"], "assignment_binding_mismatch")
    need(integer(now_ns) and integer(bundle["sealed_ns"]) and bundle["sealed_ns"] == anchor["sealed_ns"]
         and assignment["created_ns"] <= bundle["sealed_ns"] <= now_ns < assignment["not_after_ns"], "capture_stale")
    candidate = unblob(bundle["candidate"])
    observations = bundle["observations"]
    expected_roles = [role for role in ROLES if role in assignment["workers"]]
    need(type(observations) is list and len(observations) == len(expected_roles), "incomplete_capture")
    seen_runs, seen_processes = set(), set()
    last_end = assignment["created_ns"]
    for role, observation in zip(expected_roles, observations, strict=True):
        keys(observation, "role run_id worker_id principal_id lineage_id source executable_sha256 pid argv environment cwd "
             "started_ns stopped_ns packet stdout stderr exit_code timed_out output_truncated streams_closed",
             "observation_schema")
        worker = assignment["workers"][role]
        need(observation["role"] == role and all(observation[k] == worker[k]
             for k in ("worker_id", "principal_id", "lineage_id")), "observed_worker_mismatch")
        source = unblob(observation["source"])
        need(sha(source) == worker["source_sha256"] and observation["executable_sha256"] == assignment["executable_sha256"],
             "observed_source_mismatch")
        argv = observation["argv"]
        need(type(argv) is list and len(argv) == 6 and type(argv[0]) is str and bool(argv[0])
             and argv[1:] == ["-I", "-B", "-S", "-c", source.decode("utf-8")], "observed_invocation_mismatch")
        environment = observation["environment"]
        need(type(environment) is dict and (environment == {"LANG": "C.UTF-8"}
             or set(environment) == {"SYSTEMROOT"} and type(environment["SYSTEMROOT"]) is str
             and bool(environment["SYSTEMROOT"])), "observed_environment_mismatch")
        need(type(observation["cwd"]) is str and bool(observation["cwd"]), "observed_cwd_missing")
        process_identity = (observation["pid"], observation["started_ns"])
        need(label(observation["run_id"]) and observation["run_id"] not in seen_runs
             and integer(observation["pid"], 1) and process_identity not in seen_processes, "observed_execution_reused")
        seen_runs.add(observation["run_id"])
        seen_processes.add(process_identity)
        need(integer(observation["started_ns"]) and integer(observation["stopped_ns"])
             and last_end <= observation["started_ns"] <= observation["stopped_ns"] <= bundle["sealed_ns"],
             "observed_execution_order")
        last_end = observation["stopped_ns"]
        need(type(observation["timed_out"]) is bool and type(observation["output_truncated"]) is bool
             and type(observation["streams_closed"]) is bool and type(observation["exit_code"]) is int,
             "observation_exit_schema")
        need(not observation["timed_out"] and not observation["output_truncated"] and observation["streams_closed"]
             and observation["exit_code"] == 0, "execution_incomplete")
        need(unblob(observation["stderr"]) == b"", "execution_stderr")
        need(unblob(observation["packet"]) == packet_for(assignment, role, candidate), "context_membership_mismatch")
        result = _worker_artifact(unblob(observation["stdout"]), role)
        if role == "generator":
            need(unblob(result["candidate"]) == candidate, "generated_candidate_mismatch")
        elif role == "verifier":
            need(set(result["checks"]) == set(assignment["policy"]["required_checks"]), "required_checks_missing")
            need(all(code == 0 for code in result["checks"].values()), "deterministic_check_failed")
        else:
            need(not result["checks"], "red_context_check_contract")
    need(not assignment["policy"]["live_model_required"], "live_model_provenance_unavailable")
    return {"component_verified": True, "reason_codes": [], "required_tier": tier,
        "assignment_id": assignment["assignment_id"], "candidate_sha256": sha(candidate),
        "capture_sha256": sha(bundle_raw), "verified_roles": expected_roles, "profile": PROFILE,
        "operational_acceptance": False, "execution_authorized": False,
        "integration_authorized": False, "usage_settlement_authorized": False}


def evaluate_capture(*args, **kwargs):
    try:
        return inspect_capture(*args, **kwargs)
    except (ProvenanceError, TypeError, KeyError, ValueError, UnicodeError, RecursionError) as error:
        reason = error.reason if isinstance(error, ProvenanceError) else "invalid_capture"
        return {"component_verified": False, "reason_codes": [reason], "required_tier": None,
            "profile": PROFILE, "operational_acceptance": False, "execution_authorized": False,
            "integration_authorized": False, "usage_settlement_authorized": False}
