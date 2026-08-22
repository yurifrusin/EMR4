"""Read-only post-attempt-008 canonical check-in readiness convergence review."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCHEMA_VERSION = (
    "raisa.canonical_check_in_admission_readiness_post_attempt_008_"
    "convergence_contract.v1"
)
EVIDENCE_SCHEMA_VERSION = (
    "raisa.canonical_check_in_admission_readiness_post_attempt_008_"
    "convergence_evidence.v1"
)
PLAN_SOURCE = "7fb98cbe1f9a814a237172e58f911008e68aad82"
HASH_MODE = "strict_utf8_canonical_lf_reject_bare_cr_sha256"
CLASSIFICATIONS = ("satisfied", "blocking_gap", "operational_evidence_gap")
VERDICT = "not_ready_for_ordinary_practice_admission"
RESULT = (
    "raisa_provider_free_read_only_canonical_check_in_ordinary_practice_"
    "admission_readiness_post_attempt_008_convergence_review_pass"
)
TIMESTAMP = "2026-08-23T07:48:00.0000000+10:00"

BASE = (
    "orchestration/continuity/raisa-provider-free-read-only-canonical-check-in-"
    "ordinary-practice-admission-readiness-post-attempt-008-convergence-review"
)
CONTRACT_PATH = f"{BASE}/contract.json"
SCHEMA_PATH = f"{BASE}/contract.schema.json"
EVIDENCE_PATH = f"{BASE}/evidence.json"
REPORT_PATH = f"{BASE}/report.md"

PRIOR_BASE = (
    "orchestration/continuity/raisa-provider-free-read-only-canonical-check-in-"
    "ordinary-practice-admission-readiness-convergence-review"
)
PRIOR_CONTRACT = f"{PRIOR_BASE}/contract.json"
PRIOR_EVIDENCE = f"{PRIOR_BASE}/evidence.json"
PRIOR_REPORT = f"{PRIOR_BASE}/report.md"
PRIOR_CLOSEOUT = (
    "docs/raisa-provider-free-read-only-canonical-check-in-ordinary-practice-"
    "admission-readiness-convergence-review-closeout.md"
)
PRIOR_ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-canonical-check-in-admission-"
    "readiness-convergence-review-sol-acceptance.md"
)

ATTEMPT_BASE = (
    "orchestration/continuity/raisa-provider-free-check-in-relay-free-"
    "recovery-attempt-008"
)
ATTEMPT_EVIDENCE = f"{ATTEMPT_BASE}/rehearsal-evidence.json"
ATTEMPT_ATTESTATION = f"{ATTEMPT_BASE}/transaction-attestation.json"
ATTEMPT_ENVELOPE = f"{ATTEMPT_BASE}/attempt-008-execution-envelope.json"
ATTEMPT_REPORT = f"{ATTEMPT_BASE}/closeout-report.md"
ATTEMPT_CLOSEOUT = (
    "docs/raisa-provider-free-check-in-relay-free-recovery-attempt-008-closeout.md"
)
ATTEMPT_ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-check-in-relay-free-recovery-"
    "attempt-008-sol-acceptance.md"
)

GIT_OBJECTS = {
    "prior_convergence_source": "369c1284af87631a94ffff04ca530cf4c74db4b8",
    "attempt_008_closeout_source": "4cba1edebe9bd924ff49f757935ca898845cbf99",
    "attempt_008_occupied_source": "9f37ede79a915172e449c1f2d19bdba3eb592b44",
    "attempt_008_terminal_commit": "0e50f7f48d9c8622341a1679db507de78b1260a5",
}

INPUT_BINDINGS = (
    (PRIOR_CONTRACT, "4172ccbf5b59827919c8a4a56b7b8e5482ee026f17f8fac21abb2edba25bc051"),
    (PRIOR_EVIDENCE, "bd77d5940a9286437a1d528938c4b4bad981c1ed6cb6037752e7326da1a4e97c"),
    (PRIOR_REPORT, "88f38bd9def2ceacdd1cd8a51077e97c495c28d4bfa5eb30b252063c0fcd51f4"),
    (PRIOR_CLOSEOUT, "1266219bb6ce833cb1a09e01f070f8989b137b9ce366fad25cb83fede177a137"),
    (PRIOR_ACCEPTANCE, "2908d0d4ecb08bf17f663a6317c0c713798eaf41fe99507a5d64d614f29a6eab"),
    (ATTEMPT_EVIDENCE, "d15a06188b7399df13fc4871a34e273e72969de16b729bdf360436b4d794d0b8"),
    (ATTEMPT_ATTESTATION, "d7967117f59fadde447ca0e848c428ef3461ee12a4bd140f715d8b067be5890e"),
    (ATTEMPT_ENVELOPE, "50ce4f4ef672d9392062f40c87833c63fc9eac2f4c3979567fb81da5ac0b81ce"),
    (ATTEMPT_REPORT, "7a7b3ca09d0abc4eefafa0677c92b315b3ebe05e112102cd96b6f427f4d18c40"),
    (ATTEMPT_CLOSEOUT, "d72962cfadcb16922a891d2958545650ca61c3d7570a0da4a53c0b79111ebf29"),
    (ATTEMPT_ACCEPTANCE, "7f4547133e908124c20923be588121c6a1b042e1e20ac059d655d82c242eae6f"),
)

DIMENSIONS = (
    (1, "current_default_off_and_empty_ordinary_posture", "satisfied", "original_accepted"),
    (2, "ordinary_practice_admission_control", "satisfied", "accepted_admission_kernel"),
    (3, "api_spine_contract_and_route_identity", "satisfied", "original_accepted"),
    (4, "authentication_and_dual_receptionist_authorization", "satisfied", "original_accepted"),
    (5, "tenant_isolation_and_runtime_database_role", "satisfied", "accepted_disposable_postgresql_attestation"),
    (6, "idempotency_evidence_and_replay", "satisfied", "original_accepted"),
    (7, "atomic_effect_rollback_and_unknown_commit_recovery", "satisfied", "accepted_attempt_008_one_shot_transaction_terminal"),
    (8, "append_only_audit_and_committed_event", "satisfied", "original_accepted"),
    (9, "ordinary_rollout_kill_switch_and_rollback_runbook", "satisfied", "accepted_default_off_runbook"),
    (10, "non_phi_observability_and_alerting", "satisfied", "accepted_non_phi_manifest_and_unmounted_adapter"),
    (11, "environment_manifest_and_operational_secret_posture", "operational_evidence_gap", "architecture_has_zero_operational_instances"),
    (12, "client_cutover_and_waiting_area_separation", "satisfied", "original_accepted"),
)
PRIOR_DIMENSIONS = tuple(
    (
        order,
        dimension_id,
        "operational_evidence_gap" if order == 7 else classification,
        "attempt_005_failed_before_transaction_evidence" if order == 7 else basis,
    )
    for order, dimension_id, classification, basis in DIMENSIONS
)
PRIOR_COUNTS = {"satisfied": 10, "blocking_gap": 0, "operational_evidence_gap": 2}
EXPECTED_COUNTS = {"satisfied": 11, "blocking_gap": 0, "operational_evidence_gap": 1}
REQUIRED_OPEN_GAPS = ("environment_manifest_and_operational_secret_posture",)
CLOSED_BOUNDARIES = (
    "no_app_import_or_product_runtime",
    "no_route_database_docker_sql_browser_provider_model_harness_or_network",
    "no_ordinary_practice_enablement_or_admission_release",
    "no_product_configuration_api_openapi_graphql_client_or_waiting_area_change",
    "no_product_patient_appointment_clinical_historical_or_protected_data",
    "no_environment_manifest_or_secret_posture_claim",
    "no_deployment_release_pages_or_protected_ref_movement",
    "preserve_docs_branding_and_all_unrelated_untracked_files",
)
TRANSACTION_CRITERIA = (
    "one_shot_attempt_passed",
    "no_retry_resume_or_fallback",
    "explicit_rollback_zero_effect",
    "incomplete_response_released_no_success_or_retry",
    "authoritative_readback_committed_exactly_once",
    "restricted_non_bypass_forced_rls_posture",
    "zero_ordinary_or_product_records",
    "finalized_cleanup_and_zero_owned_residue",
    "terminal_hashes_and_closed_boundaries_bound",
)
UNCHANGED_PRODUCT_PATHS = (
    "app/routers/appointments.py",
    "app/services/appointment_check_in_product_adapter.py",
    "app/schemas/appointments.py",
    "docs/api-spine/openapi/appointment-commands.yaml",
    "docs/api-spine/graphql",
    "docs/diary/diary.js",
)


class ContractError(RuntimeError):
    """The frozen contract or an exact source binding changed."""


class EvidenceError(RuntimeError):
    """The accepted packets cannot prove the frozen transition."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def canonical_text(root: Path, relative: str) -> str:
    root = root.resolve()
    path = (root / relative).resolve()
    require(path.is_relative_to(root), f"path escapes repository: {relative}")
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContractError(f"non-UTF-8 source: {relative}") from exc
    require("\r" not in text.replace("\r\n", ""), f"bare CR source: {relative}")
    return text.replace("\r\n", "\n")


