"""Deterministic canonical check-in admission-readiness convergence review.

The reviewer joins the accepted original twelve-dimension result to exact
accepted descendants.  It reads repository files and local Git objects only.
It imports no application module and opens no runtime or provider surface.
"""

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
    "raisa.canonical_check_in_admission_readiness_convergence_review_contract.v1"
)
EVIDENCE_SCHEMA_VERSION = (
    "raisa.canonical_check_in_admission_readiness_convergence_review_evidence.v1"
)
PLANNING_SOURCE = "f4623fed8d12011a9a34747d12696e5e6017f18b"
HASH_MODE = "strict_utf8_canonical_lf_reject_bare_cr_sha256"
CLASSIFICATIONS = ("satisfied", "blocking_gap", "operational_evidence_gap")
VERDICT = "not_ready_for_ordinary_practice_admission"
RESULT = (
    "raisa_provider_free_read_only_canonical_check_in_ordinary_practice_"
    "admission_readiness_convergence_review_pass"
)

BASE = (
    "orchestration/continuity/raisa-provider-free-read-only-canonical-check-in-"
    "ordinary-practice-admission-readiness-convergence-review"
)
CONTRACT_PATH = f"{BASE}/contract.json"
EVIDENCE_PATH = f"{BASE}/evidence.json"
REPORT_PATH = f"{BASE}/report.md"

ORIGINAL = (
    "orchestration/continuity/raisa-provider-free-read-only-ordinary-practice-"
    "canonical-check-in-admission-readiness-review/provider-free-read-only-evidence.json"
)
KERNEL = (
    "orchestration/continuity/raisa-provider-free-unmounted-default-off-ordinary-"
    "practice-canonical-check-in-admission-control-kernel-rehearsal/"
    "provider-free-kernel-rehearsal-evidence.json"
)
RUNBOOK = "docs/api-spine/manifests/canonical-check-in-rollout-kill-switch-rollback-runbook.json"
OBSERVABILITY = "docs/api-spine/manifests/canonical-check-in-non-phi-observability.json"
TENANT_BASE = (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-"
    "check-in-runtime-role-tenant-isolation-attestation-rehearsal"
)
TENANT_ATTESTATION = f"{TENANT_BASE}/tenant-role-attestation.json"
TENANT_EVIDENCE = f"{TENANT_BASE}/rehearsal-evidence.json"
ATTEMPT_BASE = "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-005"
ATTEMPT_FAILURE = f"{ATTEMPT_BASE}/rehearsal-failure-evidence.json"
ATTEMPT_ENVELOPE = f"{ATTEMPT_BASE}/attempt-005-execution-envelope.json"
REPAIR = (
    "orchestration/continuity/raisa-provider-free-check-in-server-attachment-"
    "lifetime-and-post-readiness-observability-conformance-repair/repair-evidence.json"
)
ENVIRONMENT = (
    "orchestration/continuity/raisa-provider-free-default-off-check-in-environment-"
    "manifest-secret-posture-architecture/provider-free-architecture-evidence.json"
)

ORIGINAL_CLOSEOUT = (
    "docs/raisa-provider-free-read-only-ordinary-practice-canonical-check-in-"
    "admission-readiness-review-closeout.md"
)
KERNEL_CLOSEOUT = (
    "docs/raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-"
    "check-in-admission-control-kernel-rehearsal-closeout.md"
)
RUNBOOK_CLOSEOUT = (
    "docs/raisa-provider-free-default-off-canonical-check-in-rollout-kill-switch-"
    "rollback-runbook-convergence-rehearsal-closeout.md"
)
OBSERVABILITY_CLOSEOUT = (
    "docs/raisa-provider-free-default-off-canonical-check-in-non-phi-observability-"
    "manifest-convergence-rehearsal-closeout.md"
)
OBSERVER_CLOSEOUT = (
    "docs/raisa-provider-free-unmounted-default-off-canonical-check-in-non-phi-"
    "observer-adapter-rehearsal-closeout.md"
)
TENANT_CLOSEOUT = (
    "docs/raisa-provider-free-disposable-postgresql-default-off-check-in-runtime-"
    "role-tenant-isolation-attestation-rehearsal-closeout.md"
)
ATTEMPT_CLOSEOUT = "docs/raisa-provider-free-check-in-relay-free-recovery-attempt-005-blocked-closeout.md"
REPAIR_CLOSEOUT = (
    "docs/raisa-provider-free-check-in-server-attachment-lifetime-and-post-readiness-"
    "observability-conformance-repair-closeout.md"
)
ENVIRONMENT_CLOSEOUT = (
    "docs/raisa-provider-free-default-off-check-in-environment-manifest-secret-"
    "posture-architecture-closeout.md"
)

