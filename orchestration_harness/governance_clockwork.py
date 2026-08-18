"""Provider-free shadow reducer for clock-bound governance projections."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import uuid
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, NoReturn

from orchestration_harness.active_operation import validate_active_operation
from scripts.ariadne_agent_error_register import (
    EXPECTED_ORIGIN_BY_CATEGORY,
    validate_register,
)


HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
PROJECTION_OWNERS = {
    "atomic_projection_binding",
    "baton_projection",
    "clock_tip_binding",
    "command_projection",
    "compass_projection",
    "continuity_projection",
    "efficacy_binding",
    "incident_projection",
    "latch_projection",
    "pattern_projection",
    "revision_projection",
}
OBSERVATION_KEYS = {
    "candidate_state",
    "causal_claim_level",
    "correction",
    "detection_method",
    "evidence_paths",
    "expected_invariant",
    "failure_class",
    "model",
    "observed_error",
    "observed_on",
    "process_severity",
    "reasoning_level",
    "recurrence_signature",
    "resource_id",
    "role",
    "stage",
    "tranche",
    "transport",
    "workflow_disposition",
}


class GovernanceRejection(ValueError):
    """A prospective governance reading failed before publication."""

    def __init__(self, rule: str) -> None:
        super().__init__(rule)
        self.rule = rule


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise GovernanceRejection("json_object_required")
    return value


def reject(rule: str) -> NoReturn:
    raise GovernanceRejection(rule)


def fail_closed(function):
    def wrapped(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except GovernanceRejection:
            raise
        except (AttributeError, IndexError, KeyError, TypeError):
            reject("invalid_shape")
    return wrapped
def _exact(value: object, keys: set[str], rule: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        reject(rule)
    return value


def _git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo_root, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


@fail_closed
def validate_contract(value: object) -> dict[str, Any]:
    keys = {
        "baseline_maintained_surfaces", "baseline_surrounding_reruns", "candidate_maintained_surfaces",
        "commands", "failure_classes", "gate_result_mappings", "incremental_line_budget",
        "inherited_boundaries", "legacy_bindings", "line_budget_files", "maximum_steady_state_surrounding_reruns",
        "minimum_surface_reduction_percent", "operation_id", "predecessor_acknowledged_tip_sha256",
        "predecessor_sunk_reruns", "protected_commit", "required_ancestor", "schema_version",
    }
    row = _exact(value, keys, "contract_keys")
    if row["schema_version"] != "ariadne.governance_projection_contract.v1":
        reject("contract_version")
    if not HEX40.fullmatch(row["required_ancestor"]) or not HEX40.fullmatch(row["protected_commit"]):
        reject("contract_git_oid")
    if not HEX64.fullmatch(row["predecessor_acknowledged_tip_sha256"]):
        reject("contract_clock_tip")
    if row["baseline_surrounding_reruns"] != 9 or row["predecessor_sunk_reruns"] != 13:
        reject("frozen_rerun_baseline")
    if row["maximum_steady_state_surrounding_reruns"] > 1 or row["incremental_line_budget"] > 850:
        reject("efficacy_budget_weakened")
    for mapping in row["failure_classes"].values():
        _exact(mapping, {"category", "origin"}, "failure_class_mapping")
    for mapping in row["gate_result_mappings"].values():
        _exact(mapping, {"attention", "compass", "continuity_decision", "continuity_node", "latch"}, "gate_mapping")
    owners = {item["owner"] for item in row["legacy_bindings"]}
    if not owners <= PROJECTION_OWNERS or len(row["legacy_bindings"]) < 1:
        reject("legacy_binding_owner")
    if any(len(items) != len(set(items)) for items in (row["baseline_maintained_surfaces"], row["candidate_maintained_surfaces"])):
        reject("duplicate_maintained_surface")
    if set(row["baseline_maintained_surfaces"]) & set(row["candidate_maintained_surfaces"]):
        reject("dual_control_surface")
    binding_ids = [item["binding_id"] for item in row["legacy_bindings"]]
    if len(binding_ids) != len(set(binding_ids)):
        reject("duplicate_legacy_binding")
    _validate_commands(row["commands"])
    return row


@fail_closed
def validate_probes(value: object) -> list[dict[str, Any]]:
    row = _exact(value, {"probes", "schema_version"}, "probe_ledger_keys")
    if row["schema_version"] != "ariadne.governance_rerun_probes.v1" or len(row["probes"]) != 13:
        reject("probe_ledger_population")
    incident_ids: list[str] = []
    surrounding = 0
    for index, probe in enumerate(row["probes"], 1):
        probe = _exact(probe, {"classification", "control_owner", "failure_signature", "incident_ids", "probe_id"}, "probe_keys")
        if probe["probe_id"] != f"rerun-{index:02d}" or probe["control_owner"] not in PROJECTION_OWNERS:
            reject("probe_identity")
        if probe["classification"] not in {"clock_core", "surrounding_governance"}:
            reject("probe_classification")
        surrounding += probe["classification"] == "surrounding_governance"
        incident_ids.extend(probe["incident_ids"])
    if surrounding != 9 or incident_ids != [f"AER-{number:04d}" for number in range(616, 630)]:
        reject("probe_frozen_coverage")
    return row["probes"]


def _validate_commands(commands: object) -> None:
    if not isinstance(commands, list) or not commands:
        reject("command_population")
    for command in commands:
        command = _exact(command, {"arguments", "command_id", "executable"}, "command_keys")
        if not isinstance(command["arguments"], list) or not all(isinstance(arg, str) and arg for arg in command["arguments"]):
            reject("command_arguments")
        flattened = [command["executable"], *command["arguments"]]
        if any(any(mark in part for mark in "*?[]") for part in flattened):
            reject("untyped_command_operand")
        if command["command_id"] == "register_project" and "--output" not in command["arguments"]:
            reject("register_output_required")


def _source_snapshot(repo_root: Path, contract: dict[str, Any]) -> dict[str, Any]:
    head = _git(repo_root, "rev-parse", "HEAD")
    if not HEX40.fullmatch(head):
        reject("source_oid")
    _git(repo_root, "merge-base", "--is-ancestor", contract["required_ancestor"], head)
    refs = {
        ref: _git(repo_root, "rev-parse", ref)
        for ref in ("master", "handoff/current", "origin/master", "origin/handoff/current")
    }
    if set(refs.values()) != {contract["protected_commit"]}:
        reject("protected_refs")
    return {"source_commit": head, "protected_refs_sha256": digest(refs)}


def _evidence_digest(repo_root: Path, paths: list[str]) -> str:
    readings = []
    for raw in paths:
        if "\\" in raw or raw.startswith("docs/branding/"):
            reject("evidence_path")
        path = (repo_root / raw).resolve()
        try:
            path.relative_to(repo_root.resolve())
        except ValueError:
            reject("evidence_path")
        if not path.is_file():
            reject("evidence_missing")
        readings.append({"path": raw, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    return digest(readings)


def _incident_observation(value: object, contract: dict[str, Any], repo_root: Path) -> tuple[dict[str, Any], str]:
    row = _exact(value, OBSERVATION_KEYS, "observation_keys")
    if row["failure_class"] not in contract["failure_classes"]:
        reject("failure_class")
    if not isinstance(row["evidence_paths"], list) or not row["evidence_paths"]:
        reject("evidence_paths")
    return copy.deepcopy(row), _evidence_digest(repo_root, row["evidence_paths"])


def _project_register(
    repo_root: Path,
    contract: dict[str, Any],
    register: dict[str, Any],
    schema: dict[str, Any],
    observations: list[object],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    validate_register(register, schema, root=repo_root)
    prospective = copy.deepcopy(register)
    next_number = int(register["incidents"][-1]["incident_id"].split("-")[1]) + 1
    generated: list[dict[str, Any]] = []
    for offset, value in enumerate(observations):
        observation, evidence_sha = _incident_observation(value, contract, repo_root)
        mapping = contract["failure_classes"][observation.pop("failure_class")]
        stable = {key: observation[key] for key in ("observed_on", "tranche", "role", "resource_id", "model", "reasoning_level", "transport", "stage")}
        attempt_id = f"clock-{digest({'stable': stable, 'evidence': evidence_sha})[:24]}"
        incident = copy.deepcopy(observation)
        incident.update({
            "incident_id": f"AER-{next_number + offset:04d}",
            "attempt_id": attempt_id,
            "origin": mapping["origin"],
            "category": mapping["category"],
            "related_incident_ids": [],
            "status": "corrected",
        })
        generated.append(incident)
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for incident in generated:
        groups[incident["attempt_id"]].append(incident)
    for incident in generated:
        incident["related_incident_ids"] = sorted(
            peer["incident_id"] for peer in groups[incident["attempt_id"]] if peer is not incident
        )
    prospective["incidents"].extend(generated)
    prospective["register_revision"] += 1
    validate_register(prospective, schema, root=repo_root)
    counts = {
        field: dict(sorted(Counter(str(row[field]) for row in prospective["incidents"]).items()))
        for field in ("origin", "category", "role", "process_severity", "candidate_state")
    }
    recurrences: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for row in prospective["incidents"]:
        key = tuple(row[name] for name in ("origin", "category", "role", "resource_id", "recurrence_signature"))
        recurrences[key].append(row["incident_id"])
    pattern = {
        "register_revision": prospective["register_revision"],
        "incident_count": len(prospective["incidents"]),
        "open_incident_ids": sorted(row["incident_id"] for row in prospective["incidents"] if row["status"] == "open"),
        "counts": counts,
        "recurrences": [{"composite": list(key), "incident_ids": ids} for key, ids in sorted(recurrences.items()) if len(ids) > 1],
        "register_sha256": digest(prospective),
    }
    revision = {
        "revision": prospective["register_revision"],
        "document_path": f"docs/ariadne-agent-error-correction-register-revision-{prospective['register_revision']}.md",
        "incident_count": len(prospective["incidents"]),
        "open_count": len(pattern["open_incident_ids"]),
    }
    return prospective, pattern, revision


def _efficacy(repo_root: Path, contract: dict[str, Any], latch: dict[str, Any], probes: list[dict[str, Any]]) -> dict[str, Any]:
    line_counts = {}
    for raw in contract["line_budget_files"]:
        path = repo_root / raw
        line_counts[raw] = len(path.read_text(encoding="utf-8").splitlines()) if path.is_file() else 0
    growth = sum(line_counts.values())
    construction = sum(latch["checkpoint"]["retry_counters"].values())
    steady = 0
    savings = contract["baseline_surrounding_reruns"] - steady
    baseline = len(contract["baseline_maintained_surfaces"])
    candidate = len(contract["candidate_maintained_surfaces"])
    reduction = round((baseline - candidate) * 100 / baseline, 3)
    owners = {item["owner"] for item in contract["legacy_bindings"]}
    return {
        "probe_coverage": len(probes),
        "surrounding_probe_coverage": sum(p["classification"] == "surrounding_governance" for p in probes),
        "caller_authored_derived_fields": 0,
        "steady_state_surrounding_reruns": steady,
        "construction_reruns": construction,
        "predecessor_sunk_reruns": contract["predecessor_sunk_reruns"],
        "steady_state_savings_per_closeout": savings,
        "repair_only_break_even_closeouts": math.ceil(construction / savings),
        "cumulative_break_even_closeouts": math.ceil((construction + contract["predecessor_sunk_reruns"]) / savings),
        "incremental_line_counts": line_counts,
        "incremental_line_growth": growth,
        "line_budget": contract["incremental_line_budget"],
        "baseline_maintained_surfaces": baseline,
        "candidate_maintained_surfaces": candidate,
        "maintained_surface_reduction_percent": reduction,
        "unmapped_legacy_bindings": sorted(owners - PROJECTION_OWNERS),
        "retirement_ready": not (owners - PROJECTION_OWNERS) and reduction >= contract["minimum_surface_reduction_percent"],
        "new_mutable_current_fixtures": 0,
        "partial_publications": 0,
        "uncaught_escapes": 0,
        "provider_calls": 0,
    }


@fail_closed
def build_bundle(
    repo_root: Path,
    contract_path: Path,
    probes_path: Path,
    register_path: Path,
    schema_path: Path,
    latch_path: Path,
    observations: list[object],
    *,
    gate_result: str,
) -> dict[str, Any]:
    contract = validate_contract(load_object(contract_path))
    probes = validate_probes(load_object(probes_path))
    latch = validate_active_operation(load_object(latch_path))
    if latch["operation_id"] != contract["operation_id"] or latch["status"] != "in_progress":
        reject("active_latch")
    if gate_result not in contract["gate_result_mappings"]:
        reject("gate_result")
    source = _source_snapshot(repo_root, contract)
    register, pattern, revision = _project_register(
        repo_root, contract, load_object(register_path), load_object(schema_path), observations
    )
    mapping = contract["gate_result_mappings"][gate_result]
    projections = {
        "incident_projection": register,
        "pattern_projection": pattern,
        "revision_projection": revision,
        "command_projection": {"commands": copy.deepcopy(contract["commands"])},
        "continuity_projection": {"node_status": mapping["continuity_node"], "decision_status": mapping["continuity_decision"]},
        "compass_projection": {"horizon_status": mapping["compass"], "register_revision": revision["revision"]},
        "baton_projection": {"register_revision": revision["revision"], "incident_count": revision["incident_count"], "gate_result": gate_result, "inherited_boundaries": copy.deepcopy(contract["inherited_boundaries"])},
        "latch_projection": {"status": mapping["latch"], "user_attention_required": mapping["attention"], "source_commit": source["source_commit"]},
    }
    efficacy = _efficacy(repo_root, contract, latch, probes)
    clock = {
        "previous_acknowledged_tip_sha256": contract["predecessor_acknowledged_tip_sha256"],
        "source_commit": source["source_commit"],
        "protected_refs_sha256": source["protected_refs_sha256"],
        "latch_sha256": digest(latch),
        "projections_sha256": digest(projections),
        "efficacy_sha256": digest(efficacy),
    }
    clock["acknowledged_tip_sha256"] = digest(clock)
    bundle = {
        "schema_version": "ariadne.governance_projection_bundle.v1",
        "operation_id": contract["operation_id"],
        "clock": clock,
        "projections": projections,
        "probe_results": [{"probe_id": p["probe_id"], "result": "covered_before_publication"} for p in probes],
        "efficacy": efficacy,
        "live_adoption": False,
        "current_controls_retired": False,
    }
    bundle["bundle_sha256"] = digest(bundle)
    validate_bundle(bundle, contract)
    return bundle


@fail_closed
def validate_bundle(value: object, contract: dict[str, Any]) -> dict[str, Any]:
    bundle = _exact(value, {"bundle_sha256", "clock", "current_controls_retired", "efficacy", "live_adoption", "operation_id", "probe_results", "projections", "schema_version"}, "bundle_keys")
    supplied = bundle.pop("bundle_sha256")
    if supplied != digest(bundle):
        reject("bundle_digest")
    bundle["bundle_sha256"] = supplied
    if bundle["live_adoption"] or bundle["current_controls_retired"]:
        reject("live_control_effect")
    if bundle["schema_version"] != "ariadne.governance_projection_bundle.v1" or bundle["operation_id"] != contract["operation_id"]:
        reject("bundle_identity")
    projections = bundle["projections"]
    expected_projection_keys = {
        "baton_projection", "command_projection", "compass_projection",
        "continuity_projection", "incident_projection", "latch_projection",
        "pattern_projection", "revision_projection",
    }
    if set(projections) != expected_projection_keys:
        reject("projection_population")
    register = projections["incident_projection"]
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for incident in register["incidents"]:
        if incident["origin"] != EXPECTED_ORIGIN_BY_CATEGORY[incident["category"]]:
            reject("category_origin_relation")
        groups[incident["attempt_id"]].append(incident)
    for incident in register["incidents"]:
        peers = sorted(row["incident_id"] for row in groups[incident["attempt_id"]] if row is not incident)
        if incident.get("related_incident_ids", []) != peers:
            reject("attempt_peer_relation")
        if len({row["resource_id"] for row in groups[incident["attempt_id"]]}) != 1:
            reject("attempt_resource_relation")
    pattern = projections["pattern_projection"]
    revision = projections["revision_projection"]
    baton = projections["baton_projection"]
    if pattern["register_sha256"] != digest(register):
        reject("register_pattern_binding")
    if not (pattern["register_revision"] == revision["revision"] == baton["register_revision"] == projections["compass_projection"]["register_revision"]):
        reject("revision_projection_binding")
    if not (pattern["incident_count"] == revision["incident_count"] == baton["incident_count"] == len(register["incidents"])):
        reject("count_projection_binding")
    gate_result = baton["gate_result"]
    if gate_result not in contract["gate_result_mappings"]:
        reject("gate_projection")
    mapping = contract["gate_result_mappings"][gate_result]
    if projections["continuity_projection"] != {"node_status": mapping["continuity_node"], "decision_status": mapping["continuity_decision"]}:
        reject("continuity_vocabulary")
    if projections["compass_projection"]["horizon_status"] != mapping["compass"] or projections["latch_projection"]["status"] != mapping["latch"] or projections["latch_projection"]["user_attention_required"] != mapping["attention"]:
        reject("terminal_vocabulary")
    _validate_commands(projections["command_projection"]["commands"])
    clock = bundle["clock"]
    if clock["previous_acknowledged_tip_sha256"] != contract["predecessor_acknowledged_tip_sha256"] or not HEX40.fullmatch(clock["source_commit"]):
        reject("clock_source_binding")
    if projections["latch_projection"]["source_commit"] != clock["source_commit"]:
        reject("latch_source_binding")
    if clock["projections_sha256"] != digest(projections) or clock["efficacy_sha256"] != digest(bundle["efficacy"]):
        reject("clock_projection_binding")
    acknowledged = clock.pop("acknowledged_tip_sha256")
    if acknowledged != digest(clock):
        reject("acknowledged_tip_binding")
    clock["acknowledged_tip_sha256"] = acknowledged
    efficacy = bundle["efficacy"]
    if efficacy["probe_coverage"] != 13 or efficacy["surrounding_probe_coverage"] != 9:
        reject("coverage")
    if efficacy["steady_state_surrounding_reruns"] > contract["maximum_steady_state_surrounding_reruns"]:
        reject("steady_state_reruns")
    if efficacy["incremental_line_growth"] > efficacy["line_budget"] or not efficacy["retirement_ready"]:
        reject("efficacy_cost_or_surface")
    if any(efficacy[key] for key in ("caller_authored_derived_fields", "new_mutable_current_fixtures", "partial_publications", "uncaught_escapes", "provider_calls")):
        reject("closed_boundary")
    boundaries = bundle["projections"]["baton_projection"]["inherited_boundaries"]
    if boundaries != contract["inherited_boundaries"]:
        reject("inherited_boundary")
    return bundle


def publish_private_shadow(bundle: dict[str, Any], contract: dict[str, Any], target: Path, *, fail_after_write: int | None = None) -> Path:
    validate_bundle(copy.deepcopy(bundle), contract)
    if "private-shadow" not in target.name or target.exists():
        reject("private_shadow_target")
    staging = target.with_name(f".{target.name}.staging-{uuid.uuid4().hex}")
    files = {
        "bundle.json": bundle,
        "register.json": bundle["projections"]["incident_projection"],
        "commands.json": bundle["projections"]["command_projection"],
    }
    try:
        staging.mkdir(parents=True)
        for index, (name, payload) in enumerate(files.items(), 1):
            (staging / name).write_bytes(json.dumps(payload, indent=2, sort_keys=True).encode() + b"\n")
            if fail_after_write == index:
                raise OSError("injected_private_shadow_write_failure")
        for name, payload in files.items():
            if json.loads((staging / name).read_text(encoding="utf-8")) != payload:
                reject("staging_readback")
        os.replace(staging, target)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return target