def canonical_sha256(root: Path, relative: str) -> str:
    return hashlib.sha256(canonical_text(root, relative).encode("utf-8")).hexdigest()


def load_json(root: Path, relative: str) -> dict[str, Any]:
    value = json.loads(canonical_text(root, relative))
    require(isinstance(value, dict), f"JSON object required: {relative}")
    return value


def git_object_is_ancestor(root: Path, object_id: str) -> bool:
    process = subprocess.run(
        ["git", "merge-base", "--is-ancestor", object_id, "HEAD"],
        cwd=root,
        check=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return process.returncode == 0


def product_paths_are_unchanged(root: Path) -> bool:
    process = subprocess.run(
        [
            "git",
            "diff",
            "--quiet",
            f"{GIT_OBJECTS['prior_convergence_source']}..HEAD",
            "--",
            *UNCHANGED_PRODUCT_PATHS,
        ],
        cwd=root,
        check=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return process.returncode == 0


def validate_contract(
    contract: dict[str, Any], root: Path, *, check_sources: bool = True
) -> None:
    require(
        set(contract)
        == {
            "schema_version",
            "planning_source",
            "input_hash_mode",
            "accepted_git_objects",
            "inputs",
            "classifications",
            "dimensions",
            "prior_expected_counts",
            "acceptance",
            "closed_boundaries",
        },
        "top-level keys changed",
    )
    require(contract["schema_version"] == SCHEMA_VERSION, "schema version changed")
    require(contract["planning_source"] == PLAN_SOURCE, "planning source changed")
    require(contract["input_hash_mode"] == HASH_MODE, "hash mode changed")
    require(tuple(contract["classifications"]) == CLASSIFICATIONS, "classifications changed")
    require(contract["accepted_git_objects"] == GIT_OBJECTS, "accepted Git objects changed")

    for label, object_id in {
        "planning_source": contract["planning_source"],
        **contract["accepted_git_objects"],
    }.items():
        require(re.fullmatch(r"[0-9a-f]{40}", object_id) is not None, f"invalid full Git ID: {label}")
        if check_sources:
            require(git_object_is_ancestor(root, object_id), f"Git object is not an ancestor: {label}")

    inputs = contract["inputs"]
    require(isinstance(inputs, list) and len(inputs) == len(INPUT_BINDINGS), "input count changed")
    observed_bindings: list[tuple[str, str]] = []
    for item in inputs:
        require(isinstance(item, dict) and set(item) == {"path", "sha256"}, "input shape changed")
        require(isinstance(item["path"], str), "input path changed")
        require(re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is not None, "invalid SHA-256")
        observed_bindings.append((item["path"], item["sha256"]))
    require(tuple(observed_bindings) == INPUT_BINDINGS, "input bindings changed")
    if check_sources:
        for relative, digest in INPUT_BINDINGS:
            require(canonical_sha256(root, relative) == digest, f"source hash changed: {relative}")

    observed_dimensions = tuple(
        (
            item.get("order"),
            item.get("id"),
            item.get("expected_classification"),
            item.get("basis"),
        )
        for item in contract["dimensions"]
        if isinstance(item, dict) and set(item) == {"order", "id", "expected_classification", "basis"}
    )
    require(observed_dimensions == DIMENSIONS, "dimension order, vocabulary or basis changed")
    require(contract["prior_expected_counts"] == PRIOR_COUNTS, "prior counts changed")
    require(
        contract["acceptance"]
        == {
            "expected_counts": EXPECTED_COUNTS,
            "expected_verdict": VERDICT,
            "minimum_hostile_mutations": 120,
            "required_open_gaps": list(REQUIRED_OPEN_GAPS),
        },
        "acceptance changed",
    )
    require(tuple(contract["closed_boundaries"]) == CLOSED_BOUNDARIES, "closed boundaries changed")


def validate_prior_packet(
    prior_contract: dict[str, Any], prior: dict[str, Any], texts: dict[str, str]
) -> list[dict[str, Any]]:
    require(
        prior_contract.get("schema_version")
        == "raisa.canonical_check_in_admission_readiness_convergence_review_contract.v1",
        "prior contract schema changed",
    )
    require(prior_contract.get("planning_source") == "f4623fed8d12011a9a34747d12696e5e6017f18b", "prior planning source changed")
    require(prior_contract.get("acceptance", {}).get("expected_counts") == PRIOR_COUNTS, "prior contract counts changed")
    require(
        prior.get("result")
        == "raisa_provider_free_read_only_canonical_check_in_ordinary_practice_admission_readiness_convergence_review_pass",
        "prior result changed",
    )
    require(prior.get("dimension_counts") == PRIOR_COUNTS, "prior evidence counts changed")
    require(
        prior.get("operational_evidence_gaps")
        == [
            "atomic_effect_rollback_and_unknown_commit_recovery",
            "environment_manifest_and_operational_secret_posture",
        ],
        "prior open gaps changed",
    )
    require(prior.get("blocking_gaps") == [], "prior blocking gaps changed")
    require(prior.get("verdict") == VERDICT, "prior verdict changed")
    require(prior.get("hostile_mutations_rejected", 0) >= 120, "prior hostile coverage changed")
    require(
        all(value is False for value in prior.get("closed_boundaries", {}).values()),
        "prior boundary opened",
    )
    dimensions = prior.get("dimensions")
    require(isinstance(dimensions, list) and len(dimensions) == 12, "prior dimensions changed")
    observed = tuple(
        (item.get("order"), item.get("id"), item.get("classification"), item.get("basis"))
        for item in dimensions
    )
    require(observed == PRIOR_DIMENSIONS, "prior dimension matrix changed")
    source = GIT_OBJECTS["prior_convergence_source"]
    require(source in texts[PRIOR_CLOSEOUT], "prior source missing from closeout")
    require(source in texts[PRIOR_ACCEPTANCE], "prior source missing from acceptance")
    return dimensions


def validate_attempt_packet(
    evidence: dict[str, Any],
    attestation: dict[str, Any],
    envelope: dict[str, Any],
    texts: dict[str, str],
) -> dict[str, bool]:
    occupied = GIT_OBJECTS["attempt_008_occupied_source"]
    terminal = GIT_OBJECTS["attempt_008_terminal_commit"]
    require(
        evidence.get("result")
        == "raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal_pass",
        "attempt evidence result changed",
    )
    require(evidence.get("source_head") == occupied, "attempt evidence source changed")
    require(len(evidence.get("scenarios", [])) == 12, "attempt scenario count changed")
    require(all(item.get("status") == "passed" for item in evidence["scenarios"]), "attempt scenario failed")
    require(evidence.get("hostile_mutations", {}).get("escapes") == 0, "attempt hostile mutation escaped")
    require(evidence.get("source_binding_count") == 15, "attempt source binding count changed")

    rollback = attestation.get("explicit_rollback", {})
    require(rollback.get("classification") == "rolled_back_zero_effect", "rollback classification changed")
    require(rollback.get("staged_counts") == {"audit": 1, "effect": 1, "receipt": 1}, "rollback staged packet changed")
    require(rollback.get("readback_counts") == {"audit": 0, "effect": 0, "receipt": 0}, "rollback readback changed")

    ambiguous = attestation.get("ambiguous_response", {})
    require(ambiguous.get("classification") == "connection_lost_without_complete_terminal_response", "ambiguous response changed")
    require(ambiguous.get("complete_terminal_response") is False, "complete response observed")
    require(ambiguous.get("success_released") is False, "ambiguous success released")
    require(ambiguous.get("retry_count") == 0, "ambiguous response retried")
    require(ambiguous.get("exact_backend_observed") is True, "backend observation absent")
    require(ambiguous.get("exact_backend_terminated") is True, "backend termination absent")
    require(ambiguous.get("caller_state", {}).get("exit_code") == 42, "caller terminal changed")

    readback = attestation.get("authoritative_readback", {})
    require(readback.get("classification") == "committed_exactly_once", "readback classification changed")
    require(readback.get("counts") == {"audit": 1, "effect": 1, "receipt": 1}, "readback packet changed")
    require(readback.get("duplicate_effect_count") == 0, "duplicate effect observed")
    require(readback.get("other_practice_visible_count") == 0, "cross-practice visibility observed")

    role = attestation.get("role_catalogue", {})
    for key in ("superuser", "bypass_rls", "create_database", "create_role", "inherit", "replication"):
        require(role.get(key) is False, f"restricted role privilege changed: {key}")
    for key in ("memberships", "owned_objects", "product_privileges"):
        require(role.get(key) == 0, f"restricted role ownership changed: {key}")
    relation = attestation.get("relation_catalogue", {})
    require(relation.get("relation_count") == 3, "relation count changed")
    require(relation.get("rls_enabled_count") == 3, "RLS enabled count changed")
    require(relation.get("rls_forced_count") == 3, "forced RLS count changed")
    require(relation.get("grants_exact") is True, "relation grants changed")

    require(attestation.get("ordinary_admission_release_count") == 0, "ordinary admission released")
    require(attestation.get("product_record_count") == 0, "product record created")
    require(attestation.get("redaction", {}).get("status") == "passed", "attestation redaction failed")
    require(attestation.get("redaction", {}).get("forbidden_fields") == 0, "forbidden attestation field")
    require(attestation.get("redaction", {}).get("forbidden_values") == 0, "forbidden attestation value")

    cleanup = evidence.get("cleanup", {})
    require(cleanup.get("status") == "cleanup_verified", "cleanup not verified")
    require(cleanup.get("matching_owned_resources") == 0, "owned residue present")
    for key in ("attachments_absent", "network_absent", "role_absent_before_teardown", "server_absent", "sidecars_absent"):
        require(cleanup.get(key) is True, f"cleanup absence changed: {key}")
    require(all(value is False for value in evidence.get("closed_boundaries", {}).values()), "attempt boundary opened")

    require(
        envelope.get("result")
        == "raisa_provider_free_check_in_relay_free_recovery_attempt_008_pass",
        "attempt envelope result changed",
    )
    require(envelope.get("source_head") == occupied, "attempt envelope source changed")
    require(envelope.get("occupied_execution_count") == 1, "occupied execution count changed")
    require(envelope.get("automatic_retry_count") == 0, "automatic retry occurred")
    require(envelope.get("resume_count") == 0, "resume occurred")
    require(envelope.get("fallback_count") == 0, "fallback occurred")
    require(envelope.get("ambiguous_success_released") is False, "envelope released success")
    require(envelope.get("ordinary_admission_release_count") == 0, "envelope released admission")
    require(envelope.get("product_record_count") == 0, "envelope recorded product")
    require(envelope.get("cleanup_status") == "cleanup_verified", "envelope cleanup changed")
    require(envelope.get("terminal_binding_restored") is True, "terminal binding not restored")
    require(envelope.get("finalized_cleanup_projection_preserved") is True, "cleanup projection lost")
    require(envelope.get("terminal_artifact_sha256") == INPUT_BINDINGS[5][1], "evidence hash binding changed")
    require(envelope.get("transaction_attestation_sha256") == INPUT_BINDINGS[6][1], "attestation hash binding changed")
    require(evidence.get("attestation_sha256") == INPUT_BINDINGS[6][1], "evidence attestation binding changed")
    require(attestation.get("source_head") == occupied, "attestation source changed")

    require(occupied in texts[ATTEMPT_CLOSEOUT], "occupied source missing from closeout")
    require(terminal in texts[ATTEMPT_CLOSEOUT], "terminal commit missing from closeout")
    require(occupied in texts[ATTEMPT_ACCEPTANCE], "occupied source missing from acceptance")
    require(terminal in texts[ATTEMPT_ACCEPTANCE], "terminal commit missing from acceptance")
    return {criterion: True for criterion in TRANSACTION_CRITERIA}


def derive_dimensions(prior: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = copy.deepcopy(prior)
    row = result[6]
    require(row.get("order") == 7 and row.get("id") == DIMENSIONS[6][1], "dimension 7 identity changed")
    row["classification"] = "satisfied"
    row["basis"] = "accepted_attempt_008_one_shot_transaction_terminal"
    row["citations"] = [
        ATTEMPT_EVIDENCE,
        ATTEMPT_ATTESTATION,
        ATTEMPT_ENVELOPE,
        ATTEMPT_REPORT,
        ATTEMPT_CLOSEOUT,
        ATTEMPT_ACCEPTANCE,
    ]
    row["markers"] = [
        "one_occupied_invocation_zero_retry_resume_fallback",
        "explicit_rollback_zero_effect_receipt_audit",
        "incomplete_response_no_success_or_retry",
        "fresh_readback_committed_exactly_once",
        "zero_duplicates_and_cross_practice_visibility",
        "forced_rls_non_bypass_role",
        "cleanup_verified_zero_owned_residue",
    ]
    observed = tuple(
        (item.get("order"), item.get("id"), item.get("classification"), item.get("basis"))
        for item in result
    )
    require(observed == DIMENSIONS, "derived dimension matrix changed")
    return result


def hostile_mutations(contract: dict[str, Any], root: Path) -> int:
    mutations: list[dict[str, Any]] = []
    for index in range(len(contract["inputs"])):
        candidate = copy.deepcopy(contract)
        del candidate["inputs"][index]
        mutations.append(candidate)
        candidate = copy.deepcopy(contract)
        candidate["inputs"][index]["path"] = "AGENTS.md"
        mutations.append(candidate)
        candidate = copy.deepcopy(contract)
        digest = candidate["inputs"][index]["sha256"]
        candidate["inputs"][index]["sha256"] = ("0" if digest[0] != "0" else "1") + digest[1:]
        mutations.append(candidate)
        candidate = copy.deepcopy(contract)
        candidate["inputs"][index]["extra"] = True
        mutations.append(candidate)
    for label, object_id in contract["accepted_git_objects"].items():
        candidate = copy.deepcopy(contract)
        candidate["accepted_git_objects"][label] = object_id[:7]
        mutations.append(candidate)
        candidate = copy.deepcopy(contract)
        candidate["accepted_git_objects"][label] = "0" * 40
        mutations.append(candidate)
        candidate = copy.deepcopy(contract)
        del candidate["accepted_git_objects"][label]
        mutations.append(candidate)
    for index, dimension in enumerate(contract["dimensions"]):
        candidate = copy.deepcopy(contract)
        candidate["dimensions"][index]["id"] += "_drift"
        mutations.append(candidate)
        candidate = copy.deepcopy(contract)
        candidate["dimensions"][index]["basis"] += "_drift"
        mutations.append(candidate)
        candidate = copy.deepcopy(contract)
        candidate["dimensions"][index]["expected_classification"] = next(
            value for value in CLASSIFICATIONS if value != dimension["expected_classification"]
        )
        mutations.append(candidate)
        candidate = copy.deepcopy(contract)
        candidate["dimensions"][index]["order"] = 99
        mutations.append(candidate)
        candidate = copy.deepcopy(contract)
        candidate["dimensions"][index]["extra"] = True
        mutations.append(candidate)
    for key, value in (
        ("schema_version", "mutated"),
        ("planning_source", PLAN_SOURCE[:7]),
        ("input_hash_mode", "mutated"),
        ("classifications", ["satisfied"]),
        ("prior_expected_counts", {}),
        ("acceptance", {}),
        ("closed_boundaries", []),
    ):
        candidate = copy.deepcopy(contract)
        candidate[key] = value
        mutations.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["extra"] = True
    mutations.append(candidate)

    rejected = 0
    for candidate in mutations:
        try:
            validate_contract(candidate, root, check_sources=False)
        except (ContractError, KeyError, TypeError):
            rejected += 1
        else:
            raise EvidenceError("hostile contract mutation escaped")
    return rejected


def build_evidence(
    contract: dict[str, Any],
    dimensions: list[dict[str, Any]],
    criteria: dict[str, bool],
    rejected: int,
) -> dict[str, Any]:
    counts = Counter(item["classification"] for item in dimensions)
    ordered_counts = {name: counts.get(name, 0) for name in CLASSIFICATIONS}
    require(ordered_counts == EXPECTED_COUNTS, f"unexpected counts: {ordered_counts}")
    gaps = [item["id"] for item in dimensions if item["classification"] == "operational_evidence_gap"]
    require(tuple(gaps) == REQUIRED_OPEN_GAPS, "open gaps changed")
    require(all(criteria.values()) and tuple(criteria) == TRANSACTION_CRITERIA, "transaction criteria changed")
    require(rejected >= contract["acceptance"]["minimum_hostile_mutations"], "too few hostile mutations")
    return {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "result": RESULT,
        "planning_source": PLAN_SOURCE,
        "accepted_git_objects": GIT_OBJECTS,
        "source_bindings": {path: digest for path, digest in INPUT_BINDINGS},
        "prior_dimension_counts": PRIOR_COUNTS,
        "transaction_criteria": criteria,
        "dimensions": dimensions,
        "dimension_counts": ordered_counts,
        "blocking_gaps": [],
        "operational_evidence_gaps": gaps,
        "verdict": VERDICT,
        "hostile_mutations_rejected": rejected,
        "api_spine_boundary": {
            "classification": "read_only_security_audit_idempotency_evidence_review",
            "graphql_remains_read_only": True,
            "rest_command_pattern_unchanged": True,
            "practice_scope_confirmation_idempotency_audit_retained": True,
            "authoritative_readback_decides_unknown_response": True,
            "api_or_product_artifact_changed": False,
            "unchanged_path_count": len(UNCHANGED_PRODUCT_PATHS),
        },
        "closed_boundaries": {
            "app_imported": False,
            "route_called": False,
            "database_opened": False,
            "docker_used": False,
            "sql_executed": False,
            "browser_opened": False,
            "provider_called": False,
            "worker_or_model_used": False,
            "network_opened": False,
            "product_or_configuration_changed": False,
            "ordinary_practice_enabled": False,
            "ordinary_admission_released": False,
            "environment_or_secret_posture_claimed": False,
        },
    }


def render_report(evidence: dict[str, Any]) -> str:
    counts = evidence["dimension_counts"]
    lines = [
        "# Post-attempt-008 canonical check-in admission-readiness convergence report",
        "",
        "Date: 2026-08-23",
        "",
        f"Timestamp: {TIMESTAMP} (Australia/Brisbane)",
        "",
        "Status: `frozen_evidence`",
        "",
        f"Result: `{evidence['result']}`",
        "",
        f"Verdict: `{evidence['verdict']}`",
        "",
        "## Outcome",
        "",
        "The accepted attempt-008 terminal closes exactly the atomic rollback and unknown-response recovery evidence gap. The matrix advances from 10/0/2 to 11/0/1. The environment-manifest and operational-secret-posture gap remains open, so ordinary-practice admission remains not ready and unauthorised.",
        "",
        "This is one read-only evidence-clock reading. It changes no product, route, API, client, configuration, database or runtime surface.",
        "",
        "## Dimension matrix",
        "",
        "| Order | Dimension | Classification | Basis |",
        "|---:|---|---|---|",
    ]
    for item in evidence["dimensions"]:
        lines.append(f"| {item['order']} | `{item['id']}` | `{item['classification']}` | `{item['basis']}` |")
    lines.extend(
        [
            "",
            "## Counts and remaining gap",
            "",
            f"Satisfied: {counts['satisfied']}; blocking gaps: {counts['blocking_gap']}; operational-evidence gaps: {counts['operational_evidence_gap']}.",
            "",
            "The sole remaining gap is `environment_manifest_and_operational_secret_posture`. Attempt 008 supplies no canonical environment instance, operational secret-reference custody, rotation evidence or live role binding.",
            "",
            "## Why dimension 7 now passes",
            "",
            "Attempt 008 executed once with zero retry, resume or fallback. It proved explicit rollback with zero persisted packet members, an incomplete caller response with no success or retry, fresh restricted-role readback of one exact effect/receipt/audit packet, zero duplicate or cross-practice visibility, forced RLS under a non-bypass role and complete cleanup with zero owned residue.",
            "",
            "## API Spine and closed authority",
            "",
            "The existing explicit REST command remains practice-scoped, confirmed, idempotent and auditable; authoritative readback resolves the unknown response. GraphQL remains read-only. No API or product artifact changed.",
            "",
            f"All eleven input hashes and five full Git bindings passed. Rejected {evidence['hostile_mutations_rejected']} hostile contract mutations with zero escape.",
            "",
            "No `app` module was imported; no route, database, Docker, SQL, browser, provider, model, Harness or network surface was opened. Ordinary practice remains default-off and denied.",
            "",
        ]
    )
    return "\n".join(lines)


def run_review(root: Path | None = None, *, release: bool = True) -> dict[str, Any]:
    root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    contract = load_json(root, CONTRACT_PATH)
    validate_contract(contract, root)
    require(product_paths_are_unchanged(root), "API or product path changed after prior review")
    texts = {path: canonical_text(root, path) for path, _ in INPUT_BINDINGS}
    prior_contract = json.loads(texts[PRIOR_CONTRACT])
    prior_evidence = json.loads(texts[PRIOR_EVIDENCE])
    prior_dimensions = validate_prior_packet(prior_contract, prior_evidence, texts)
    criteria = validate_attempt_packet(
        json.loads(texts[ATTEMPT_EVIDENCE]),
        json.loads(texts[ATTEMPT_ATTESTATION]),
        json.loads(texts[ATTEMPT_ENVELOPE]),
        texts,
    )
    dimensions = derive_dimensions(prior_dimensions)
    rejected = hostile_mutations(contract, root)
    evidence = build_evidence(contract, dimensions, criteria, rejected)
    if release:
        (root / EVIDENCE_PATH).write_text(
            json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        (root / REPORT_PATH).write_text(render_report(evidence), encoding="utf-8", newline="\n")
    return evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)
    try:
        run_review(args.repo_root, release=not args.no_write)
    except (ContractError, EvidenceError, OSError, json.JSONDecodeError) as exc:
        print(f"FAIL_CLOSED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
