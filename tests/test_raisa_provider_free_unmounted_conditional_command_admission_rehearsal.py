from __future__ import annotations

from scripts.raisa_provider_free_unmounted_conditional_command_admission_rehearsal import (
    EXPECTED_CONTRACT_HASH,
    EXPECTED_OPERATIONS,
    EXPECTED_OUTCOMES,
    SCENARIOS_PATH,
    SCHEMA_PATH,
    _file_hash,
    _load,
    build_report,
    evaluate_scenario,
    hostile_mutations,
    validate_packet,
    ARCHITECTURE_CONTRACT_PATH,
)


def _packet() -> tuple[dict, dict]:
    return _load(SCENARIOS_PATH), _load(SCHEMA_PATH)


def _results() -> dict[str, dict]:
    packet, _ = _packet()
    return {
        scenario["id"]: evaluate_scenario(scenario)
        for scenario in packet["scenarios"]
    }


def test_rehearsal_passes_without_any_effect_surface() -> None:
    report = build_report()

    assert report["status"] == "passed"
    assert report["canonical_errors"] == []
    assert report["scenario_count"] == 37
    assert report["admission_rejected_count"] == 19
    assert set(report["effect_boundary"].values()) <= {False, 0}


def test_packet_is_closed_and_binds_the_exact_architecture_contract() -> None:
    packet, schema = _packet()

    assert schema["additionalProperties"] is False
    assert validate_packet(packet, schema) == []
    assert _file_hash(ARCHITECTURE_CONTRACT_PATH) == EXPECTED_CONTRACT_HASH
    assert packet["contract_binding"]["contract_sha256"] == EXPECTED_CONTRACT_HASH


def test_all_operation_and_outcome_families_are_exercised() -> None:
    packet, _ = _packet()
    results = _results().values()

    assert {scenario["operation"] for scenario in packet["scenarios"]} == EXPECTED_OPERATIONS
    assert {result["outcome"] for result in results if result["outcome"]} == EXPECTED_OUTCOMES


def test_only_committed_plans_a_mutation_and_no_effect_is_performed() -> None:
    results = _results().values()

    assert all(
        result["planned_mutation"] == (result["outcome"] == "committed")
        for result in results
    )
    assert all(result["effect_performed"] is False for result in results)
    assert all(
        result["receipt_disposition"] == "planned_new_receipt"
        for result in results
        if result["outcome"] == "committed"
    )


def test_replay_returns_only_the_original_receipt_reference() -> None:
    results = _results()

    assert results["ccar-005-idempotent-replay"]["receipt_disposition"] == (
        "original_receipt_reference"
    )
    assert results["ccar-035-replay-before-stale"]["receipt_disposition"] == (
        "original_receipt_reference"
    )
    assert all(
        (result["receipt_disposition"] == "original_receipt_reference")
        == (result["outcome"] == "idempotent_replay")
        for result in results.values()
    )


def test_create_requires_fence_and_existing_operations_require_target_lock() -> None:
    results = _results()

    assert results["ccar-025-create-missing-fence"]["reason_codes"] == [
        "lock_plan_invalid"
    ]
    assert results["ccar-026-update-missing-lock"]["reason_codes"] == [
        "lock_plan_invalid"
    ]
    assert results["ccar-027-status-extra-schedule-lock"]["reason_codes"] == [
        "lock_plan_invalid"
    ]
    assert results["ccar-028-reordered-locks"]["reason_codes"] == [
        "lock_plan_invalid"
    ]


def test_events_are_rejected_as_truth_or_success_evidence() -> None:
    results = _results()

    assert results["ccar-031-event-claims-truth"]["reason_codes"] == [
        "event_cannot_assert_current_truth"
    ]
    assert results["ccar-032-event-claims-success"]["reason_codes"] == [
        "event_cannot_assert_command_success"
    ]
    assert results["ccar-031-event-claims-truth"]["outcome"] is None
    assert results["ccar-032-event-claims-success"]["outcome"] is None


def test_frozen_precedence_prevents_receipt_or_state_disclosure_drift() -> None:
    results = _results()

    assert results["ccar-010-authority-before-replay"]["outcome"] == "authority_revoked"
    assert results["ccar-033-authority-before-stale"]["outcome"] == "authority_revoked"
    assert results["ccar-034-confirmation-before-stale"]["outcome"] == (
        "confirmation_required"
    )
    assert results["ccar-035-replay-before-stale"]["outcome"] == "idempotent_replay"
    assert results["ccar-036-stale-before-conflict"]["outcome"] == "stale_precondition"
    assert results["ccar-037-conflict-before-validation"]["outcome"] == (
        "schedule_conflict"
    )


def test_structural_rejection_never_produces_a_command_outcome() -> None:
    results = _results().values()

    rejected = [result for result in results if result["admission"] == "admission_rejected"]
    assert len(rejected) == 19
    assert all(result["outcome"] is None for result in rejected)
    assert all(result["receipt_disposition"] == "none" for result in rejected)


def test_all_hostile_mutations_fail_closed() -> None:
    packet, schema = _packet()
    admitted = [
        name
        for name, mutation in hostile_mutations(packet)
        if not validate_packet(mutation, schema)
    ]

    assert len(hostile_mutations(packet)) == 32
    assert admitted == []