GIT_OBJECTS = {
    "original_readiness_review": "27101faa86b5aa3850e90bc4ded8600e5f8d7dc9",
    "admission_control_architecture": "752b521c59f5b44bf46de0cf776a33ac74b8134d",
    "admission_control_kernel": "4204ec6348abb0f92b1a30314699d4a469fa860a",
    "rollout_runbook": "149e377344fab671927682e428af7825e9a0e143",
    "observability_manifest": "7acd4e9c39ce534042178f9b8b7e049161ce8b03",
    "observer_adapter": "1fb1db90e1fdbf73d4dcbaf7d51793f4320ba8b5",
    "tenant_role_attestation": "6a2832575e9b4df5c40a13984db7281e79814a94",
    "unknown_commit_attempt_node": "03b94136c9c6cd82d5a8098705f263ba34a20de4",
    "unknown_commit_occupied_execution": "905184b76f576006232fcfdc78da71d98fcf0ca0",
    "server_lifecycle_repair": "290923ef7b068b4b61f1bf41fff84fe4f47e3049",
    "environment_secret_architecture": "a1f309a6d52d01f9866432f7e9abb8095788d023",
}

DIMENSIONS = (
    (
        1,
        "current_default_off_and_empty_ordinary_posture",
        "satisfied",
        "original_accepted",
    ),
    (
        2,
        "ordinary_practice_admission_control",
        "satisfied",
        "accepted_admission_kernel",
    ),
    (3, "api_spine_contract_and_route_identity", "satisfied", "original_accepted"),
    (
        4,
        "authentication_and_dual_receptionist_authorization",
        "satisfied",
        "original_accepted",
    ),
    (
        5,
        "tenant_isolation_and_runtime_database_role",
        "satisfied",
        "accepted_disposable_postgresql_attestation",
    ),
    (6, "idempotency_evidence_and_replay", "satisfied", "original_accepted"),
    (
        7,
        "atomic_effect_rollback_and_unknown_commit_recovery",
        "operational_evidence_gap",
        "attempt_005_failed_before_transaction_evidence",
    ),
    (8, "append_only_audit_and_committed_event", "satisfied", "original_accepted"),
    (
        9,
        "ordinary_rollout_kill_switch_and_rollback_runbook",
        "satisfied",
        "accepted_default_off_runbook",
    ),
    (
        10,
        "non_phi_observability_and_alerting",
        "satisfied",
        "accepted_non_phi_manifest_and_unmounted_adapter",
    ),
    (
        11,
        "environment_manifest_and_operational_secret_posture",
        "operational_evidence_gap",
        "architecture_has_zero_operational_instances",
    ),
    (
        12,
        "client_cutover_and_waiting_area_separation",
        "satisfied",
        "original_accepted",
    ),
)

EXPECTED_COUNTS = {
    "satisfied": 10,
    "blocking_gap": 0,
    "operational_evidence_gap": 2,
}
REQUIRED_OPEN_GAPS = (
    "atomic_effect_rollback_and_unknown_commit_recovery",
    "environment_manifest_and_operational_secret_posture",
)
CLOSED_BOUNDARIES = (
    "no_app_import_or_product_runtime",
    "no_route_database_docker_sql_browser_provider_model_harness_or_network",
    "no_ordinary_practice_enablement_or_admission_release",
    "no_product_configuration_api_client_or_waiting_area_change",
    "no_product_patient_clinical_historical_or_protected_data",
    "no_deployment_release_pages_or_protected_ref_movement",
    "preserve_docs_branding_and_all_unrelated_untracked_files",
)


class ContractError(RuntimeError):
    """Frozen contract or exact source binding changed."""


