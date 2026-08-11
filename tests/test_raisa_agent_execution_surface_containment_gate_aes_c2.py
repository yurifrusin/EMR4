"""Focused defensive tests for the AES-C2 provider-free broker simulator."""

from __future__ import annotations

import copy
import json

from scripts.raisa_agent_execution_surface_containment_gate_aes_c0_acceptance import (
    validate_instance,
)
from scripts.raisa_agent_execution_surface_containment_gate_aes_c1_admission import (
    digest_of,
)
from scripts.raisa_agent_execution_surface_containment_gate_aes_c2_broker_simulator import (
    ADAPTER_ARTIFACT_DIGEST,
    BROKER_REGISTRY_ENTRY,
    CONTRACT_PATH,
    IMPLEMENTATION_DEFINITION,
    IMPLEMENTATION_DEFINITION_DIGEST,
    INHERITED_ARTIFACT_DIGESTS,
    SCENARIOS_PATH,
    SCENARIO_EXPECTATIONS,
    SCHEMA_PATH,
    SYNTHETIC_FIXTURE_HANDLE,
    SYNTHETIC_FIXTURE_VALUE,
    _hostile_contract_mutations,
    _hostile_mutations,
    _load,
    build_report,
    evaluate_simulation_attempt,
    generate_scenarios,
    static_boundary_check,
    validate_attempt,
    validate_contract,
    validate_hostile_contract_mutations,
    validate_hostile_mutations,
    validate_scenario_packet,
)
import scripts.raisa_agent_execution_surface_containment_gate_aes_c2_broker_simulator as c2_module


def _packet() -> tuple[dict, dict, dict]:
    return _load(CONTRACT_PATH), _load(SCHEMA_PATH), _load(SCENARIOS_PATH)


def _all_scenarios() -> dict[str, dict]:
    _, _, packet = _packet()
    return {scenario["scenario_id"]: scenario for scenario in packet["scenarios"]}


def test_aes_c2_report_passes_with_zero_runtime_provider_or_data() -> None:
    report = build_report()

    assert report["status"] == "passed"
    assert report["reasons"] == []
    assert report["scenario_count"] == 26
    assert report["simulated_count"] == 2
    assert report["not_dispatched_count"] == 4
    assert report["stop_count"] == 20
    assert report["simulated_inert_invocation_count"] == 3
    assert report["runtime_started"] is False
    assert report["provider_calls"] == 0
    assert report["real_adapters_executed"] == 0
    assert report["network_operations"] == 0
    assert report["database_operations"] == 0
    assert report["source_operations"] == 0
    assert report["filesystem_operations"] == 0
    assert report["executable_or_tool_operations"] == 0
    assert report["command_operations"] == 0
    assert report["real_credentials_used"] is False
    assert report["product_or_patient_data"] is False
    assert report["mutation_admitted"] == []
    assert report["mutation_rejected_count"] == len(_hostile_mutations())
    assert report["contract_mutation_admitted"] == []
    assert report["contract_mutation_rejected_count"] == len(
        _hostile_contract_mutations()
    )


def test_aes_c2_inherited_aes_c1_digests_match_frozen_hashes() -> None:
    contract, _, _ = _packet()

    assert contract["inherited_artifact_digests"] == INHERITED_ARTIFACT_DIGESTS
    assert INHERITED_ARTIFACT_DIGESTS == {
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/admission-rehearsal-contract.json": (
            "sha256:241f081b1c3346ef50e80eb495c9bfb6ea3b99f67956b439c7c7638962069f90"
        ),
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/admission-rehearsal-contract.schema.json": (
            "sha256:2e6c5b83d379f5b6f900fa0a26a8733b6fe09496ff8e1c52d5ed40123603e9b6"
        ),
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/authored-synthetic-admission-scenarios.json": (
            "sha256:e6e427efa32fb27387598042f0d1b1f19c4472b09288f7c8d3ed321a7309945c"
        ),
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/provider-free-admission-evidence.json": (
            "sha256:f7d1a2f60ef4b6f46242cfff7a12b36b6e20405a07ad788854c877851a0bbd4c"
        ),
        "scripts/raisa_agent_execution_surface_containment_gate_aes_c1_admission.py": (
            "sha256:4407646c98dee84e8ef4210b0e06aa500178b5a2e2094ca02003b43fbf0acda6"
        ),
    }


