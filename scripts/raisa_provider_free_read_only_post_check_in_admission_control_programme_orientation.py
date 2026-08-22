"""Build deterministic evidence for the post-check-in programme orientation."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from orchestration_harness import check_in_rollout_runbook as runbook


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
OPENAPI = ROOT / "docs/api-spine/openapi/appointment-commands.yaml"
ARCHITECTURE_CONTRACT = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-default-off-ordinary-practice-canonical-check-in-"
    "admission-control-architecture/contract.json"
)
TARGET_MANIFEST = ROOT / runbook.TARGET_RELATIVE_PATH

OPERATION_ID = (
    "raisa-provider-free-read-only-post-check-in-admission-control-programme-"
    "orientation"
)
SUCCESSOR_ID = (
    "raisa-provider-free-default-off-canonical-check-in-rollout-kill-switch-"
    "rollback-runbook-convergence-rehearsal"
)
FULL_GIT_OBJECT = re.compile(r"^[0-9a-f]{40}$")

REQUIRED_NODES = {
    "route": "raisa-provider-free-default-off-canonical-check-in-route-adapter-convergence-rehearsal",
    "readiness": "raisa-provider-free-read-only-ordinary-practice-canonical-check-in-admission-readiness-review",
    "admission_architecture": "raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture",
    "admission_kernel": "raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-check-in-admission-control-kernel-rehearsal",
    "environment_architecture": "raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture",
    "tenant_role": "raisa-provider-free-disposable-postgresql-default-off-check-in-runtime-role-tenant-isolation-attestation-rehearsal",
    "relay_transport": "raisa-provider-free-default-off-check-in-relay-free-unknown-response-transport-redesign",
    "database_attempt": "raisa-provider-free-check-in-relay-free-recovery-attempt-005",
    "harness_terminal": "raisa-authored-synthetic-native-harness-corrected-guard-graph-first-useful-development-recovery-rehearsal",
}

CLASSIFICATIONS = [
    {
        "dimension": "route_and_api_command_identity",
        "classification": "satisfied_accepted",
        "reason": "accepted_default_off_route_delegates_to_the_canonical_adapter",
    },
    {
        "dimension": "ordinary_admission_control",
        "classification": "satisfied_contract_only",
        "reason": "accepted_architecture_and_unmounted_kernel_have_zero_active_records",
    },
    {
        "dimension": "ordinary_rollout_kill_switch_and_rollback_runbook",
        "classification": "satisfied_contract_only",
        "reason": "closed_form_validator_exists_but_canonical_api_spine_manifest_is_absent",
    },
    {
        "dimension": "non_phi_observability_and_alerting",
        "classification": "satisfied_contract_only",
        "reason": "five_metric_families_and_six_non_actuating_alerts_are_frozen_but_unmounted",
    },
    {
        "dimension": "environment_manifest_and_operational_secret_posture",
        "classification": "operational_evidence_gap",
        "reason": "architecture_exists_with_zero_manifests_secret_references_or_operational_artifacts",
    },
    {
        "dimension": "tenant_isolation_and_runtime_database_role",
        "classification": "satisfied_accepted",
        "reason": "disposable_postgresql_non_owner_nobypassrls_and_cross_tenant_denial_passed",
    },
    {
        "dimension": "atomic_rollback_and_unknown_commit_recovery",
        "classification": "operational_evidence_gap",
        "reason": "rollback_passed_but_unknown_response_readback_never_reached_acceptance",
    },
    {
        "dimension": "native_harness_worker_allocation",
        "classification": "closed_later_gate",
        "reason": "final_one_request_terminal_produced_no_candidate_and_allocation_is_unavailable",
    },
    {
        "dimension": "ordinary_practice_activation",
        "classification": "closed_later_gate",
        "reason": "activation_authority_false_and_zero_active_ordinary_records",
    },
    {
        "dimension": "atomic_two_client_cutover_and_waiting_area_separation",
        "classification": "closed_later_gate",
        "reason": "client_cutover_is_distinct_and_waiting_area_movement_remains_separate",
    },
]


class OrientationError(ValueError):
    """The repository no longer matches the frozen read-only orientation."""


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise OrientationError(f"json_root_invalid:{path.as_posix()}")
    return value


def build_evidence(root: Path = ROOT) -> dict[str, Any]:
    graph = _read_json(root / GRAPH.relative_to(ROOT))
    nodes = {node["id"]: node for node in graph.get("nodes", [])}
    if len(nodes) != len(graph.get("nodes", [])):
        raise OrientationError("graph_node_id_duplicate")

    node_evidence: dict[str, dict[str, str]] = {}
    for role, node_id in REQUIRED_NODES.items():
        node = nodes.get(node_id)
        if node is None or node.get("status") != "accepted":
            raise OrientationError(f"required_accepted_node_missing:{role}")
        source_head = node.get("coordinates", {}).get("source_head")
        if not isinstance(source_head, str) or not FULL_GIT_OBJECT.fullmatch(
            source_head
        ):
            raise OrientationError(f"required_node_source_invalid:{role}")
        node_evidence[role] = {
            "operation_id": node_id,
            "source_head": source_head,
        }

    if SUCCESSOR_ID in nodes:
        raise OrientationError("selected_successor_already_recorded")

    openapi = (root / OPENAPI.relative_to(ROOT)).read_text(encoding="utf-8")
    for marker in (
        "operationId: proposeAppointmentCheckIn",
        "operationId: confirmAppointmentCheckInProposal",
        "Default-off, authored-synthetic-practice-only",
        "Receptionist-confirmed atomic check-in",
    ):
        if marker not in openapi:
            raise OrientationError(f"openapi_marker_missing:{marker}")

    architecture = _read_json(root / ARCHITECTURE_CONTRACT.relative_to(ROOT))
    posture = architecture.get("current_posture", {})
    observability = architecture.get("observability", {})
    if posture.get("feature_default") is not False:
        raise OrientationError("feature_default_not_false")
    if posture.get("synthetic_allowlist_default") != []:
        raise OrientationError("synthetic_allowlist_default_not_empty")
    if architecture.get("ordinary_state_machine", {}).get(
        "activation_authority_granted"
    ) is not False:
        raise OrientationError("ordinary_activation_authority_not_false")
    if len(observability.get("metric_families", [])) != 5:
        raise OrientationError("metric_family_count_invalid")
    if len(observability.get("alerts", [])) != 6:
        raise OrientationError("alert_count_invalid")
    if any(alert.get("automatic_control_action") is not False for alert in observability["alerts"]):
        raise OrientationError("alert_actuates")

    expected_candidate = runbook.required_candidate_bytes()
    admitted = runbook.validate_candidate_bytes(expected_candidate)
    target = root / runbook.TARGET_RELATIVE_PATH
    if target.exists():
        raise OrientationError("runbook_target_already_present")

    counts = {
        status: sum(
            item["classification"] == status for item in CLASSIFICATIONS
        )
        for status in (
            "satisfied_accepted",
            "satisfied_contract_only",
            "operational_evidence_gap",
            "closed_later_gate",
        )
    }

    return {
        "schema_version": "emr4.post_check_in_programme_orientation.v1",
        "operation_id": OPERATION_ID,
        "result": "pass",
        "required_nodes": node_evidence,
        "api_spine": {
            "boundary": "rest_openapi_command",
            "proposal_operation_id": "proposeAppointmentCheckIn",
            "confirmation_operation_id": "confirmAppointmentCheckInProposal",
            "graphql_mutation_authorized": False,
            "manifest_is_command_authority": False,
        },
        "current_posture": {
            "feature_default": False,
            "synthetic_allowlist_default": [],
            "ordinary_activation_authority": False,
            "active_ordinary_records": 0,
            "native_harness_allocation": "unavailable",
        },
        "classifications": CLASSIFICATIONS,
        "classification_counts": counts,
        "runbook_contract": {
            "schema_version": runbook.SCHEMA_VERSION,
            "target_path": runbook.TARGET_RELATIVE_PATH,
            "target_present": False,
            "closed_form_byte_count": admitted["canonical_byte_count"],
            "closed_form_sha256": admitted["canonical_sha256"],
            "ordinary_practice_enabled": admitted["ordinary_practice_enabled"],
            "activation_authority": admitted["activation_authority"],
            "claim": admitted["claim"],
        },
        "selected_successor": {
            "operation_id": SUCCESSOR_ID,
            "already_recorded": False,
            "owned_product_artifact": runbook.TARGET_RELATIVE_PATH,
            "product_source_change_authorized": False,
            "ordinary_enablement_authorized": False,
            "reason": "exact_default_off_closed_form_exists_and_its_canonical_api_spine_manifest_is_genuinely_absent",
        },
        "claim_boundary": {
            "ordinary_practice_ready": False,
            "unknown_commit_recovery_proved": False,
            "live_secret_custody_proved": False,
            "operational_monitoring_proved": False,
            "client_cutover_authorized": False,
            "product_runtime_changed": False,
            "provider_used": False,
            "protected_ref_moved": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.dumps(build_evidence(), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8", newline="\n")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