class EvidenceError(RuntimeError):
    """Exact artifacts cannot prove the frozen current classification."""


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
    if "\r" in text.replace("\r\n", ""):
        raise ContractError(f"bare CR source: {relative}")
    return text.replace("\r\n", "\n")


def canonical_sha256(root: Path, relative: str) -> str:
    return hashlib.sha256(canonical_text(root, relative).encode("utf-8")).hexdigest()


def load_json(root: Path, relative: str) -> dict[str, Any]:
    value = json.loads(canonical_text(root, relative))
    if not isinstance(value, dict):
        raise ContractError(f"JSON object required: {relative}")
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


def validate_contract(
    contract: dict[str, Any], root: Path, *, check_git: bool = True
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
            "acceptance",
            "closed_boundaries",
        },
        "top-level keys changed",
    )
    require(contract["schema_version"] == SCHEMA_VERSION, "schema version changed")
    require(contract["planning_source"] == PLANNING_SOURCE, "planning source changed")
    require(contract["input_hash_mode"] == HASH_MODE, "hash mode changed")
    require(
        tuple(contract["classifications"]) == CLASSIFICATIONS, "classifications changed"
    )
    require(
        contract["accepted_git_objects"] == GIT_OBJECTS, "accepted Git objects changed"
    )
    for label, object_id in {
        "planning_source": contract["planning_source"],
        **contract["accepted_git_objects"],
    }.items():
        require(
            re.fullmatch(r"[0-9a-f]{40}", object_id) is not None,
            f"invalid full Git ID: {label}",
        )
        if check_git:
            require(
                git_object_is_ancestor(root, object_id),
                f"Git object is not an ancestor: {label}",
            )

    inputs = contract["inputs"]
    require(isinstance(inputs, list) and len(inputs) == 20, "input count changed")
    expected_paths = (
        ORIGINAL,
        ORIGINAL_CLOSEOUT,
        "orchestration/agent_inbox/codex/raisa-ordinary-practice-check-in-admission-readiness-review-sol-acceptance.md",
        KERNEL,
        KERNEL_CLOSEOUT,
        RUNBOOK,
        RUNBOOK_CLOSEOUT,
        OBSERVABILITY,
        OBSERVABILITY_CLOSEOUT,
        OBSERVER_CLOSEOUT,
        TENANT_ATTESTATION,
        TENANT_EVIDENCE,
        TENANT_CLOSEOUT,
        ATTEMPT_FAILURE,
        ATTEMPT_ENVELOPE,
        ATTEMPT_CLOSEOUT,
        REPAIR,
        REPAIR_CLOSEOUT,
        ENVIRONMENT,
        ENVIRONMENT_CLOSEOUT,
    )
    require(
        tuple(item.get("path") for item in inputs) == expected_paths,
        "input path order changed",
    )
    for item in inputs:
        require(set(item) == {"path", "sha256"}, "input shape changed")
        require(
            re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is not None, "invalid SHA-256"
        )
        require(
            canonical_sha256(root, item["path"]) == item["sha256"],
            f"source hash changed: {item['path']}",
        )

    observed_dimensions = tuple(
        (
            item.get("order"),
            item.get("id"),
            item.get("expected_classification"),
            item.get("basis"),
        )
        for item in contract["dimensions"]
    )
    require(
        observed_dimensions == DIMENSIONS,
        "dimension order, vocabulary or basis changed",
    )
    acceptance = contract["acceptance"]
    require(
        acceptance
        == {
            "expected_counts": EXPECTED_COUNTS,
            "expected_verdict": VERDICT,
            "minimum_hostile_mutations": 120,
            "required_open_gaps": list(REQUIRED_OPEN_GAPS),
        },
        "acceptance changed",
    )
    require(
        tuple(contract["closed_boundaries"]) == CLOSED_BOUNDARIES,
        "closed boundaries changed",
    )


