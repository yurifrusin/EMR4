from __future__ import annotations

from scripts.raisa_context_fabric_source_owned_truth_reorientation_acceptance import (
    CONTRACT_PATH,
    EXPECTED_OPERATIONS,
    EXPECTED_OUTCOMES,
    SCHEMA_PATH,
    _load,
    build_report,
    hostile_mutations,
    validate_contract,
)


def _packet() -> tuple[dict, dict]:
    return _load(CONTRACT_PATH), _load(SCHEMA_PATH)


def test_source_owned_truth_architecture_packet_passes_without_runtime() -> None:
    report = build_report()

    assert report["status"] == "passed"
    assert report["canonical_errors"] == []
    assert report["runtime_started"] is False
    assert report["database_opened"] is False
    assert report["provider_calls"] == 0
    assert report["product_or_patient_data"] is False


def test_schema_is_closed_and_contract_is_valid() -> None:
    contract, schema = _packet()

    assert schema["additionalProperties"] is False
    assert validate_contract(contract, schema) == []
    assert all(
        definition.get("additionalProperties") is False
        for definition in schema["$defs"].values()
        if definition.get("type") == "object"
    )


def test_events_are_only_acceleration_hints() -> None:
    contract, _ = _packet()
    event = contract["authority_planes"]["event_watcher"]

    assert event == {
        "authority": "acceleration_hint_only",
        "fresh_authorized_read_required": True,
        "may_assert_current_truth": False,
        "may_assert_command_success": False,
    }
    assert (
        contract["authority_planes"]["authoritative_source"]
        ["depends_on_cue_delivery_for_correctness"]
        is False
    )


def test_freshness_confirmation_idempotency_and_audit_are_distinct() -> None:
    contract, _ = _packet()
    packet = contract["conditional_command_packet"]

    assert packet["precondition_owner"] == "backend_command_service"
    assert packet["client_may_mint_or_amend"] is False
    assert packet["token_alone_closes_toctou"] is False
    assert set(packet["separate_evidence"]) == {
        "human_or_policy_confirmation",
        "idempotency_identity",
        "audit_attribution",
    }


def test_create_fences_the_conflict_domain_and_other_operations_lock_rows() -> None:
    contract, _ = _packet()
    operations = {item["operation"]: item for item in contract["operation_families"]}

    assert set(operations) == EXPECTED_OPERATIONS
    assert operations["create"]["target_row_exists_before_command"] is False
    assert operations["create"]["required_serialization"] == "schedule_conflict_domain_fence"
    assert "database_constraint" in operations["create"]["required_rechecks"]
    assert all(
        operations[name]["target_row_exists_before_command"]
        for name in ("update", "status", "delete")
    )


def test_only_commit_mutates_and_only_replay_returns_original_receipt() -> None:
    contract, _ = _packet()
    outcomes = {item["code"]: item for item in contract["outcomes"]}

    assert set(outcomes) == EXPECTED_OUTCOMES
    assert {code for code, item in outcomes.items() if item["mutation"]} == {"committed"}
    assert {
        code for code, item in outcomes.items() if item["returns_original_receipt"]
    } == {"idempotent_replay"}


def test_legacy_routes_converge_without_equating_freshness_and_confirmation() -> None:
    contract, _ = _packet()
    legacy = contract["legacy_compatibility_migration"]

    assert legacy["current_behavior_changed_by_this_contract"] is False
    assert legacy["target_kernel"] == "single_backend_conditional_command_kernel"
    assert legacy["implicit_freshness_is_human_confirmation"] is False
    assert legacy["retirement_requires_client_parity"] is True


def test_durable_cue_delivery_is_deferred_not_abandoned() -> None:
    contract, _ = _packet()
    durability = contract["deferred_durable_event_and_cue_delivery"]

    assert durability["status"] == "named_future_extension_not_abandoned"
    assert durability["command_authority"] is False
    assert durability["current_truth_authority"] is False
    assert durability["cf_d1_evidence_retained"] is True
    assert durability["cf_d2_reopen_policy"] == "fresh_observability_first_plan_only"
    assert durability["consumer_topology"] == {
        "logical_consumers_per_partition": 1,
        "initial_physical_processes_per_database": 1,
        "high_availability_mode": "active_standby_with_external_fencing",
        "equal_checkpoint_writers_per_partition": False,
        "duplicate_delivery_policy": "idempotent_at_least_once",
    }


def test_all_hostile_mutations_fail_closed() -> None:
    contract, schema = _packet()
    admitted = [
        name
        for name, mutation in hostile_mutations(contract)
        if not validate_contract(mutation, schema)
    ]

    assert len(hostile_mutations(contract)) == 28
    assert admitted == []


def test_next_descendant_remains_provider_free_and_unmounted() -> None:
    contract, _ = _packet()

    assert contract["next_descendant"] == {
        "id": "provider-free-unmounted-conditional-command-admission-rehearsal",
        "authored_synthetic_only": True,
        "runtime": False,
        "database": False,
        "route_change": False,
        "provider_call": False,
        "command_or_write": False,
    }