def test_aes_c2_contract_and_packet_are_closed_and_exact() -> None:
    contract, schema, packet = _packet()

    assert validate_contract(contract, schema) == []
    assert schema["additionalProperties"] is False
    assert len(packet["scenarios"]) == 26
    ids = [scenario["scenario_id"] for scenario in packet["scenarios"]]
    assert len(set(ids)) == 26
    assert set(ids) == set(SCENARIO_EXPECTATIONS)
    assert len(contract["broker_registry"]["entries"]) == 1
    assert len(contract["reason_vocabulary"]) == 12
    assert len(contract["status_vocabulary"]) == 3


def test_aes_c2_all_26_scenarios_match_expected_status_reason_and_calls() -> None:
    by_id = _all_scenarios()

    assert set(by_id) == set(SCENARIO_EXPECTATIONS)
    for scenario_id, (status, reasons, calls) in SCENARIO_EXPECTATIONS.items():
        result = evaluate_simulation_attempt(by_id[scenario_id])
        assert result["status"] == status, scenario_id
        assert result["reason_codes"] == reasons, scenario_id
        assert result["simulated_invocation_count"] == calls, scenario_id
        assert result["released_simulated_result"] == (status == "simulated"), (
            scenario_id
        )


def test_aes_c2_registry_has_exactly_one_entry_and_identity_is_broker_resolved() -> (
    None
):
    contract, _, _ = _packet()
    registry = contract["broker_registry"]
    entries = registry["entries"]

    assert len(entries) == 1
    entry = entries[0]
    assert entry == BROKER_REGISTRY_ENTRY
    assert entry["capability_class"] == "inert_tool_adapter"
    assert entry["capability_id"] == "capability-synthetic-inert"
    assert entry["adapter_id"] == "synthetic-inert-adapter"
    assert entry["operation_id"] == "render-inert-adapter"
    assert entry["destination_id"] == "synthetic-inert-destination"
    assert entry["method"] == "POST"
    assert entry["media_type"] == "application/json"
    assert entry["source_class"] == "authored_synthetic"
    assert entry["implementation_id"] == "aes-c2-pure-inert-render-v1"
    assert entry["effect_class"] == "none"
    assert entry["external_io"] is False
    assert entry["command_authority"] is False


def test_aes_c2_two_digest_layers_are_independent_and_exact() -> None:
    contract, _, _ = _packet()
    entry = contract["broker_registry"]["entries"][0]

    # Inherited C1 adapter-artifact identity: sha256: plus 64 f characters.
    assert entry["adapter_artifact_digest"] == ADAPTER_ARTIFACT_DIGEST
    assert ADAPTER_ARTIFACT_DIGEST == "sha256:" + "f" * 64

    # Independently recomputed C2 implementation-definition digest.
    assert entry["implementation_definition_digest"] == IMPLEMENTATION_DEFINITION_DIGEST
    assert IMPLEMENTATION_DEFINITION_DIGEST == digest_of(IMPLEMENTATION_DEFINITION)

    # No equality or preimage relation between the two layers.
    assert entry["adapter_artifact_digest"] != entry["implementation_definition_digest"]
    assert digest_of(IMPLEMENTATION_DEFINITION) != ADAPTER_ARTIFACT_DIGEST