def validate_original(
    original: dict[str, Any], texts: dict[str, str]
) -> dict[int, dict[str, Any]]:
    require(
        original.get("result")
        == "raisa_provider_free_read_only_ordinary_practice_canonical_check_in_admission_readiness_review_pass",
        "original result changed",
    )
    require(original.get("verdict") == VERDICT, "original verdict changed")
    require(
        original.get("dimension_counts")
        == {"blocking_gap": 3, "operational_evidence_gap": 3, "satisfied": 6},
        "original counts changed",
    )
    dimensions = original.get("dimensions")
    require(
        isinstance(dimensions, list) and len(dimensions) == 12,
        "original dimensions changed",
    )
    indexed = {item.get("order"): item for item in dimensions}
    require(tuple(indexed) == tuple(range(1, 13)), "original dimension order changed")
    require(
        GIT_OBJECTS["original_readiness_review"] in texts[ORIGINAL_CLOSEOUT],
        "original accepted source missing from closeout",
    )
    return indexed


def validate_descendants(
    data: dict[str, dict[str, Any]], texts: dict[str, str]
) -> None:
    kernel = data[KERNEL]
    require(kernel.get("status") == "passed", "kernel did not pass")
    require(
        kernel.get("canonical_active_ordinary_record_count") == 0,
        "ordinary record active",
    )
    require(
        kernel.get("ordinary_admission_release_count") == 0,
        "ordinary admission released",
    )
    require(
        kernel.get("product_or_configuration_changed") is False,
        "kernel changed product",
    )
    evaluator = kernel.get("evaluator", {}).get("results", [])
    ordinary = [item for item in evaluator if item.get("lane") == "ordinary_practice"]
    require(
        ordinary and all(item.get("decision") == "denied" for item in ordinary),
        "ordinary kernel path admitted",
    )
    require(
        GIT_OBJECTS["admission_control_kernel"] in texts[KERNEL_CLOSEOUT],
        "kernel source missing",
    )

    runbook = data[RUNBOOK]
    default = runbook.get("default_posture", {})
    require(
        default.get("ordinary_practice_enabled") is False,
        "runbook enables ordinary practice",
    )
    require(
        default.get("active_ordinary_practice_records") == 0,
        "runbook has active records",
    )
    require(
        runbook.get("runbook", {}).get("status") == "prepared_not_authorized",
        "runbook authorised",
    )
    require(
        runbook.get("runbook", {}).get("kill_switch", {}).get("default_state")
        == "engaged",
        "kill switch not engaged",
    )
    require(
        runbook.get("runbook", {}).get("rollback", {}).get("unknown_commit_policy")
        == "deny_success_no_blind_retry",
        "unknown policy changed",
    )
    require(
        GIT_OBJECTS["rollout_runbook"] in texts[RUNBOOK_CLOSEOUT],
        "runbook source missing",
    )

    observability = data[OBSERVABILITY]
    posture = observability.get("default_posture", {})
    require(
        all(value is False for value in posture.values()),
        "observability default posture opened",
    )
    body = observability.get("observability", {})
    require(len(body.get("metric_families", [])) == 5, "metric family count changed")
    require(len(body.get("alerts", [])) == 6, "alert count changed")
    require(
        all(item.get("contains_identifier") is False for item in body["alerts"]),
        "identifying alert",
    )
    require(
        all(item.get("automatic_control_action") is False for item in body["alerts"]),
        "actuating alert",
    )
    require(
        GIT_OBJECTS["observability_manifest"] in texts[OBSERVABILITY_CLOSEOUT],
        "observability source missing",
    )
    require(
        GIT_OBJECTS["observer_adapter"] in texts[OBSERVER_CLOSEOUT],
        "observer source missing",
    )

    attestation = data[TENANT_ATTESTATION]
    role = attestation.get("role_catalogue", {})
    for key in (
        "superuser",
        "create_database",
        "create_role",
        "inherit",
        "replication",
        "bypass_rls",
    ):
        require(role.get(key) is False, f"tenant role privilege changed: {key}")
    for key in (
        "memberships",
        "owned_databases",
        "owned_functions",
        "owned_relations",
        "owned_schemas",
        "product_relation_privileges",
    ):
        require(role.get(key) == 0, f"tenant role ownership changed: {key}")
    require(
        attestation.get("ordinary_admission_release_count") == 0,
        "tenant rehearsal released admission",
    )
    tenant = data[TENANT_EVIDENCE]
    require(
        tenant.get("cleanup", {}).get("status") == "cleanup_verified",
        "tenant cleanup failed",
    )
    require(
        tenant.get("closed_boundaries", {}).get("product_relation_used") is False,
        "product relation used",
    )
    require(
        tenant.get("closed_boundaries", {}).get("ordinary_admission_released") is False,
        "ordinary admission released",
    )
    require(
        GIT_OBJECTS["tenant_role_attestation"] in texts[TENANT_CLOSEOUT],
        "tenant source missing",
    )

    failure = data[ATTEMPT_FAILURE]
    require(failure.get("result") == "failed_closed", "attempt 005 terminal changed")
    require(failure.get("stage") == "environment", "attempt 005 stage changed")
    require(
        failure.get("code") == "server_not_running_after_readiness",
        "attempt 005 code changed",
    )
    require(failure.get("retry_count") == 0, "attempt 005 retried")
    require(failure.get("success_released") is False, "attempt 005 released success")
    require(
        "setup_and_catalogue" not in failure.get("lifecycle", []),
        "attempt reached transaction setup",
    )
    envelope = data[ATTEMPT_ENVELOPE]
    require(
        envelope.get("source_head") == GIT_OBJECTS["unknown_commit_occupied_execution"],
        "occupied source changed",
    )
    require(
        envelope.get("transaction_attestation_sha256") is None,
        "transaction attestation unexpectedly present",
    )
    require(envelope.get("automatic_retry_count") == 0, "occupied attempt retried")
    require(
        GIT_OBJECTS["unknown_commit_occupied_execution"] in texts[ATTEMPT_CLOSEOUT],
        "occupied source missing",
    )

    repair = data[REPAIR]
    require(repair.get("status") == "accepted", "server lifecycle repair not accepted")
    verification = repair.get("deterministic_verification", {})
    require(verification.get("docker_invocations") == 0, "repair used Docker")
    require(verification.get("database_invocations") == 0, "repair used database")
    require(
        repair.get("implementation", {}).get("api_or_product_change") is False,
        "repair changed product",
    )

    environment = data[ENVIRONMENT]
    require(
        environment.get("status") == "passed", "environment architecture did not pass"
    )
    for key in (
        "canonical_manifest_instance_count",
        "current_rotation_evidence_count",
        "current_secret_reference_count",
    ):
        require(
            environment.get(key) == 0,
            f"operational environment evidence unexpectedly present: {key}",
        )
    require(
        environment.get("database_or_role_used") is False,
        "environment architecture used role",
    )
    require(
        environment.get("provider_or_network_used") is False,
        "environment architecture used provider",
    )
    require(
        GIT_OBJECTS["environment_secret_architecture"] in texts[ENVIRONMENT_CLOSEOUT],
        "environment source missing",
    )


