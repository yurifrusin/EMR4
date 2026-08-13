from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PACKET_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-cf-d2-observability-first-event-cue"
)
CONTRACT_PATH = PACKET_DIR / "observability-contract.json"
SCHEMA_PATH = PACKET_DIR / "observability-contract.schema.json"
API_SPINE_PATH = (
    ROOT / "docs" / "api-spine" / "async" / "durable-diary-event-cue-observability.yaml"
)

EXPECTED_AUTHORITY = {
    "source_owns_current_truth": True,
    "context_frame_is_expiring_read_only_evidence": True,
    "event_is_acceleration_hint_only": True,
    "cue_is_acceleration_hint_only": True,
    "event_or_cue_may_assert_command_success": False,
    "event_or_cue_may_grant_command_authority": False,
    "consumer_must_fresh_read": True,
    "command_must_recheck_current_authority_and_source_truth": True,
}
EXPECTED_CLASSIFICATIONS = {
    "cue_required",
    "suppressed_irrelevant",
    "rejected_unsupported",
}
EXPECTED_DIAGNOSTIC_STAGES = {
    "source_head_unknown",
    "observation_lag",
    "position_gap",
    "classification_gap",
    "classification_rejected",
    "obligation_gap",
    "dispatch_lag",
    "dispatch_failed",
    "ownership_fenced",
    "reconciliation_failed",
}
EXPECTED_CUE_FIELDS = {
    "cue_schema_version",
    "obligation_id",
    "practice_scope_digest",
    "consumer_scope",
    "event_family",
    "source_epoch",
    "from_position",
    "through_position",
    "reason_code",
    "fresh_authorized_read_required",
}
EXPECTED_PROHIBITED_CONTENT = {
    "appointment_or_person_identifier",
    "appointment_status_or_time",
    "patient_or_clinical_content",
    "free_text_or_event_payload",
    "command_result_or_receipt",
    "precondition_or_confirmation_evidence",
    "credential_or_provider_output",
}
EXPECTED_OPERATOR_EVIDENCE = {
    "partition_digest",
    "source_epoch_digest",
    "source_head_state",
    "observed_position",
    "checkpoint_position",
    "lag_state_and_value_or_null",
    "receipt_state_and_reason_code",
    "pending_obligation_count",
    "oldest_pending_age_bucket",
    "lease_generation_digest",
    "last_dispatch_state",
    "last_reconciliation_state",
}


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def semantic_errors(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if contract["authority"] != EXPECTED_AUTHORITY:
        errors.append("authority_boundary_mismatch")

    partition = contract["partition"]
    if partition != {
        "key_fields": ["source_system", "practice_scope_digest", "event_family"],
        "logical_consumer_count": 1,
        "initial_physical_consumers_per_database": 1,
        "high_availability_mode": "active_standby_external_lease_and_fencing",
        "equal_checkpoint_writers_allowed": False,
    }:
        errors.append("partition_or_fencing_mismatch")

    position = contract["position"]
    required_true = {
        "ordered_within_partition_epoch_only",
        "source_head_distinct_from_observed",
        "observed_distinct_from_checkpoint",
        "checkpoint_requires_contiguous_terminal_receipts",
        "checkpoint_requires_atomic_required_obligation",
    }
    if position["coordinate_fields"] != ["source_epoch", "source_position"]:
        errors.append("position_coordinate_mismatch")
    if position["source_position_minimum"] != 1:
        errors.append("position_must_be_positive")
    for field in required_true:
        if position[field] is not True:
            errors.append(f"position_control_false:{field}")
    if position["delivery_required_before_checkpoint"] is not False:
        errors.append("delivery_must_not_gate_checkpoint")
    if position["gap_crossing_allowed"] is not False:
        errors.append("checkpoint_must_not_cross_gap")

    classification = contract["classification"]
    if set(classification["terminal_results"]) != EXPECTED_CLASSIFICATIONS:
        errors.append("classification_census_mismatch")
    if classification["exactly_one_terminal_receipt_per_position"] is not True:
        errors.append("classification_receipt_not_unique")
    if classification["duplicate_returns_original_receipt"] is not True:
        errors.append("duplicate_must_return_original_receipt")
    if classification["divergent_identity_result"] != "identity_conflict":
        errors.append("divergent_identity_must_conflict")
    if classification["identity_conflict_advances_checkpoint"] is not False:
        errors.append("identity_conflict_must_not_advance")
    if classification["rejected_event_creates_obligation"] is not False:
        errors.append("rejected_event_must_not_create_obligation")

    cue = contract["cue_obligation"]
    if set(cue["required_fields"]) != EXPECTED_CUE_FIELDS:
        errors.append("cue_field_census_mismatch")
    if set(cue["prohibited_content"]) != EXPECTED_PROHIBITED_CONTENT:
        errors.append("cue_prohibited_content_mismatch")
    if cue["consumer_scope"] != "reception_one_diary_projection":
        errors.append("cue_consumer_scope_mismatch")
    if cue["delivery_semantics"] != "at_least_once":
        errors.append("cue_delivery_semantics_mismatch")
    if cue["duplicate_policy"] != "reuse_original_obligation":
        errors.append("cue_duplicate_policy_mismatch")
    if (
        cue["coalescing_policy"]
        != "contiguous_pending_same_partition_consumer_and_reason_only"
    ):
        errors.append("cue_coalescing_scope_too_broad")
    if cue["fresh_authorized_read_required"] is not True:
        errors.append("cue_must_require_fresh_read")

    lag = contract["lag"]
    if set(lag["states"]) != {"exact", "unknown", "epoch_mismatch"}:
        errors.append("lag_state_census_mismatch")
    if lag["exact_formula"] != "source_head_minus_checkpoint_within_same_epoch":
        errors.append("lag_formula_mismatch")
    if lag["unknown_may_serialize_as_zero"] is not False:
        errors.append("unknown_lag_must_not_be_zero")
    if lag["epoch_mismatch_may_serialize_as_zero"] is not False:
        errors.append("epoch_mismatch_must_not_be_zero")

    reconciliation = contract["reconciliation"]
    if reconciliation["cue_may_directly_update_display"] is not False:
        errors.append("cue_must_not_update_display_directly")
    if reconciliation["practice_role_resource_recheck_required"] is not True:
        errors.append("reconciliation_must_recheck_scope")
    if reconciliation["fresh_scoped_read_required"] is not True:
        errors.append("reconciliation_must_fresh_read")
    if reconciliation["acknowledgement_confers_future_freshness"] is not False:
        errors.append("acknowledgement_must_not_confer_future_freshness")

    diagnostics = contract["diagnostics"]
    stages = diagnostics["stages"]
    stage_names = [item["stage"] for item in stages]
    observables = [item["observable"] for item in stages]
    responses = [item["safe_response"] for item in stages]
    if set(stage_names) != EXPECTED_DIAGNOSTIC_STAGES or len(stage_names) != len(
        EXPECTED_DIAGNOSTIC_STAGES
    ):
        errors.append("diagnostic_stage_census_mismatch")
    if len(set(observables)) != len(observables):
        errors.append("diagnostic_observables_not_distinct")
    if len(set(responses)) != len(responses):
        errors.append("diagnostic_safe_responses_not_distinct")
    if diagnostics["generic_collapsed_failure_coordinate_allowed"] is not False:
        errors.append("collapsed_failure_coordinate_forbidden")
    if diagnostics["distinct_observable_per_stage_required"] is not True:
        errors.append("distinct_observable_not_required")
    if diagnostics["distinct_safe_response_per_stage_required"] is not True:
        errors.append("distinct_safe_response_not_required")

    if set(contract["retained_operator_evidence"]) != EXPECTED_OPERATOR_EVIDENCE:
        errors.append("operator_evidence_census_mismatch")
    if len(contract["forbidden_effects"]) != 10:
        errors.append("forbidden_effect_census_mismatch")
    if contract["prior_evidence"] != {
        "cf_d1_concurrency_retained": True,
        "stopped_cf_d2_attempts_remain_negative_evidence": True,
        "old_four_crash_anchor_protocol_retried": False,
        "workflow_evidence_led_gate_applied": True,
    }:
        errors.append("prior_evidence_boundary_mismatch")
    if contract["next_descendant"] != {
        "id": "provider-free-unmounted-event-cue-admission-rehearsal",
        "authored_synthetic_only": True,
        "pure_state_machine_only": True,
        "runtime": False,
        "database_or_source": False,
        "persistence": False,
        "provider_call": False,
        "command_or_write": False,
    }:
        errors.append("next_descendant_broadens_authority")
    return errors


def api_spine_errors(api_contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    authority = api_contract["authority_boundary"]
    expected_false = {
        "event_is_current_truth",
        "cue_is_current_truth",
        "event_or_cue_is_command_authority",
        "event_or_cue_is_command_receipt",
    }
    expected_true = {
        "fresh_authorized_read_before_display",
        "consequential_mutation_requires_rest_command",
        "command_rechecks_current_authority_and_source_truth",
    }
    for field in expected_false:
        if authority[field] is not False:
            errors.append(f"api_spine_authority_true:{field}")
    for field in expected_true:
        if authority[field] is not True:
            errors.append(f"api_spine_control_false:{field}")
    if api_contract["closed_surfaces"] != {
        "runtime_wiring": "blocked",
        "watcher_listener_worker": "blocked",
        "database_or_source_access": "blocked",
        "operational_retention": "blocked",
        "product_patient_clinical_data": "blocked",
        "external_patient_clients": "blocked",
        "provider_adc_credentials_iam_network": "blocked",
        "executable_tools_commands_or_writes": "blocked",
        "graphql_openapi_route_changes": "blocked",
        "deployment_production_release_pages": "blocked",
        "protected_refs": "blocked",
    }:
        errors.append("api_spine_closed_surface_mismatch")
    return errors


def validate_contract(
    contract: dict[str, Any], schema: dict[str, Any], api_contract: dict[str, Any]
) -> list[str]:
    Draft202012Validator.check_schema(schema)
    schema_errors = sorted(
        error.message for error in Draft202012Validator(schema).iter_errors(contract)
    )
    return schema_errors + semantic_errors(contract) + api_spine_errors(api_contract)


def _mutate(
    contract: dict[str, Any], path: tuple[Any, ...], value: Any
) -> dict[str, Any]:
    changed = copy.deepcopy(contract)
    cursor: Any = changed
    for component in path[:-1]:
        cursor = cursor[component]
    cursor[path[-1]] = value
    return changed


def hostile_mutations(contract: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    cases: list[tuple[str, tuple[Any, ...], Any]] = [
        ("source_loses_truth", ("authority", "source_owns_current_truth"), False),
        ("event_claims_truth", ("authority", "event_is_acceleration_hint_only"), False),
        ("cue_claims_truth", ("authority", "cue_is_acceleration_hint_only"), False),
        (
            "event_claims_success",
            ("authority", "event_or_cue_may_assert_command_success"),
            True,
        ),
        (
            "cue_grants_command",
            ("authority", "event_or_cue_may_grant_command_authority"),
            True,
        ),
        ("consumer_skips_read", ("authority", "consumer_must_fresh_read"), False),
        (
            "command_skips_recheck",
            ("authority", "command_must_recheck_current_authority_and_source_truth"),
            False,
        ),
        ("two_logical_consumers", ("partition", "logical_consumer_count"), 2),
        (
            "equal_checkpoint_writers",
            ("partition", "equal_checkpoint_writers_allowed"),
            True,
        ),
        ("position_starts_zero", ("position", "source_position_minimum"), 0),
        (
            "cross_epoch_order",
            ("position", "ordered_within_partition_epoch_only"),
            False,
        ),
        (
            "head_equals_observed",
            ("position", "source_head_distinct_from_observed"),
            False,
        ),
        (
            "observed_equals_checkpoint",
            ("position", "observed_distinct_from_checkpoint"),
            False,
        ),
        (
            "checkpoint_skips_receipt",
            ("position", "checkpoint_requires_contiguous_terminal_receipts"),
            False,
        ),
        (
            "checkpoint_skips_obligation",
            ("position", "checkpoint_requires_atomic_required_obligation"),
            False,
        ),
        (
            "delivery_gates_checkpoint",
            ("position", "delivery_required_before_checkpoint"),
            True,
        ),
        ("checkpoint_crosses_gap", ("position", "gap_crossing_allowed"), True),
        (
            "duplicate_new_receipt",
            ("classification", "duplicate_returns_original_receipt"),
            False,
        ),
        (
            "identity_conflict_advances",
            ("classification", "identity_conflict_advances_checkpoint"),
            True,
        ),
        (
            "reject_creates_obligation",
            ("classification", "rejected_event_creates_obligation"),
            True,
        ),
        (
            "cue_includes_identifier",
            ("cue_obligation", "prohibited_content", 0),
            "allowed_identifier",
        ),
        (
            "cue_skips_fresh_read",
            ("cue_obligation", "fresh_authorized_read_required"),
            False,
        ),
        ("cue_exactly_once", ("cue_obligation", "delivery_semantics"), "exactly_once"),
        (
            "cue_broad_coalescing",
            ("cue_obligation", "coalescing_policy"),
            "all_pending",
        ),
        ("unknown_lag_zero", ("lag", "unknown_may_serialize_as_zero"), True),
        ("epoch_lag_zero", ("lag", "epoch_mismatch_may_serialize_as_zero"), True),
        (
            "cue_updates_display",
            ("reconciliation", "cue_may_directly_update_display"),
            True,
        ),
        (
            "reconcile_skips_scope",
            ("reconciliation", "practice_role_resource_recheck_required"),
            False,
        ),
        (
            "ack_confers_freshness",
            ("reconciliation", "acknowledgement_confers_future_freshness"),
            True,
        ),
        (
            "collapse_coordinate",
            ("diagnostics", "generic_collapsed_failure_coordinate_allowed"),
            True,
        ),
        (
            "duplicate_observable",
            ("diagnostics", "stages", 1, "observable"),
            contract["diagnostics"]["stages"][0]["observable"],
        ),
        (
            "duplicate_safe_response",
            ("diagnostics", "stages", 1, "safe_response"),
            contract["diagnostics"]["stages"][0]["safe_response"],
        ),
        (
            "retry_old_anchor_protocol",
            ("prior_evidence", "old_four_crash_anchor_protocol_retried"),
            True,
        ),
        ("discard_cf_d1", ("prior_evidence", "cf_d1_concurrency_retained"), False),
        ("next_opens_runtime", ("next_descendant", "runtime"), True),
        ("next_opens_database", ("next_descendant", "database_or_source"), True),
        ("next_opens_persistence", ("next_descendant", "persistence"), True),
        ("next_opens_provider", ("next_descendant", "provider_call"), True),
        ("next_opens_command", ("next_descendant", "command_or_write"), True),
    ]
    return [(name, _mutate(contract, path, value)) for name, path, value in cases]


def build_report() -> dict[str, Any]:
    contract = _load_json(CONTRACT_PATH)
    schema = _load_json(SCHEMA_PATH)
    api_contract = _load_yaml(API_SPINE_PATH)
    canonical_errors = validate_contract(contract, schema, api_contract)
    admitted_mutations = [
        name
        for name, mutation in hostile_mutations(contract)
        if not validate_contract(mutation, schema, api_contract)
    ]
    return {
        "status": "passed"
        if not canonical_errors and not admitted_mutations
        else "failed",
        "canonical_errors": canonical_errors,
        "hostile_mutation_count": len(hostile_mutations(contract)),
        "admitted_mutations": admitted_mutations,
        "diagnostic_stage_count": len(contract["diagnostics"]["stages"]),
        "runtime_started": False,
        "database_or_source_opened": False,
        "provider_calls": 0,
        "product_patient_or_clinical_data": False,
        "command_or_write": False,
    }


def main() -> int:
    report = build_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