def test_aes_c2_work_cell_never_receives_registry_lease_or_credential() -> None:
    by_id = _all_scenarios()

    for scenario_id, scenario in by_id.items():
        view = scenario["work_cell_view"]
        serialized = json.dumps(view, sort_keys=True)
        assert "capability_lease" not in serialized, scenario_id
        assert "broker_registry" not in serialized, scenario_id
        assert SYNTHETIC_FIXTURE_HANDLE not in serialized, scenario_id
        assert SYNTHETIC_FIXTURE_VALUE not in serialized, scenario_id
        result = evaluate_simulation_attempt(scenario)
        assert (
            result["boundary_assertions"]["work_cell_received_lease_or_registry"]
            is False
        )
        assert (
            result["boundary_assertions"]["work_cell_received_credential_fixture"]
            is False
        )
        assert (
            result["boundary_assertions"]["candidate_selected_operation_identity"]
            is False
        )
        assert result["boundary_assertions"]["command_authority"] is False
        assert result["contains_sensitive_values"] is False


def test_aes_c2_fixture_handle_and_value_never_occur_in_results_or_evidence() -> None:
    report = build_report()

    def occurs(value):
        if isinstance(value, str):
            return SYNTHETIC_FIXTURE_HANDLE in value or SYNTHETIC_FIXTURE_VALUE in value
        if isinstance(value, dict):
            return any(occurs(v) for v in value.values())
        if isinstance(value, list):
            return any(occurs(v) for v in value)
        return False

    assert not occurs(report)
    for result in report["scenario_results"]:
        assert not occurs(result)
    # The fixture value is not usable as a real credential and is not a secret.
    assert SYNTHETIC_FIXTURE_VALUE.startswith("synthetic-noncredential-fixture:")
    assert SYNTHETIC_FIXTURE_HANDLE.startswith("synthetic-noncredential-fixture:")


def test_aes_c2_all_hostile_mutations_fail_closed_with_zero_release() -> None:
    rejected, admitted = validate_hostile_mutations()

    assert len(_hostile_mutations()) == 18
    assert len(rejected) == 18
    assert admitted == []


def test_aes_c2_all_hostile_contract_mutations_fail_closed() -> None:
    rejected, admitted = validate_hostile_contract_mutations()

    assert len(_hostile_contract_mutations()) == 14
    assert len(rejected) == 14
    assert admitted == []


def test_aes_c2_contract_rejects_undeclared_nested_rules_and_changed_digests() -> None:
    contract, schema, _ = _packet()

    inherited_changed = copy.deepcopy(contract)
    inherited_key = next(iter(inherited_changed["inherited_artifact_digests"]))
    inherited_changed["inherited_artifact_digests"][inherited_key] = (
        "sha256:" + "9" * 64
    )
    assert validate_contract(inherited_changed, schema)

    registry_adapter_changed = copy.deepcopy(contract)
    registry_adapter_changed["broker_registry"]["entries"][0]["adapter_id"] = "other"
    assert validate_contract(registry_adapter_changed, schema)

    precedence_changed = copy.deepcopy(contract)
    precedence_changed["dispatch_precedence"][0] = "0_forged_precedence"
    assert validate_contract(precedence_changed, schema)

    custody_policy_extra = copy.deepcopy(contract)
    custody_policy_extra["synthetic_custody_policy"]["forged_policy"] = True
    assert validate_contract(custody_policy_extra, schema)

    zero_runtime_opened = copy.deepcopy(contract)
    zero_runtime_opened["zero_runtime_boundary"]["runtime_started"] = True
    assert validate_contract(zero_runtime_opened, schema)

    digest_rules_extra = copy.deepcopy(contract)
    digest_rules_extra["digest_rules"]["forged_rule"] = {"forged": True}
    assert validate_contract(digest_rules_extra, schema)


def test_aes_c2_invocation_and_result_digests_are_independent() -> None:
    by_id = _all_scenarios()
    report = build_report()
    results = {r["scenario_id"]: r for r in report["scenario_results"]}

    simulated = [
        s
        for s in by_id.values()
        if s["scenario_id"]
        in (
            "exact-inert-dispatch-simulated",
            "exact-inert-second-within-budget-simulated",
        )
    ]
    assert len(simulated) == 2
    for scenario in simulated:
        result = results[scenario["scenario_id"]]
        assert result["invocation_digest"] is not None
        assert result["result_digest"] is not None
        assert result["invocation_digest"] != result["result_digest"]
        assert (
            result["implementation_definition_digest"]
            == IMPLEMENTATION_DEFINITION_DIGEST
        )
        assert result["adapter_artifact_identity_digest"] == ADAPTER_ARTIFACT_DIGEST