def derive_dimensions(original: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    updates: dict[int, tuple[list[str], list[str]]] = {
        2: (
            [KERNEL, KERNEL_CLOSEOUT],
            [
                "zero_active_ordinary_records",
                "every_ordinary_scenario_denied",
                "kernel_unmounted_and_product_unchanged",
            ],
        ),
        5: (
            [TENANT_ATTESTATION, TENANT_EVIDENCE, TENANT_CLOSEOUT],
            [
                "restricted_runtime_role_attested",
                "forced_rls_cross_tenant_denials_observed",
                "disposable_cleanup_verified",
            ],
        ),
        7: (
            [
                ATTEMPT_FAILURE,
                ATTEMPT_ENVELOPE,
                ATTEMPT_CLOSEOUT,
                REPAIR,
                REPAIR_CLOSEOUT,
            ],
            [
                "attempt_005_failed_before_transaction_setup",
                "transaction_attestation_absent",
                "lifecycle_repair_static_without_database_execution",
            ],
        ),
        9: (
            [RUNBOOK, RUNBOOK_CLOSEOUT],
            [
                "kill_switch_defaults_engaged",
                "rollback_order_and_triggers_frozen",
                "prepared_not_authorized",
            ],
        ),
        10: (
            [OBSERVABILITY, OBSERVABILITY_CLOSEOUT, OBSERVER_CLOSEOUT],
            [
                "five_metric_families_defined",
                "six_non_identifying_non_actuating_alerts_defined",
                "instrumentation_and_transport_disabled",
            ],
        ),
        11: (
            [ENVIRONMENT, ENVIRONMENT_CLOSEOUT],
            [
                "canonical_manifest_instance_count_zero",
                "secret_and_rotation_evidence_counts_zero",
                "architecture_only_no_role_or_provider_use",
            ],
        ),
    }
    results: list[dict[str, Any]] = []
    for order, dimension_id, classification, basis in DIMENSIONS:
        original_item = original[order]
        require(
            original_item.get("id") == dimension_id,
            f"original dimension ID changed: {order}",
        )
        if order not in updates:
            require(
                original_item.get("classification") == "satisfied",
                f"original satisfied dimension regressed: {dimension_id}",
            )
            citations = original_item.get("citations", [])
            markers = ["original_exact_accepted_classification_retained"]
        else:
            citations, markers = updates[order]
        results.append(
            {
                "order": order,
                "id": dimension_id,
                "classification": classification,
                "basis": basis,
                "citations": citations,
                "markers": markers,
            }
        )
    return results


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
        candidate["inputs"][index]["sha256"] = (
            "0" if digest[0] != "0" else "1"
        ) + digest[1:]
        mutations.append(candidate)
    for label, object_id in contract["accepted_git_objects"].items():
        candidate = copy.deepcopy(contract)
        candidate["accepted_git_objects"][label] = object_id[:7]
        mutations.append(candidate)
        candidate = copy.deepcopy(contract)
        candidate["accepted_git_objects"][label] = "0" * 40
        mutations.append(candidate)
    for index, dimension in enumerate(contract["dimensions"]):
        candidate = copy.deepcopy(contract)
        candidate["dimensions"][index]["id"] += "_drift"
        mutations.append(candidate)
        candidate = copy.deepcopy(contract)
        candidate["dimensions"][index]["basis"] += "_drift"
        mutations.append(candidate)
        alternatives = [
            value
            for value in CLASSIFICATIONS
            if value != dimension["expected_classification"]
        ]
        candidate = copy.deepcopy(contract)
        candidate["dimensions"][index]["expected_classification"] = alternatives[0]
        mutations.append(candidate)
    for key, value in (
        ("schema_version", "mutated"),
        ("planning_source", PLANNING_SOURCE[:7]),
        ("input_hash_mode", "mutated"),
        ("classifications", ["satisfied"]),
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
            validate_contract(candidate, root, check_git=False)
        except (ContractError, OSError, KeyError, TypeError):
            rejected += 1
        else:
            raise EvidenceError("hostile contract mutation escaped")
    return rejected


def build_evidence(
    contract: dict[str, Any], dimensions: list[dict[str, Any]], rejected: int
) -> dict[str, Any]:
    counts = Counter(item["classification"] for item in dimensions)
    ordered_counts = {name: counts.get(name, 0) for name in CLASSIFICATIONS}
    require(ordered_counts == EXPECTED_COUNTS, f"unexpected counts: {ordered_counts}")
    open_gaps = [
        item["id"]
        for item in dimensions
        if item["classification"] == "operational_evidence_gap"
    ]
    require(tuple(open_gaps) == REQUIRED_OPEN_GAPS, "open gaps changed")
    require(
        rejected >= contract["acceptance"]["minimum_hostile_mutations"],
        "too few hostile mutations",
    )
    return {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "result": RESULT,
        "planning_source": PLANNING_SOURCE,
        "accepted_git_objects": GIT_OBJECTS,
        "source_bindings": {
            item["path"]: item["sha256"] for item in contract["inputs"]
        },
        "dimensions": dimensions,
        "dimension_counts": ordered_counts,
        "blocking_gaps": [],
        "operational_evidence_gaps": open_gaps,
        "verdict": VERDICT,
        "hostile_mutations_rejected": rejected,
        "closed_boundaries": {
            "app_imported": False,
            "route_called": False,
            "database_opened": False,
            "docker_used": False,
            "sql_executed": False,
            "browser_opened": False,
            "provider_called": False,
            "model_or_harness_used": False,
            "network_opened": False,
            "product_or_configuration_changed": False,
            "ordinary_practice_enabled": False,
            "ordinary_admission_released": False,
        },
    }


def render_report(evidence: dict[str, Any]) -> str:
    counts = evidence["dimension_counts"]
    lines = [
        "# Canonical check-in ordinary-practice admission-readiness convergence report",
        "",
        "Date: 2026-08-23",
        "",
        "Timestamp: 2026-08-23T01:10:00.0000000+10:00 (Australia/Brisbane)",
        "",
        "Status: frozen evidence",
        "",
        f"Result: `{evidence['result']}`",
        "",
        f"Verdict: `{evidence['verdict']}`",
        "",
        "## Outcome",
        "",
        "The review records measurable convergence: four of the original six gaps are now satisfied by exact accepted descendants. No design-level blocking gap remains. Unknown-commit recovery and environment/secret posture remain operational-evidence gaps, so ordinary-practice admission remains not ready and unauthorised.",
        "",
        "The result adds no control layer and changes no product or runtime source. It is a reading of the accepted evidence clock, not an enablement act.",
        "",
        "## Dimension matrix",
        "",
        "| Order | Dimension | Classification | Basis |",
        "|---:|---|---|---|",
    ]
    for item in evidence["dimensions"]:
        lines.append(
            f"| {item['order']} | `{item['id']}` | `{item['classification']}` | `{item['basis']}` |"
        )
    lines.extend(
        [
            "",
            "## Counts",
            "",
            f"Satisfied: {counts['satisfied']}; blocking gaps: {counts['blocking_gap']}; operational-evidence gaps: {counts['operational_evidence_gap']}.",
            "",
            "Remaining operational-evidence gaps:",
            "",
        ]
    )
    lines.extend(f"- `{value}`" for value in evidence["operational_evidence_gaps"])
    lines.extend(
        [
            "",
            "## Exact source boundary",
            "",
            "All accepted Git objects are full 40-character IDs and ancestors of reviewed HEAD. All twenty input files matched strict UTF-8 canonical-LF SHA-256 bindings.",
            "",
            "| Accepted object | Full Git ID |",
            "|---|---|",
        ]
    )
    for label, object_id in evidence["accepted_git_objects"].items():
        lines.append(f"| `{label}` | `{object_id}` |")
    lines.extend(
        [
            "",
            "## Why two gaps remain",
            "",
            "Attempt 005 failed closed at `environment/server_not_running_after_readiness` before transaction setup, ambiguous response, authoritative readback or transaction attestation. The accepted server-lifecycle repair is static and records zero Docker/database executions; it does not retrospectively prove recovery.",
            "",
            "The environment/secret architecture records zero canonical environment manifests, secret references and rotation evidence. Its future typed slots are not operational posture.",
            "",
            "## Deterministic rejection",
            "",
            f"Rejected {evidence['hostile_mutations_rejected']} hostile contract mutations with zero escape.",
            "",
            "No `app` module was imported; no route, database, Docker, SQL, browser, provider, model, Harness or network surface was opened. No practice was enabled and no product/configuration source changed.",
            "",
        ]
    )
    return "\n".join(lines)


def run_review(root: Path | None = None, *, release: bool = True) -> dict[str, Any]:
    root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    contract = load_json(root, CONTRACT_PATH)
    validate_contract(contract, root)
    texts = {
        item["path"]: canonical_text(root, item["path"]) for item in contract["inputs"]
    }
    data = {
        path: json.loads(texts[path])
        for path in (
            ORIGINAL,
            KERNEL,
            RUNBOOK,
            OBSERVABILITY,
            TENANT_ATTESTATION,
            TENANT_EVIDENCE,
            ATTEMPT_FAILURE,
            ATTEMPT_ENVELOPE,
            REPAIR,
            ENVIRONMENT,
        )
    }
    original = validate_original(data[ORIGINAL], texts)
    validate_descendants(data, texts)
    dimensions = derive_dimensions(original)
    rejected = hostile_mutations(contract, root)
    evidence = build_evidence(contract, dimensions, rejected)
    if release:
        (root / EVIDENCE_PATH).write_text(
            json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        (root / REPORT_PATH).write_text(
            render_report(evidence), encoding="utf-8", newline="\n"
        )
    return evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root", type=Path, default=Path(__file__).resolve().parents[1]
    )
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
