"""Validate the inert default-off shadow-comparison architecture contract."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-default-off-shadow-comparison-architecture"
)
CONTRACT_PATH = CONTRACT_DIR / "contract.json"
SCHEMA_PATH = CONTRACT_DIR / "contract.schema.json"
PARENT_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-pure-route-adapter-differential-rehearsal"
    / "contract.json"
)

EXPECTED_SOURCE_HEAD = "71e240218b1adf1214fff87b542a9d0f6764230e"
EXPECTED_SOURCES = {
    "orchestration/continuity/raisa-provider-free-unmounted-pure-route-adapter-differential-rehearsal/contract.json": "050ddc373b5ca7f1f00207122da653fd9bb5dae01c7b313a88fa529e6b640ddc",
    "docs/raisa-provider-free-unmounted-pure-route-adapter-differential-rehearsal-plan.md": "91b3be0c756443bbe8b4b2fe5fe5a11bc61358b8f74db9eda36a33fc67786c27",
    "docs/raisa-provider-free-unmounted-pure-route-adapter-differential-rehearsal-design.md": "a1e700ae24a7b6143357edc7d84a325d8492c39b70abf0d887a962f601b430f0",
    "docs/raisa-provider-free-unmounted-pure-route-adapter-differential-rehearsal-closeout.md": "b84b6816038aa0177df3485acafe0a93acb3cedaec2fb3f337510d9fe089b0b6",
    "orchestration/continuity/raisa-provider-free-unmounted-legacy-route-convergence-kernel-interface/contract.json": "abe1e35032ca5a979ac187b45adffc498897e341d185b65c8e0eb6b094cfb582",
    "orchestration/api_spine_adr.md": "d0fa77aec371d634284f81bf1fd6cfd49bb5a52fbe14003a17c5e35dcaf0283e",
}
EXPECTED_ROUTES = {
    "raw_compat_create": ("appointment_create", "POST", "/api/v1/appointments", "confirmAppointmentCreateProposal"),
    "raw_compat_update": ("appointment_update", "PUT", "/api/v1/appointments/{appointment_id}", "confirmAppointmentUpdateProposal"),
    "raw_compat_status": ("appointment_status", "PATCH", "/api/v1/appointments/{appointment_id}/status", "confirmAppointmentStatusProposal"),
    "raw_compat_delete": ("appointment_delete", "DELETE", "/api/v1/appointments/{appointment_id}", "confirmAppointmentDeleteProposal"),
}
EXPECTED_ENABLEMENT = {
    "generation_model": "immutable_new_generation_for_any_amendment",
    "required_generation_status": "current",
    "global_default": "disabled",
    "practice_default": "disabled",
    "route_allowlist_default": [],
    "admission_expression": "generation_current AND global_enabled AND practice_enabled AND exact_route_allowlisted AND NOT externally_disabled",
    "unknown_or_missing_control": "disabled_no_observation",
    "stale_superseded_or_revoked_generation": "disabled_no_observation",
    "external_kill_switch": "disable_only_cannot_enable",
    "enablement_authority_granted": False,
}
EXPECTED_PRIMARY_COMPONENTS = [
    "http_status",
    "response_body",
    "response_headers",
    "transaction_disposition",
    "mutation_audit_disposition",
]
EXPECTED_GAPS = [
    "backend_precondition_missing",
    "confirmation_evidence_missing",
    "idempotency_identity_missing",
]
EXPECTED_COMPARISONS = [
    "expected_current_gap_match",
    "unexpected_gap_set",
    "unexpected_candidate_mapped",
    "candidate_projection_divergent",
    "candidate_projection_equivalent",
    "observer_failed",
    "disabled_no_observation",
]
EXPECTED_FEEDBACK_EDGES = [
    "shadow_to_request_admission",
    "shadow_to_authorization",
    "shadow_to_http_status",
    "shadow_to_response_body",
    "shadow_to_response_headers",
    "shadow_to_transaction",
    "shadow_to_mutation",
    "shadow_to_mutation_audit",
    "shadow_to_retry",
    "shadow_to_latency_budget",
    "shadow_to_kernel_eligibility",
    "shadow_to_client_behavior",
]
EXPECTED_SEQUENCE = [
    "provider_free_unmounted_authored_synthetic_shadow_comparison_rehearsal",
    "separately_reviewed_default_off_runtime_instrumentation",
    "ordinary_and_fallback_client_proposal_confirm_parity",
    "raw_status_kernel_convergence",
    "raw_delete_kernel_convergence",
    "raw_update_kernel_convergence",
    "create_schedule_fence_selection_and_proof",
    "raw_create_kernel_convergence",
]
EXPECTED_PROJECTION_FIELDS = [
    "schema_version",
    "architecture_generation_digest",
    "route_adapter_id",
    "canonical_operation_id",
    "practice_scope_digest",
    "actor_digest",
    "actor_role",
    "session_digest",
    "purpose",
    "target_shape",
    "target_digest",
    "conflict_domain_digest",
    "command_digest",
    "precondition_present",
    "precondition_version",
    "precondition_digest",
    "confirmation_present",
    "confirmation_mode",
    "confirmation_reference_digest",
    "idempotency_present",
    "idempotency_key_digest",
    "canonicalization_version",
    "correlation_digest",
    "request_shape_digest",
]
EXPECTED_RECORD_FIELDS = [
    "schema_version",
    "architecture_generation_digest",
    "configuration_digest",
    "route_adapter_id",
    "canonical_operation_id",
    "practice_scope_digest",
    "correlation_digest",
    "request_shape_digest",
    "adapter_result",
    "gap_codes",
    "mismatch_field_codes",
    "comparison_class",
    "timing_category",
    "overflow_category",
    "recorded_at",
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_contract() -> dict[str, Any]:
    return _load(CONTRACT_PATH)


def load_schema() -> dict[str, Any]:
    return _load(SCHEMA_PATH)


def admission_decision(
    *,
    generation_status: str | None,
    global_state: str | None,
    practice_state: str | None,
    route_allowed: bool | None,
    externally_disabled: bool | None,
) -> str:
    if (
        generation_status != "current"
        or global_state != "enabled"
        or practice_state != "enabled"
        or route_allowed is not True
        or externally_disabled is not False
    ):
        return "disabled_no_observation"
    return "shadow_observation_admitted"


def semantic_errors(packet: dict[str, Any], *, verify_source_files: bool = False) -> list[str]:
    errors: list[str] = []
    if packet["source_head"] != EXPECTED_SOURCE_HEAD:
        errors.append("source_head_mismatch")
    bindings = {row["path"]: row["sha256"] for row in packet["source_bindings"]}
    if bindings != EXPECTED_SOURCES:
        errors.append("source_bindings_mismatch")
    if verify_source_files:
        for path, digest in EXPECTED_SOURCES.items():
            source = ROOT / path
            if not source.is_file() or _hash(source) != digest:
                errors.append(f"source_file_hash_mismatch:{path}")

    parent = _load(PARENT_PATH)
    routes = packet["scope"]["route_adapters"]
    observed_routes = {
        row["adapter_id"]: (
            row["family_id"], row["method"], row["path"], row["canonical_operation_id"]
        )
        for row in routes
    }
    if len(observed_routes) != len(routes):
        errors.append("route_adapter_duplicate")
    if observed_routes != EXPECTED_ROUTES:
        errors.append("raw_route_scope_mismatch")
    parent_raw = {
        row["adapter_id"]: (
            row["family_id"], row["method"], row["path"], row["canonical_operation_id"]
        )
        for row in parent["adapter_specs"]
        if row["ingress_kind"] == "raw"
    }
    if observed_routes != parent_raw:
        errors.append("parent_raw_route_binding_mismatch")
    if packet["scope"]["proposal_routes_in_scope"] or packet["scope"]["confirm_routes_in_scope"]:
        errors.append("non_raw_route_scope_open")
    if packet["scope"]["current_parent_posture"] != "current_raw_not_kernel_eligible":
        errors.append("parent_route_posture_changed")

    if packet["enablement"] != EXPECTED_ENABLEMENT:
        errors.append("enablement_contract_mismatch")
    denied_variants = [
        (None, "enabled", "enabled", True, False),
        ("stale", "enabled", "enabled", True, False),
        ("current", None, "enabled", True, False),
        ("current", "disabled", "enabled", True, False),
        ("current", "enabled", None, True, False),
        ("current", "enabled", "disabled", True, False),
        ("current", "enabled", "enabled", None, False),
        ("current", "enabled", "enabled", False, False),
        ("current", "enabled", "enabled", True, None),
        ("current", "enabled", "enabled", True, True),
    ]
    for variant in denied_variants:
        if admission_decision(
            generation_status=variant[0], global_state=variant[1],
            practice_state=variant[2], route_allowed=variant[3],
            externally_disabled=variant[4]
        ) != "disabled_no_observation":
            errors.append("default_deny_variant_admitted")
    if admission_decision(
        generation_status="current", global_state="enabled",
        practice_state="enabled", route_allowed=True,
        externally_disabled=False
    ) != "shadow_observation_admitted":
        errors.append("exact_intersection_not_admitted")

    placement = packet["placement"]
    if placement["primary_result_components"] != EXPECTED_PRIMARY_COMPONENTS:
        errors.append("sealed_primary_component_mismatch")
    expected_placement = {
        "primary_owner": "authoritative_appointment_handler",
        "primary_result_state_before_observation": "sealed_immutable",
        "handoff_direction": "primary_to_shadow_only",
        "handler_return_channel": "none",
        "delivery": "bounded_best_effort_at_most_once",
        "overflow": "drop_shadow_evidence_only",
        "timeout": "drop_shadow_evidence_only",
        "observer_failure": "contain_and_drop_or_emit_bounded_failure_record",
        "retry_required": False,
        "correctness_dependency": False,
    }
    if any(placement[key] != value for key, value in expected_placement.items()):
        errors.append("placement_or_failure_isolation_mismatch")

    projection = packet["projection"]
    if projection["allowed_fields"] != EXPECTED_PROJECTION_FIELDS:
        errors.append("projection_field_set_mismatch")
    if projection["identity_encoding"] != "versioned_one_way_hmac_digest":
        errors.append("identity_encoding_mismatch")
    required_forbidden = {
        "raw_request_body", "raw_response_body", "patient_identifier",
        "appointment_reason_free_text", "appointment_note_free_text",
        "direct_practice_id", "direct_actor_id", "direct_target_id",
        "raw_confirmation_token", "credential", "source_state",
        "authority_decision", "database_value", "mutation_receipt", "audit_receipt",
    }
    if not required_forbidden <= set(projection["forbidden_material"]):
        errors.append("projection_forbidden_material_missing")
    forbidden_allowed = {
        "raw_request_body", "raw_response_body", "patient_identifier",
        "patient_name", "date_of_birth", "phone_number", "medicare_number",
        "appointment_reason_free_text", "appointment_note_free_text",
        "direct_practice_id", "direct_actor_id", "direct_session_id",
        "direct_target_id", "direct_correlation_id", "raw_confirmation_token",
        "credential", "source_state", "authority_decision", "database_value",
        "mutation_receipt", "audit_receipt",
    } & set(projection["allowed_fields"])
    if forbidden_allowed:
        errors.append("projection_allows_forbidden_material")

    observer = packet["observer"]
    if observer["expected_current_gap_codes"] != EXPECTED_GAPS:
        errors.append("expected_gap_codes_mismatch")
    if observer["expected_current_gap_codes"] != parent["envelope_profiles"]["raw_current"]["missing_control_codes"]:
        errors.append("parent_gap_codes_mismatch")
    if observer["comparison_classes"] != EXPECTED_COMPARISONS:
        errors.append("comparison_class_mismatch")
    if any(observer["capabilities"].values()):
        errors.append("observer_capability_open")
    if (
        observer["candidate_executable"]
        or observer["runtime_execution_authorized"]
        or observer["command_outcome_emitted"]
        or observer["parent_route_posture_changed"]
    ):
        errors.append("observer_authority_boundary_open")

    record = packet["diagnostic_record"]
    if record["allowed_fields"] != EXPECTED_RECORD_FIELDS:
        errors.append("record_field_set_mismatch")
    if not {"command_outcome", "mutation_receipt", "audit_receipt", "patient_data", "free_text"} <= set(record["forbidden_material"]):
        errors.append("record_forbidden_material_missing")
    if any(
        record[key]
        for key in (
            "is_audit_record", "is_command_receipt", "is_source_truth",
            "persistence_selected", "retention_selected", "aggregation_selected",
        )
    ):
        errors.append("diagnostic_record_authority_or_persistence_open")
    if record["authority"] != "diagnostic_only_non_authoritative_lossy":
        errors.append("diagnostic_record_authority_mismatch")

    if packet["forbidden_feedback_edges"] != EXPECTED_FEEDBACK_EDGES:
        errors.append("feedback_edge_contract_mismatch")
    if packet["future_evidence_sequence"] != EXPECTED_SEQUENCE:
        errors.append("future_evidence_sequence_mismatch")
    if any(packet["claim_boundary"].values()):
        errors.append("claim_boundary_not_zero")
    if any(packet["effect_boundary"].values()):
        errors.append("effect_boundary_not_zero")
    return sorted(set(errors))


def validate_contract(packet: dict[str, Any], *, verify_source_files: bool = False) -> list[str]:
    schema = load_schema()
    Draft202012Validator.check_schema(schema)
    schema_errors = sorted(
        f"schema:{error.json_path}:{error.message}"
        for error in Draft202012Validator(schema).iter_errors(packet)
    )
    try:
        semantic = semantic_errors(packet, verify_source_files=verify_source_files)
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        semantic = [f"semantic_validation_failed:{type(error).__name__}"]
    return sorted(set(schema_errors + semantic))


def hostile_mutations(packet: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("source_head", lambda p: p.__setitem__("source_head", "0" * 40)),
        ("source_hash", lambda p: p["source_bindings"][0].__setitem__("sha256", "0" * 64)),
        ("source_removed", lambda p: p["source_bindings"].pop()),
        ("route_behavior", lambda p: p["claim_boundary"].__setitem__("route_behavior_changed", True)),
        ("route_import", lambda p: p["claim_boundary"].__setitem__("application_route_imported", True)),
        ("runtime_created", lambda p: p["claim_boundary"].__setitem__("observer_runtime_created", True)),
        ("database_access", lambda p: p["claim_boundary"].__setitem__("database_or_source_accessed", True)),
        ("product_data", lambda p: p["claim_boundary"].__setitem__("product_or_patient_data_used", True)),
        ("command_invoked", lambda p: p["claim_boundary"].__setitem__("kernel_or_command_invoked", True)),
        ("route_removed", lambda p: p["scope"]["route_adapters"].pop()),
        ("route_duplicate", lambda p: p["scope"]["route_adapters"].__setitem__(3, copy.deepcopy(p["scope"]["route_adapters"][2]))),
        ("confirm_in_scope", lambda p: p["scope"].__setitem__("confirm_routes_in_scope", True)),
        ("posture_changed", lambda p: p["scope"].__setitem__("current_parent_posture", "kernel_eligible")),
        ("global_default", lambda p: p["enablement"].__setitem__("global_default", "enabled")),
        ("practice_default", lambda p: p["enablement"].__setitem__("practice_default", "enabled")),
        ("route_default", lambda p: p["enablement"]["route_allowlist_default"].append("raw_compat_status")),
        ("generation_mutable", lambda p: p["enablement"].__setitem__("generation_model", "mutable")),
        ("intersection_weakened", lambda p: p["enablement"].__setitem__("admission_expression", "global_enabled OR practice_enabled")),
        ("kill_switch_enables", lambda p: p["enablement"].__setitem__("external_kill_switch", "enable_or_disable")),
        ("enablement_authority", lambda p: p["enablement"].__setitem__("enablement_authority_granted", True)),
        ("primary_unsealed", lambda p: p["placement"].__setitem__("primary_result_state_before_observation", "mutable")),
        ("return_channel", lambda p: p["placement"].__setitem__("handler_return_channel", "observer_result")),
        ("synchronous_delivery", lambda p: p["placement"].__setitem__("delivery", "blocking_exactly_once")),
        ("overflow_blocks", lambda p: p["placement"].__setitem__("overflow", "block_primary")),
        ("timeout_fails", lambda p: p["placement"].__setitem__("timeout", "fail_request")),
        ("retry_required", lambda p: p["placement"].__setitem__("retry_required", True)),
        ("correctness_dependency", lambda p: p["placement"].__setitem__("correctness_dependency", True)),
        ("projection_field_removed", lambda p: p["projection"]["allowed_fields"].pop()),
        ("projection_raw_body", lambda p: p["projection"]["allowed_fields"].append("raw_request_body")),
        ("projection_forbidden_removed", lambda p: p["projection"]["forbidden_material"].remove("patient_identifier")),
        ("identity_reversible", lambda p: p["projection"].__setitem__("identity_encoding", "plain_text")),
        ("candidate_executable", lambda p: p["observer"].__setitem__("candidate_executable", True)),
        ("kernel_capability", lambda p: p["observer"]["capabilities"].__setitem__("kernel_entry_point", True)),
        ("response_capability", lambda p: p["observer"]["capabilities"].__setitem__("response_writer", True)),
        ("gap_removed", lambda p: p["observer"]["expected_current_gap_codes"].pop()),
        ("comparison_added", lambda p: p["observer"]["comparison_classes"].append("enforce_rejection")),
        ("outcome_emitted", lambda p: p["observer"].__setitem__("command_outcome_emitted", True)),
        ("posture_mutated", lambda p: p["observer"].__setitem__("parent_route_posture_changed", True)),
        ("record_field_removed", lambda p: p["diagnostic_record"]["allowed_fields"].pop()),
        ("record_candidate", lambda p: p["diagnostic_record"]["allowed_fields"].append("kernel_candidate")),
        ("record_audit", lambda p: p["diagnostic_record"].__setitem__("is_audit_record", True)),
        ("persistence_selected", lambda p: p["diagnostic_record"].__setitem__("persistence_selected", True)),
        ("feedback_removed", lambda p: p["forbidden_feedback_edges"].remove("shadow_to_response_body")),
        ("sequence_reordered", lambda p: p["future_evidence_sequence"].reverse()),
        ("effect_runtime", lambda p: p["effect_boundary"].__setitem__("observer_runtime", True)),
        ("effect_response", lambda p: p["effect_boundary"].__setitem__("response_change", True)),
    ]
    results: list[tuple[str, dict[str, Any]]] = []
    for name, mutate in mutations:
        candidate = copy.deepcopy(packet)
        mutate(candidate)
        results.append((name, candidate))
    return results


def build_report(packet: dict[str, Any] | None = None) -> dict[str, Any]:
    packet = load_contract() if packet is None else packet
    errors = validate_contract(packet, verify_source_files=True)
    mutants = hostile_mutations(packet)
    escaped = [name for name, mutant in mutants if not validate_contract(mutant)]
    if escaped:
        errors.append("hostile_mutation_escaped:" + ",".join(escaped))
    return {
        "schema_version": "emr4.default-off-shadow-comparison-architecture-report.v1",
        "status": "passed" if not errors else "failed",
        "reasons": sorted(set(errors)),
        "source_head": packet["source_head"],
        "raw_route_count": len(packet["scope"]["route_adapters"]),
        "enablement_dimension_count": 4,
        "projection_field_count": len(packet["projection"]["allowed_fields"]),
        "record_field_count": len(packet["diagnostic_record"]["allowed_fields"]),
        "forbidden_feedback_edge_count": len(packet["forbidden_feedback_edges"]),
        "hostile_mutation_count": len(mutants),
        "hostile_mutation_escape_count": len(escaped),
        "observer_runtime_created": False,
        "command_or_write_performed": False,
    }


def main() -> int:
    report = build_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