def test_aes_c2_static_boundary_check_finds_no_external_effect_path() -> None:
    assert static_boundary_check() == []


def test_aes_c2_every_scenario_attempt_is_closed_and_validates() -> None:
    _, schema, packet = _packet()
    for scenario in packet["scenarios"]:
        assert validate_attempt(scenario) == [], scenario["scenario_id"]
        result = evaluate_simulation_attempt(scenario)
        assert (
            validate_instance(
                result,
                schema["$defs"]["BrokerSimulationResult"],
                root_schema=schema,
            )
            == []
        ), scenario["scenario_id"]


def test_aes_c2_regenerated_packet_is_stable() -> None:
    current = _load(SCENARIOS_PATH)
    regenerated = generate_scenarios()

    assert [s["scenario_id"] for s in regenerated["scenarios"]] == [
        s["scenario_id"] for s in current["scenarios"]
    ]
    for scenario in regenerated["scenarios"]:
        scenario_id = scenario["scenario_id"]
        expected = SCENARIO_EXPECTATIONS[scenario_id]
        result = evaluate_simulation_attempt(scenario)
        assert result["status"] == expected[0]
        assert result["reason_codes"] == expected[1]
        assert result["simulated_invocation_count"] == expected[2]


def test_aes_c2_work_cell_custody_exposure_stops_with_zero_release() -> None:
    by_id = _all_scenarios()
    scenario = by_id["work-cell-custody-exposure-stop"]

    assert scenario["work_cell_view"].get("credential_reference") is not None
    result = evaluate_simulation_attempt(scenario)
    assert result["status"] == "stop"
    assert result["reason_codes"] == ["credential_custody_violation"]
    assert result["simulated_invocation_count"] == 0
    assert result["released_simulated_result"] is False


def test_aes_c2_repeat_after_terminal_stops_before_invocation() -> None:
    by_id = _all_scenarios()
    scenario = by_id["repeat-after-terminal-stop"]

    assert (
        scenario["broker_admission_attempt"]["budget_state"]["next_operation_permitted"]
        is False
    )
    result = evaluate_simulation_attempt(scenario)
    assert result["status"] == "stop"
    assert result["reason_codes"] == ["generation_terminal"]
    assert result["simulated_invocation_count"] == 0
    assert result["released_simulated_result"] is False


def test_aes_c2_malformed_result_calls_once_and_releases_nothing() -> None:
    by_id = _all_scenarios()
    scenario = by_id["adapter-result-contract-mismatch-stop"]
    result = evaluate_simulation_attempt(scenario)

    assert result["status"] == "stop"
    assert result["reason_codes"] == ["adapter_result_invalid"]
    assert result["simulated_invocation_count"] == 1
    assert result["released_simulated_result"] is False


def _count_pure_adapter_calls(attempt) -> tuple[list, dict]:
    """Run one attempt with a counting wrapper on the real pure adapter."""
    calls: list = []
    original = c2_module._pure_inert_render

    def counting(invocation, fixture_value):
        calls.append(invocation)
        return original(invocation, fixture_value)

    c2_module._pure_inert_render = counting
    try:
        result = evaluate_simulation_attempt(attempt)
    finally:
        c2_module._pure_inert_render = original
    return calls, result


def test_aes_c2_malformed_result_executes_pure_adapter_exactly_once() -> None:
    by_id = _all_scenarios()
    scenario = by_id["adapter-result-contract-mismatch-stop"]
    calls, result = _count_pure_adapter_calls(scenario)

    assert len(calls) == 1
    assert result["status"] == "stop"
    assert result["reason_codes"] == ["adapter_result_invalid"]
    assert result["simulated_invocation_count"] == 1
    assert result["released_simulated_result"] is False


