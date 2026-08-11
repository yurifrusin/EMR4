from __future__ import annotations

from scripts.raisa_agent_execution_surface_containment_gate_aes_c0_acceptance import (
    ALWAYS_DENIED,
    BUDGET_DIMENSIONS,
    CONTRACT_PATH,
    EXAMPLES_PATH,
    LEASEABLE_CLASSES,
    MESSAGE_DEFS,
    SCHEMA_PATH,
    _load,
    build_report,
    hostile_mutations,
    validate_contract,
    validate_examples,
    validate_hostile_mutations,
)


def _packet() -> tuple[dict, dict, dict]:
    return _load(CONTRACT_PATH), _load(SCHEMA_PATH), _load(EXAMPLES_PATH)


def test_aes_c0_canonical_packet_passes_without_runtime_or_data() -> None:
    report = build_report()

    assert report["status"] == "passed"
    assert report["canonical_error_count"] == 0
    assert report["runtime_started"] is False
    assert report["provider_calls"] == 0
    assert report["product_or_patient_data"] is False


def test_aes_c0_schema_and_all_six_messages_are_closed_and_valid() -> None:
    contract, schema, examples = _packet()

    assert schema["additionalProperties"] is False
    assert set(examples["messages"]) == set(MESSAGE_DEFS)
    assert all(
        schema["$defs"][definition]["additionalProperties"] is False
        for definition in MESSAGE_DEFS.values()
    )
    assert validate_contract(contract, schema) == []
    assert validate_examples(examples, contract, schema) == []


def test_aes_c0_work_cell_has_no_ambient_or_command_authority() -> None:
    contract, _, _ = _packet()

    assert set(contract["authority_boundary"].values()) == {False}
    assert all(
        boundary["model_controls_boundary"] is False
        for boundary in contract["trust_boundaries"]
    )
    assert {
        item["class_id"] for item in contract["capability_classes"]["leaseable"]
    } == LEASEABLE_CLASSES
    assert set(contract["capability_classes"]["always_denied"]) == ALWAYS_DENIED
    assert (
        contract["generation_manifest_policy"][
            "work_cell_receives_lease_or_credential"
        ]
        is False
    )


def test_aes_c0_candidate_content_cannot_choose_operation_identity() -> None:
    contract, _, _ = _packet()
    policy = contract["candidate_influence_policy"]

    assert policy["context_and_memory_are_inert"] is True
    assert {
        "capability_id",
        "adapter_id",
        "operation_id",
        "destination_id",
        "url",
        "method",
        "credential",
        "filesystem_path",
        "sql",
        "executable",
        "tool_definition",
        "command_route",
        "cleanup_target",
        "policy_amendment",
    } <= set(policy["candidate_must_not_supply"])
    assert set(policy["broker_must_resolve"]).isdisjoint(
        policy["candidate_may_supply"]
    )


def test_aes_c0_budgets_are_cumulative_and_command_ceiling_is_zero() -> None:
    contract, _, examples = _packet()
    policy = contract["budget_policy"]
    dimensions = {
        item["dimension"]: set(item["counters"]) for item in policy["dimensions"]
    }

    assert dimensions == BUDGET_DIMENSIONS
    assert all(item["cumulative"] is True for item in policy["dimensions"])
    assert policy["maximum_redirects_per_generation"] == 0
    assert policy["maximum_product_mutations_per_generation"] == 0
    assert policy["maximum_command_confirmations_per_generation"] == 0
    budget = examples["messages"]["budget_state"]
    assert budget["terminal_state"] == "exhausted"
    assert budget["next_operation_permitted"] is False


def test_aes_c0_preserves_api_spine_and_no_fallback_boundary() -> None:
    contract, _, _ = _packet()
    routes = contract["route_classification"]
    fallback = contract["fallback_policy"]

    assert routes["graphql_query"]["command_authority"] is False
    assert routes["event_signal"]["current_truth"] is False
    assert routes["event_signal"]["fresh_authorized_read_required"] is True
    command = routes["rest_openapi_command"]
    assert command["broker_may_confirm_command"] is False
    assert command["current_authorization_required"] is True
    assert command["human_or_policy_gate_required"] is True
    assert command["idempotency_required"] is True
    assert command["audit_required"] is True
    assert command["deterministic_readback_required"] is True
    assert fallback["provider_unavailable_state"] == "intelligence_unavailable"
    assert fallback["silent_provider_fallback"] is False
    assert fallback["silent_model_fallback"] is False
    assert fallback["deterministic_equivalent_intelligence_fallback"] is False


def test_aes_c0_revocation_and_evidence_are_external_and_minimized() -> None:
    contract, _, examples = _packet()
    revocation = contract["revocation_and_kill_switch"]
    evidence_policy = contract["audit_evidence_policy"]

    assert revocation["owner"] == "external_control_plane"
    assert revocation["model_may_disable_or_delay"] is False
    assert revocation["suspected_escape_reuses_work_cell"] is False
    evidence = examples["messages"]["audit_evidence"]
    assert set(evidence) == set(evidence_policy["allowed_fields"])
    assert evidence["contains_sensitive_values"] is False
    assert {
        "raw_prompt",
        "model_reasoning",
        "credential",
        "patient_or_product_value",
        "unrestricted_log",
    } <= set(evidence_policy["forbidden_fields"])


def test_aes_c0_all_hostile_mutations_fail_closed() -> None:
    contract, schema, examples = _packet()
    rejected, admitted = validate_hostile_mutations(contract, examples, schema)

    assert len(hostile_mutations()) == 37
    assert len(rejected) == 37
    assert admitted == []


def test_aes_c1_handoff_remains_provider_free_and_unmounted() -> None:
    contract, _, _ = _packet()

    assert contract["next_descendant"] == {
        "id": "aes-c1-provider-free-admission-rehearsal",
        "runtime": False,
        "provider_call": False,
        "product_or_patient_data": False,
        "tool_or_command": False,
        "requires_fresh_frozen_plan": True,
    }
