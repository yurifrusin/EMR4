from __future__ import annotations

import json
from pathlib import Path

from scripts.raisa_provider_free_cf_d2_observability_first_event_cue_acceptance import (
    API_SPINE_PATH,
    CONTRACT_PATH,
    EXPECTED_CUE_FIELDS,
    EXPECTED_DIAGNOSTIC_STAGES,
    EXPECTED_OPERATOR_EVIDENCE,
    EXPECTED_PROHIBITED_CONTENT,
    SCHEMA_PATH,
    _load_json,
    _load_yaml,
    build_report,
    hostile_mutations,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-cf-d2-observability-first-event-cue-plan.md"
ARCHITECTURE = (
    ROOT
    / "docs/raisa-provider-free-cf-d2-observability-first-event-cue-architecture.md"
)
THREAT = (
    ROOT
    / "docs"
    / "security"
    / "raisa-provider-free-cf-d2-observability-first-event-cue-threat-model-delta.md"
)
LATCH = ROOT / "orchestration/continuity/ariadne-active-operation-latch/current.json"


def _packet() -> tuple[dict, dict, dict]:
    return (
        _load_json(CONTRACT_PATH),
        _load_json(SCHEMA_PATH),
        _load_yaml(API_SPINE_PATH),
    )


def test_canonical_observability_contract_passes_without_runtime() -> None:
    report = build_report()

    assert report == {
        "status": "passed",
        "canonical_errors": [],
        "hostile_mutation_count": 39,
        "admitted_mutations": [],
        "diagnostic_stage_count": 10,
        "runtime_started": False,
        "database_or_source_opened": False,
        "provider_calls": 0,
        "product_patient_or_clinical_data": False,
        "command_or_write": False,
    }


def test_schema_is_closed_and_packet_is_valid() -> None:
    contract, schema, api_contract = _packet()

    assert schema["additionalProperties"] is False
    assert validate_contract(contract, schema, api_contract) == []
    assert all(
        definition.get("additionalProperties") is False
        for definition in schema["$defs"].values()
        if definition.get("type") == "object"
    )


def test_events_and_cues_are_non_authoritative_acceleration_hints() -> None:
    contract, _, _ = _packet()
    authority = contract["authority"]

    assert authority["source_owns_current_truth"] is True
    assert authority["event_is_acceleration_hint_only"] is True
    assert authority["cue_is_acceleration_hint_only"] is True
    assert authority["event_or_cue_may_assert_command_success"] is False
    assert authority["event_or_cue_may_grant_command_authority"] is False
    assert authority["consumer_must_fresh_read"] is True
    assert authority["command_must_recheck_current_authority_and_source_truth"] is True


def test_partition_has_one_logical_fenced_checkpoint_owner() -> None:
    contract, _, _ = _packet()
    partition = contract["partition"]

    assert partition["key_fields"] == [
        "source_system",
        "practice_scope_digest",
        "event_family",
    ]
    assert partition["logical_consumer_count"] == 1
    assert partition["initial_physical_consumers_per_database"] == 1
    assert partition["high_availability_mode"] == (
        "active_standby_external_lease_and_fencing"
    )
    assert partition["equal_checkpoint_writers_allowed"] is False


def test_checkpoint_requires_contiguous_receipt_and_atomic_obligation_not_delivery() -> (
    None
):
    contract, _, _ = _packet()
    position = contract["position"]

    assert position["coordinate_fields"] == ["source_epoch", "source_position"]
    assert position["checkpoint_requires_contiguous_terminal_receipts"] is True
    assert position["checkpoint_requires_atomic_required_obligation"] is True
    assert position["delivery_required_before_checkpoint"] is False
    assert position["gap_crossing_allowed"] is False


def test_terminal_classification_handles_duplicates_and_poison_events() -> None:
    contract, _, _ = _packet()
    classification = contract["classification"]

    assert set(classification["terminal_results"]) == {
        "cue_required",
        "suppressed_irrelevant",
        "rejected_unsupported",
    }
    assert classification["exactly_one_terminal_receipt_per_position"] is True
    assert classification["duplicate_returns_original_receipt"] is True
    assert classification["divergent_identity_result"] == "identity_conflict"
    assert classification["identity_conflict_advances_checkpoint"] is False
    assert classification["rejected_event_creates_obligation"] is False


def test_cue_is_minimal_payload_free_and_requires_fresh_read() -> None:
    contract, _, _ = _packet()
    cue = contract["cue_obligation"]

    assert set(cue["required_fields"]) == EXPECTED_CUE_FIELDS
    assert set(cue["prohibited_content"]) == EXPECTED_PROHIBITED_CONTENT
    assert cue["consumer_scope"] == "reception_one_diary_projection"
    assert cue["delivery_semantics"] == "at_least_once"
    assert cue["duplicate_policy"] == "reuse_original_obligation"
    assert cue["coalescing_policy"] == (
        "contiguous_pending_same_partition_consumer_and_reason_only"
    )
    assert cue["fresh_authorized_read_required"] is True


def test_lag_never_turns_unknown_or_epoch_mismatch_into_zero() -> None:
    contract, _, _ = _packet()
    lag = contract["lag"]

    assert set(lag["states"]) == {"exact", "unknown", "epoch_mismatch"}
    assert lag["exact_formula"] == "source_head_minus_checkpoint_within_same_epoch"
    assert lag["unknown_may_serialize_as_zero"] is False
    assert lag["epoch_mismatch_may_serialize_as_zero"] is False


def test_operator_diagnostics_are_stage_specific_and_discriminating() -> None:
    contract, _, _ = _packet()
    diagnostics = contract["diagnostics"]
    stages = diagnostics["stages"]

    assert {item["stage"] for item in stages} == EXPECTED_DIAGNOSTIC_STAGES
    assert len({item["observable"] for item in stages}) == len(stages)
    assert len({item["safe_response"] for item in stages}) == len(stages)
    assert diagnostics["generic_collapsed_failure_coordinate_allowed"] is False
    assert diagnostics["distinct_observable_per_stage_required"] is True
    assert diagnostics["distinct_safe_response_per_stage_required"] is True
    assert set(contract["retained_operator_evidence"]) == EXPECTED_OPERATOR_EVIDENCE


def test_reconciliation_uses_fresh_scoped_truth_and_cue_ack_is_narrow() -> None:
    contract, _, _ = _packet()
    reconciliation = contract["reconciliation"]

    assert reconciliation["cue_may_directly_update_display"] is False
    assert reconciliation["practice_role_resource_recheck_required"] is True
    assert reconciliation["fresh_scoped_read_required"] is True
    assert reconciliation["acknowledgement_meaning"] == "one_fresh_read_attempt_only"
    assert reconciliation["acknowledgement_confers_future_freshness"] is False


def test_api_spine_prototype_opens_no_route_or_runtime() -> None:
    _, _, api_contract = _packet()

    assert api_contract["artifact_kind"] == "non_invasive_async_architecture_contract"
    assert api_contract["status"] == "prototype_only_runtime_blocked"
    assert set(api_contract["closed_surfaces"].values()) == {"blocked"}
    assert api_contract["authority_boundary"]["event_is_current_truth"] is False
    assert api_contract["authority_boundary"]["cue_is_current_truth"] is False
    assert (
        api_contract["authority_boundary"][
            "consequential_mutation_requires_rest_command"
        ]
        is True
    )


def test_prior_durability_evidence_is_retained_without_retry() -> None:
    contract, _, _ = _packet()

    assert contract["prior_evidence"] == {
        "cf_d1_concurrency_retained": True,
        "stopped_cf_d2_attempts_remain_negative_evidence": True,
        "old_four_crash_anchor_protocol_retried": False,
        "workflow_evidence_led_gate_applied": True,
    }


def test_all_hostile_mutations_fail_closed() -> None:
    contract, schema, api_contract = _packet()
    admitted = [
        name
        for name, mutation in hostile_mutations(contract)
        if not validate_contract(mutation, schema, api_contract)
    ]

    assert len(hostile_mutations(contract)) == 39
    assert admitted == []


def test_next_descendant_remains_pure_provider_free_and_unmounted() -> None:
    contract, _, _ = _packet()

    assert contract["next_descendant"] == {
        "id": "provider-free-unmounted-event-cue-admission-rehearsal",
        "authored_synthetic_only": True,
        "pure_state_machine_only": True,
        "runtime": False,
        "database_or_source": False,
        "persistence": False,
        "provider_call": False,
        "command_or_write": False,
    }


def test_plan_documents_have_timestamp_and_exact_closed_boundary() -> None:
    for path in (PLAN, ARCHITECTURE, THREAT):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-13" in head
        assert "Timestamp: 2026-08-13T" in head
        assert "+10:00 (Australia/Brisbane)" in head

    plan = PLAN.read_text(encoding="utf-8").lower()
    for phrase in (
        "events are acceleration hints",
        "no watcher/listener/worker",
        "database/source",
        "operational retention",
        "product/patient/clinical data",
        "provider/adc",
        "command/write",
        "docs/branding/",
        "explicit-path only",
    ):
        assert phrase in plan


def test_active_latch_transferred_to_cf_d2_representation_descendant() -> None:
    latch = json.loads(LATCH.read_text(encoding="utf-8"))

    assert latch["status"] == "in_progress"
    assert latch["operation_id"] == (
        "raisa-provider-free-unmounted-cf-d2-event-cue-representation-architecture"
    )
    assert (
        "verify_representation_evidence_then_generate_precommit_receipt"
        in (latch["checkpoint"]["next_executable_stage"])
    )
    assert latch["terminal_response"]["permitted"] is False