def test_aes_c2_schema_valid_override_cannot_bypass_actual_pure_call() -> None:
    """A schema-valid override still executes the real pure adapter exactly once."""
    by_id = _all_scenarios()
    scenario = copy.deepcopy(by_id["exact-inert-dispatch-simulated"])
    admission = scenario["broker_admission_attempt"]
    c1 = c2_module.evaluate_attempt(admission)
    admitted_candidate_digest = c1["broker_decision"]["candidate_digest"]
    invocation = c2_module._build_invocation(scenario, admitted_candidate_digest)
    invocation_digest = digest_of(invocation)
    result_payload = {
        "result_code": "inert-render-ok",
        "invocation_digest": invocation_digest,
    }
    result_digest = digest_of(result_payload)
    scenario["adapter_result_override"] = {
        "schema_version": "emr4.aes_c2.adapter_result.v1",
        "result_id": "result-schema-valid-override",
        "result_code": "inert-render-ok",
        "invocation_digest": invocation_digest,
        "result_digest": result_digest,
        "command_authority": False,
        "effect_class": "none",
        "contains_sensitive_values": False,
    }

    calls, result = _count_pure_adapter_calls(scenario)

    # The actual pure adapter still executes exactly once; the override cannot
    # bypass the call.  A schema-valid override alone would otherwise release a
    # simulated result, which is exactly why packet validation must reject it.
    assert len(calls) == 1
    assert result["status"] == "simulated"
    assert result["released_simulated_result"] is True
    assert result["simulated_invocation_count"] == 1

    # The same override on a non-malformed scenario fails packet validation.
    packet = copy.deepcopy(_packet()[2])
    for i, s in enumerate(packet["scenarios"]):
        if s["scenario_id"] == "exact-inert-dispatch-simulated":
            packet["scenarios"][i] = scenario
            break
    errors = validate_scenario_packet(packet, _packet()[1])
    assert (
        "scenarios:adapter_result_override_outside_exact_malformed_scenario" in errors
    )
    assert "scenarios:not_canonical_generated_catalogue" in errors


def test_aes_c2_all_26_scenarios_execute_pure_adapter_exactly_three_times() -> None:
    _, _, packet = _packet()
    calls: list = []
    original = c2_module._pure_inert_render

    def counting(invocation, fixture_value):
        calls.append(invocation)
        return original(invocation, fixture_value)

    c2_module._pure_inert_render = counting
    try:
        for scenario in packet["scenarios"]:
            evaluate_simulation_attempt(scenario)
    finally:
        c2_module._pure_inert_render = original

    # Two released simulations plus one malformed result with no release.
    assert len(calls) == 3


def test_aes_c2_packet_rejects_extra_key_and_noncanonical_scenario() -> None:
    _, schema, packet = _packet()

    # Undeclared top-level packet key is rejected.
    extra_key = copy.deepcopy(packet)
    extra_key["forged_field"] = "forged"
    errors = validate_scenario_packet(extra_key, schema)
    assert "scenarios:keys_not_exact" in errors

    # Missing top-level packet key is rejected.
    missing_key = copy.deepcopy(packet)
    del missing_key["evidence_mode"]
    errors = validate_scenario_packet(missing_key, schema)
    assert "scenarios:keys_not_exact" in errors
    assert "scenarios:evidence_mode" in errors

    # Noncanonical scenario value (tampered malformed result code) is rejected.
    noncanonical = copy.deepcopy(packet)
    for scenario in noncanonical["scenarios"]:
        if scenario["scenario_id"] == "adapter-result-contract-mismatch-stop":
            scenario["adapter_result_override"]["result_code"] = "forged-code"
            break
    errors = validate_scenario_packet(noncanonical, schema)
    assert "scenarios:not_canonical_generated_catalogue" in errors
    assert errors
