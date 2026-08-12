"""Validate the inert legacy-route convergence and command-kernel contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-legacy-route-convergence-kernel-interface"
)
CONTRACT_PATH = CONTRACT_DIR / "contract.json"
SCHEMA_PATH = CONTRACT_DIR / "contract.schema.json"

EXPECTED_SOURCE_HEAD = "4af9966928b9d453eed372f158e566185aaad5da"
EXPECTED_SOURCES = {
    "docs/raisa-context-fabric-source-owned-truth-conditional-command-reorientation-architecture.md": "71cbddbc880cb906c25d410314e7981311446274f3f1b5355f6759cc1521a0e7",
    "docs/raisa-provider-free-unmounted-conditional-command-admission-rehearsal-design.md": "ed84a15d101b3bc6cb616b6955d4054dc42d8e9827118f319ba9e4d72ebbea53",
    "docs/api-spine/legacy-compatibility-write-deprecation-map.md": "ca7325d4d68dedf5705424dddd4a5ed53cf4395fd2ea4915a0ae633caae64ed7",
    "docs/api-spine/raw-compat-consumer-signal-readiness.md": "ca1dfb4bc69e09424cb8f1717faef9fdc1daa125bef5bc39b01d2c3f0226365e",
    "docs/api-spine/openapi/appointment-commands.yaml": "c3885ccee077df8f316b8ee8167d56a00673473841cbd57401df980d2a61c4b6",
    "orchestration/api_spine_appointment_idempotency_policy_packet.md": "174efcc3dd275275a3c161982ac8ab9d4df245525e850907fefcf846d845c574",
    "orchestration/api_spine_appointment_idempotency_confirmation_family_checkpoint.md": "dc3f3c2f503e34f8862ca6870e37adc427df412018c68b03ecfe134aefe9e5d8",
}
EXPECTED_REQUEST_FIELDS = [
    "schema_version",
    "canonical_operation_id",
    "route_adapter_id",
    "practice_id",
    "actor_id",
    "actor_role",
    "session_id",
    "purpose",
    "target_appointment_id",
    "conflict_domain_id",
    "command_digest",
    "precondition_version",
    "precondition_digest",
    "confirmation_mode",
    "confirmation_reference",
    "idempotency_key_digest",
    "canonicalization_version",
    "correlation_id",
]
EXPECTED_OUTCOMES = [
    "committed",
    "idempotent_replay",
    "stale_precondition",
    "schedule_conflict",
    "authority_revoked",
    "confirmation_required",
    "validation_rejected",
    "idempotency_conflict",
]
EXPECTED_PRECEDENCE = [
    "closed_structure_and_binding_admission",
    "current_authority_before_receipt_disclosure",
    "separate_confirmation_validation",
    "idempotency_replay_or_conflict",
    "source_and_conflict_domain_freshness",
    "current_schedule_and_domain_invariants",
    "atomic_mutation_audit_receipt_and_readback",
]
EXPECTED_LOCK_ORDER = [
    "practice",
    "schedule_domain",
    "appointment",
    "idempotency_record",
]
EXPECTED_AUDIT_FIELDS = [
    "practice_id",
    "actor_id",
    "actor_role_at_decision",
    "canonical_operation_id",
    "route_adapter_id",
    "target_or_conflict_domain_reference",
    "command_digest",
    "idempotency_key_digest",
    "precondition_version_and_digest",
    "confirmation_mode_and_reference",
    "typed_result",
    "correlation_id",
    "decided_at",
    "audit_or_receipt_id",
]
EXPECTED_AUDIT_FORBIDDEN = [
    "raw_request_body",
    "raw_confirmation_token",
    "credential",
    "patient_free_text",
]
EXPECTED_FAMILIES = {
    "appointment_create": {
        "operation": "confirmAppointmentCreateProposal",
        "raw": ("POST", "/api/v1/appointments", "create_appointment", "raw_compat_create"),
        "proposals": {
            (
                "POST",
                "/api/v1/appointments/proposals/create",
                "propose_create_appointment",
                "proposal_command",
            )
        },
        "confirms": {
            (
                "POST",
                "/api/v1/appointments/proposals/create/confirm",
                "confirm_create_proposal_route",
                "confirm_command",
            ),
            (
                "POST",
                "/api/v1/appointments/proposals/create/confirm-bernie",
                "confirm_bernie_create_proposal",
                "confirm_command_variant",
            ),
        },
        "target_shape": "null_appointment_target",
        "locks": ["practice", "schedule_domain", "idempotency_record"],
        "confirmation": "separate_confirmation_required",
        "fence": "required_separate_reviewed_database_owned_primitive",
    },
    "appointment_update": {
        "operation": "confirmAppointmentUpdateProposal",
        "raw": (
            "PUT",
            "/api/v1/appointments/{appointment_id}",
            "update_appointment",
            "raw_compat_update",
        ),
        "proposals": {
            (
                "POST",
                "/api/v1/appointments/proposals/update/{appointment_id}",
                "propose_update_appointment",
                "proposal_command",
            ),
            (
                "POST",
                "/api/v1/appointments/proposals/bernie/tool-intent",
                "propose_bernie_tool_intent",
                "command_style_read_wrapper",
            ),
        },
        "confirms": {
            (
                "POST",
                "/api/v1/appointments/proposals/update/confirm",
                "confirm_update_proposal_route",
                "confirm_command",
            )
        },
        "target_shape": "existing_appointment_target",
        "locks": [
            "practice",
            "schedule_domain",
            "appointment",
            "idempotency_record",
        ],
        "confirmation": "separate_confirmation_required",
        "fence": "required_through_schedule_domain_serialization",
    },
    "appointment_status": {
        "operation": "confirmAppointmentStatusProposal",
        "raw": (
            "PATCH",
            "/api/v1/appointments/{appointment_id}/status",
            "update_appointment_status",
            "raw_compat_status",
        ),
        "proposals": {
            (
                "POST",
                "/api/v1/appointments/proposals/status/{appointment_id}",
                "propose_status_update",
                "proposal_command",
            ),
            (
                "POST",
                "/api/v1/appointments/proposals/waiting-area/{appointment_id}",
                "propose_waiting_area_update",
                "proposal_command_variant",
            ),
        },
        "confirms": {
            (
                "POST",
                "/api/v1/appointments/proposals/status-confirm",
                "confirm_status_proposal_route",
                "confirm_command",
            )
        },
        "target_shape": "existing_appointment_target",
        "locks": ["practice", "appointment", "idempotency_record"],
        "confirmation": "separate_confirmation_required",
        "fence": "not_required_unless_transition_changes_schedule_occupancy",
    },
    "appointment_delete": {
        "operation": "confirmAppointmentDeleteProposal",
        "raw": (
            "DELETE",
            "/api/v1/appointments/{appointment_id}",
            "cancel_appointment",
            "raw_compat_delete",
        ),
        "proposals": {
            (
                "POST",
                "/api/v1/appointments/proposals/delete/{appointment_id}",
                "propose_delete_appointment",
                "proposal_command",
            )
        },
        "confirms": {
            (
                "POST",
                "/api/v1/appointments/proposals/delete-confirm",
                "confirm_delete_proposal_route",
                "confirm_command",
            )
        },
        "target_shape": "existing_appointment_target",
        "locks": ["practice", "appointment", "idempotency_record"],
        "confirmation": "separate_destructive_confirmation_required",
        "fence": "not_required_for_retained_history_cancellation",
    },
}
EXPECTED_MIGRATION_STEPS = [
    "contract_freeze",
    "pure_adapter_differential_rehearsal",
    "default_off_shadow_mapping",
    "client_proposal_confirm_parity",
    "raw_status_kernel_convergence",
    "raw_delete_kernel_convergence",
    "raw_update_kernel_convergence",
    "create_schedule_fence_selection_and_proof",
    "raw_create_kernel_convergence",
    "raw_compat_header_rollout_decision",
    "raw_route_retirement_decision",
]
EXPECTED_DEPENDENCIES = {
    "contract_freeze": [],
    "pure_adapter_differential_rehearsal": ["contract_freeze"],
    "default_off_shadow_mapping": ["pure_adapter_differential_rehearsal"],
    "client_proposal_confirm_parity": ["default_off_shadow_mapping"],
    "raw_status_kernel_convergence": ["client_proposal_confirm_parity"],
    "raw_delete_kernel_convergence": ["raw_status_kernel_convergence"],
    "raw_update_kernel_convergence": ["raw_delete_kernel_convergence"],
    "create_schedule_fence_selection_and_proof": [
        "client_proposal_confirm_parity"
    ],
    "raw_create_kernel_convergence": [
        "raw_update_kernel_convergence",
        "create_schedule_fence_selection_and_proof",
    ],
    "raw_compat_header_rollout_decision": [
        "raw_status_kernel_convergence",
        "raw_delete_kernel_convergence",
        "raw_update_kernel_convergence",
        "raw_create_kernel_convergence",
    ],
    "raw_route_retirement_decision": ["raw_compat_header_rollout_decision"],
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_contract() -> dict[str, Any]:
    return _load(CONTRACT_PATH)


def load_schema() -> dict[str, Any]:
    return _load(SCHEMA_PATH)


def _route_tuple(route: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        route.get("method", ""),
        route.get("path", ""),
        route.get("handler", ""),
        route.get("classification", ""),
    )


def validate_contract(
    contract: dict[str, Any], *, verify_source_files: bool = True
) -> list[str]:
    reasons: list[str] = []
    validator = Draft202012Validator(load_schema())
    for error in sorted(validator.iter_errors(contract), key=lambda item: list(item.path)):
        location = "/".join(str(part) for part in error.path) or "$"
        reasons.append(f"schema:{location}:{error.message}")

    if reasons:
        return reasons

    if contract["source_head"] != EXPECTED_SOURCE_HEAD:
        reasons.append("source_head_mismatch")

    bindings = {row["path"]: row["sha256"] for row in contract["source_bindings"]}
    if bindings != EXPECTED_SOURCES:
        reasons.append("source_binding_set_or_digest_mismatch")
    if verify_source_files:
        for relative, expected in EXPECTED_SOURCES.items():
            path = ROOT / relative
            if not path.is_file():
                reasons.append(f"source_missing:{relative}")
            elif _sha256(path) != expected:
                reasons.append(f"source_digest_drift:{relative}")

    boundary = contract["claim_boundary"]
    if any(boundary.values()):
        reasons.append("claim_boundary_must_remain_all_false")

    kernel = contract["kernel_interface"]
    exact_kernel_lists = {
        "required_fields": EXPECTED_REQUEST_FIELDS,
        "outcomes": EXPECTED_OUTCOMES,
        "precedence": EXPECTED_PRECEDENCE,
        "canonical_lock_order": EXPECTED_LOCK_ORDER,
        "audit_fields": EXPECTED_AUDIT_FIELDS,
        "audit_forbidden_material": EXPECTED_AUDIT_FORBIDDEN,
    }
    for field, expected in exact_kernel_lists.items():
        if kernel[field] != expected:
            reasons.append(f"kernel_{field}_mismatch")
    if kernel["only_first_effect_outcome"] != "committed":
        reasons.append("only_committed_may_own_first_effect")
    if kernel["event_authority"] != "never":
        reasons.append("event_authority_must_be_never")
    if kernel["context_frame_authority"] != "never":
        reasons.append("context_frame_authority_must_be_never")

    families = {row["family_id"]: row for row in contract["route_families"]}
    if set(families) != set(EXPECTED_FAMILIES):
        reasons.append("route_family_set_mismatch")
    raw_paths: set[tuple[str, str]] = set()
    confirm_paths: set[tuple[str, str]] = set()
    for family_id, expected in EXPECTED_FAMILIES.items():
        family = families.get(family_id)
        if family is None:
            continue
        if family["canonical_operation_id"] != expected["operation"]:
            reasons.append(f"operation_mismatch:{family_id}")

        raw = family["raw_route"]
        observed_raw = (raw["method"], raw["path"], raw["handler"], raw["adapter_id"])
        if observed_raw != expected["raw"]:
            reasons.append(f"raw_route_mismatch:{family_id}")
        if raw["current_audit_signal"] != raw["adapter_id"]:
            reasons.append(f"raw_audit_adapter_mismatch:{family_id}")
        if raw["kernel_execution_eligible_now"] is not False:
            reasons.append(f"raw_route_must_remain_ineligible:{family_id}")
        if raw["current_confirmation"] != "absent_or_unproven_backend_evidence":
            reasons.append(f"raw_confirmation_gap_must_remain_explicit:{family_id}")
        if raw["current_precondition"] != "no_echoed_backend_precondition":
            reasons.append(f"raw_precondition_gap_must_remain_explicit:{family_id}")
        if raw["current_idempotency"] != "not_uniformly_command_enforced":
            reasons.append(f"raw_idempotency_gap_must_remain_explicit:{family_id}")
        raw_key = (raw["method"], raw["path"])
        if raw_key in raw_paths:
            reasons.append(f"duplicate_raw_route:{raw_key}")
        raw_paths.add(raw_key)

        observed_proposals = {_route_tuple(row) for row in family["proposal_routes"]}
        if observed_proposals != expected["proposals"]:
            reasons.append(f"proposal_route_set_mismatch:{family_id}")
        if any(row["mutates_appointment"] for row in family["proposal_routes"]):
            reasons.append(f"proposal_route_must_be_non_mutating:{family_id}")

        observed_confirms = {_route_tuple(row) for row in family["confirm_routes"]}
        if observed_confirms != expected["confirms"]:
            reasons.append(f"confirm_route_set_mismatch:{family_id}")
        for route in family["confirm_routes"]:
            if route["canonical_operation_id"] != expected["operation"]:
                reasons.append(f"confirm_operation_alias_mismatch:{family_id}")
            confirm_key = (route["method"], route["path"])
            if confirm_key in confirm_paths:
                reasons.append(f"duplicate_confirm_route:{confirm_key}")
            confirm_paths.add(confirm_key)

        target = family["kernel_target"]
        if target["target_shape"] != expected["target_shape"]:
            reasons.append(f"target_shape_mismatch:{family_id}")
        if target["required_lock_plan"] != expected["locks"]:
            reasons.append(f"lock_plan_mismatch:{family_id}")
        if target["confirmation"] != expected["confirmation"]:
            reasons.append(f"confirmation_requirement_mismatch:{family_id}")
        if target["schedule_fence"] != expected["fence"]:
            reasons.append(f"schedule_fence_mismatch:{family_id}")
        if not target["freshness"].startswith("backend_minted_expected_source"):
            reasons.append(f"freshness_binding_weakened:{family_id}")
        if target["idempotency"] != (
            "durable_same_operation_key_and_command_digest_required"
        ):
            reasons.append(f"idempotency_requirement_weakened:{family_id}")
        if target["audit"] != (
            "attributable_atomic_decision_and_commit_evidence_required"
        ):
            reasons.append(f"audit_requirement_weakened:{family_id}")
        if not target["raw_convergence_gate"].startswith("blocked_until_"):
            reasons.append(f"raw_convergence_gate_opened:{family_id}")

    migration = contract["migration"]
    if migration["current_raw_compat_mode"] != "audit":
        reasons.append("raw_compat_mode_changed")
    if migration["header_mode_decision"] != "blocked":
        reasons.append("header_mode_gate_opened")
    steps = migration["steps"]
    step_ids = [row["step_id"] for row in steps]
    if step_ids != EXPECTED_MIGRATION_STEPS:
        reasons.append("migration_step_order_mismatch")
    if [row["order"] for row in steps] != list(range(1, 12)):
        reasons.append("migration_numeric_order_mismatch")
    step_positions = {step_id: index for index, step_id in enumerate(step_ids)}
    for row in steps:
        step_id = row["step_id"]
        expected_dependencies = EXPECTED_DEPENDENCIES.get(step_id)
        if row["depends_on"] != expected_dependencies:
            reasons.append(f"migration_dependencies_mismatch:{step_id}")
        for dependency in row["depends_on"]:
            if dependency not in step_positions:
                reasons.append(f"unknown_migration_dependency:{step_id}:{dependency}")
            elif step_positions[dependency] >= step_positions[step_id]:
                reasons.append(f"future_or_cyclic_dependency:{step_id}:{dependency}")
    if any(row["behavior_change"] for row in steps[:3]):
        reasons.append("pre_runtime_migration_step_changes_behavior")
    if steps[7]["behavior_change"] is not False:
        reasons.append("create_fence_design_step_must_not_claim_route_behavior")

    return sorted(set(reasons))


def build_report(contract: dict[str, Any] | None = None) -> dict[str, Any]:
    selected = load_contract() if contract is None else contract
    reasons = validate_contract(selected)
    return {
        "schema_version": "emr4.legacy-route-convergence-kernel-interface-report.v1",
        "status": "passed" if not reasons else "revision_required",
        "reasons": reasons,
        "source_head": selected.get("source_head"),
        "source_binding_count": len(selected.get("source_bindings", [])),
        "route_family_count": len(selected.get("route_families", [])),
        "raw_route_count": len(selected.get("route_families", [])),
        "proposal_route_count": sum(
            len(row.get("proposal_routes", []))
            for row in selected.get("route_families", [])
        ),
        "confirm_route_count": sum(
            len(row.get("confirm_routes", []))
            for row in selected.get("route_families", [])
        ),
        "migration_step_count": len(selected.get("migration", {}).get("steps", [])),
        "route_behavior_changed": selected.get("claim_boundary", {}).get(
            "route_behavior_changed"
        ),
        "command_or_write_performed": selected.get("claim_boundary", {}).get(
            "command_or_write_performed"
        ),
    }


def main() -> int:
    report = build_report()
    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
