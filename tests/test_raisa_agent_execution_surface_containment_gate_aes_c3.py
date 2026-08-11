"""Focused defensive tests for the AES-C3 provider-free hostile containment."""

from __future__ import annotations

import copy
import json

from scripts.raisa_agent_execution_surface_containment_gate_aes_c0_acceptance import (
    validate_instance,
)
from scripts.raisa_agent_execution_surface_containment_gate_aes_c3_hostile_containment import (
    CONTRACT_PATH,
    CURRENT_BUREAU_ID,
    CURRENT_GENERATION_ID,
    CURRENT_MANIFEST_DIGEST,
    CURRENT_MANIFEST_ID,
    CURRENT_WORK_CELL_ID,
    INHERITED_ARTIFACT_DIGESTS,
    MUTATION_ID_VOCABULARY,
    REPLAY_BINDING_FIELDS,
    SCENARIOS_PATH,
    SCENARIO_EXPECTATIONS,
    SCHEMA_PATH,
    STATUS_VOCABULARY,
    _hostile_contract_mutations,
    _hostile_mutations,
    _base_c2_attempt,
    _load,
    build_report,
    evaluate_attempt,
    generate_scenarios,
    static_boundary_check,
    validate_attempt,
    validate_contract,
    validate_hostile_contract_mutations,
    validate_hostile_mutations,
)
import scripts.raisa_agent_execution_surface_containment_gate_aes_c2_broker_simulator as c2_module
import scripts.raisa_agent_execution_surface_containment_gate_aes_c3_hostile_containment as c3_module


def _packet() -> tuple[dict, dict, dict]:
    return _load(CONTRACT_PATH), _load(SCHEMA_PATH), _load(SCENARIOS_PATH)


def _all_scenarios() -> dict[str, dict]:
    _, _, packet = _packet()
    return {scenario["scenario_id"]: scenario for scenario in packet["scenarios"]}


def test_aes_c3_report_passes_with_zero_runtime_provider_or_data() -> None:
    report = build_report()

    assert report["status"] == "passed"
    assert report["reasons"] == []
    assert report["scenario_count"] == 61
    assert report["contained_count"] == 21
    assert report["reject_count"] == 15
    assert report["stop_count"] == 25
    assert report["pure_python_call_count"] == 28
    assert report["digest_only_release_count"] == 21
    assert report["opaque_payload_non_release"] is True
    assert report["raw_payload_leak_scenarios"] == []
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


def test_aes_c3_inherited_digests_match_frozen_hashes() -> None:
    contract, _, _ = _packet()

    assert contract["inherited_artifact_digests"] == INHERITED_ARTIFACT_DIGESTS
    assert len(INHERITED_ARTIFACT_DIGESTS) == 11
    assert (
        INHERITED_ARTIFACT_DIGESTS[
            "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c2/broker-simulator-contract.json"
        ]
        == "sha256:530c9c3067725f6078785e846fa82c0ebb89f72d0a8feeb5c2916d567b5a4ccf"
    )
    assert (
        INHERITED_ARTIFACT_DIGESTS[
            "scripts/raisa_agent_execution_surface_containment_gate_aes_c2_broker_simulator.py"
        ]
        == "sha256:29be927d05d5ed09380a9d28884237c9067036996e6d6c928fa6fdc2b64ab068"
    )


def test_aes_c3_contract_and_packet_are_closed_and_exact() -> None:
    contract, schema, packet = _packet()

    assert validate_contract(contract, schema) == []
    assert schema["additionalProperties"] is False
    assert len(packet["scenarios"]) == 61
    ids = [scenario["scenario_id"] for scenario in packet["scenarios"]]
    assert len(set(ids)) == 61
    assert set(ids) == set(SCENARIO_EXPECTATIONS)
    assert len(contract["reason_vocabulary"]) == 12
    assert len(contract["status_vocabulary"]) == 3
    assert len(contract["mutation_id_vocabulary"]) == len(MUTATION_ID_VOCABULARY)
    assert contract["status_vocabulary"] == STATUS_VOCABULARY


def test_aes_c3_all_61_scenarios_match_expected_status_reason_calls_and_release() -> (
    None
):
    by_id = _all_scenarios()

    assert set(by_id) == set(SCENARIO_EXPECTATIONS)
    for scenario_id, (status, reason, calls, released) in SCENARIO_EXPECTATIONS.items():
        result = evaluate_attempt(by_id[scenario_id])
        assert result["status"] == status, scenario_id
        assert result["reason_codes"] == [reason], scenario_id
        assert result["pure_python_call_count"] == calls, scenario_id
        assert result["released_result_count"] == released, scenario_id


def test_aes_c3_replay_fixture_never_enters_work_cell_view() -> None:
    by_id = _all_scenarios()

    for scenario_id, scenario in by_id.items():
        result = evaluate_attempt(scenario)
        assert result["replay_fixture_presented_to_work_cell"] is False, scenario_id
        replay = scenario.get("replay_artifact")
        if replay is not None:
            assert replay["synthetic_noncredential"] is True
            assert replay["kind"] in ("lease", "alias", "token")
            assert set(REPLAY_BINDING_FIELDS) <= set(replay)
            current_binding = {
                "generation_id": CURRENT_GENERATION_ID,
                "manifest_id": CURRENT_MANIFEST_ID,
                "manifest_digest": CURRENT_MANIFEST_DIGEST,
                "bureau_id": CURRENT_BUREAU_ID,
                "work_cell_id": CURRENT_WORK_CELL_ID,
                "authority_binding_digest": scenario["authority_binding_digest"],
            }
            assert any(
                replay[field] != current_binding[field]
                for field in REPLAY_BINDING_FIELDS
            )
            c2 = _base_c2_attempt(scenario)
            work_cell_json = json.dumps(c2["work_cell_view"], sort_keys=True)
            assert replay["fixture_id"] not in work_cell_json
            assert replay["fixture_digest"] not in work_cell_json
        # The C3 wrapper is metadata-only; it carries no work-cell view at all.
        assert "work_cell_view" not in scenario, scenario_id


def test_aes_c3_raw_payloads_absent_from_results_and_evidence() -> None:
    report = build_report()
    # Recover the fixture payloads from the scenario packet, never from results.
    _, _, packet = _packet()
    payloads = [
        scenario["payload_value"]
        for scenario in packet["scenarios"]
        if isinstance(scenario.get("payload_value"), str)
    ]

    def occurs(value):
        if isinstance(value, str):
            return any(p in value for p in payloads)
        if isinstance(value, dict):
            return any(occurs(v) for v in value.values())
        if isinstance(value, list):
            return any(occurs(v) for v in value)
        return False

    assert not occurs(report)
    for result in report["scenario_results"]:
        assert not occurs(result)
    assert report["opaque_payload_non_release"] is True
    assert report["raw_payload_leak_scenarios"] == []


def test_aes_c3_all_hostile_mutations_fail_closed_with_zero_release() -> None:
    rejected, admitted = validate_hostile_mutations()

    assert len(_hostile_mutations()) == 33
    assert len(rejected) == 33
    assert admitted == []


def test_aes_c3_all_hostile_contract_mutations_fail_closed() -> None:
    rejected, admitted = validate_hostile_contract_mutations()

    assert len(_hostile_contract_mutations()) == 18
    assert len(rejected) == 18
    assert admitted == []


def test_aes_c3_contract_rejects_undeclared_nested_rules_and_changed_digests() -> None:
    contract, schema, _ = _packet()

    inherited_changed = copy.deepcopy(contract)
    inherited_key = next(iter(inherited_changed["inherited_artifact_digests"]))
    inherited_changed["inherited_artifact_digests"][inherited_key] = (
        "sha256:" + "9" * 64
    )
    assert validate_contract(inherited_changed, schema)

    precedence_changed = copy.deepcopy(contract)
    precedence_changed["containment_precedence"][0] = "0_forged_precedence"
    assert validate_contract(precedence_changed, schema)

    egress_ceiling_changed = copy.deepcopy(contract)
    egress_ceiling_changed["egress_budget_rule"]["ceiling_total_bytes_12288"] = 999
    assert validate_contract(egress_ceiling_changed, schema)

    zero_runtime_opened = copy.deepcopy(contract)
    zero_runtime_opened["zero_runtime_boundary"]["runtime_started"] = True
    assert validate_contract(zero_runtime_opened, schema)

    status_vocab_changed = copy.deepcopy(contract)
    status_vocab_changed["status_vocabulary"][0] = "forged_status"
    assert validate_contract(status_vocab_changed, schema)


def test_aes_c3_static_boundary_check_finds_no_external_effect_path() -> None:
    assert static_boundary_check() == []


def test_aes_c3_every_scenario_attempt_is_closed_and_validates() -> None:
    _, schema, packet = _packet()
    for scenario in packet["scenarios"]:
        assert validate_attempt(scenario) == [], scenario["scenario_id"]
        result = evaluate_attempt(scenario)
        assert (
            validate_instance(
                result,
                schema["$defs"]["HostileContainmentResult"],
                root_schema=schema,
            )
            == []
        ), scenario["scenario_id"]


def test_aes_c3_public_evaluator_rejects_malformed_input_without_raising() -> None:
    malformed = copy.deepcopy(_all_scenarios()["stale-alias-replay-stop"])
    del malformed["scenario_id"]

    assert "$:missing:scenario_id" in validate_attempt(malformed)
    result = evaluate_attempt(malformed)

    assert result["status"] == "reject"
    assert result["reason_codes"] == ["closed_contract_rejection"]
    assert result["pure_python_call_count"] == 0
    assert result["released_result_count"] == 0
    assert result["scenario_id"] == "invalid-hostile-containment-attempt"
    assert result["invocation_digest"] is None
    assert result["result_digest"] is None

    for malformed_root in (None, [], "forged"):
        assert validate_attempt(malformed_root) == ["$:type"]
        root_result = evaluate_attempt(malformed_root)
        assert root_result["status"] == "reject"
        assert root_result["reason_codes"] == ["closed_contract_rejection"]
        assert root_result["pure_python_call_count"] == 0
        assert root_result["released_result_count"] == 0


def test_aes_c3_replay_presence_and_declared_base_are_not_cosmetic() -> None:
    canonical = _all_scenarios()["stale-alias-replay-stop"]

    no_fixture = copy.deepcopy(canonical)
    no_fixture["replay_artifact"] = None
    assert "$:canonical_scenario_binding_mismatch" in validate_attempt(no_fixture)
    no_fixture_result = evaluate_attempt(no_fixture)
    assert no_fixture_result["status"] == "reject"
    assert no_fixture_result["released_result_count"] == 0

    changed_base = copy.deepcopy(canonical)
    changed_base["base_scenario_id"] = "exact-inert-dispatch-simulated"
    assert "$:canonical_scenario_binding_mismatch" in validate_attempt(changed_base)
    changed_base_result = evaluate_attempt(changed_base)
    assert changed_base_result["status"] == "reject"
    assert changed_base_result["released_result_count"] == 0


def test_aes_c3_declared_inherited_base_controls_the_inner_object() -> None:
    c2_packet = _load(c3_module.AES_C2_SCENARIOS_PATH)
    c2_ids = {scenario["scenario_id"] for scenario in c2_packet["scenarios"]}

    for scenario in _all_scenarios().values():
        if scenario["attack_family"] in ("cumulative", "context_binding"):
            continue
        c2 = _base_c2_attempt(scenario)
        base_id = scenario["base_scenario_id"]
        if base_id in c2_ids:
            assert c2["scenario_id"] == base_id
        else:
            assert c2["broker_admission_attempt"]["scenario_id"] == base_id


def test_aes_c3_contradictory_inner_release_cannot_be_relabelled_as_stop(
    monkeypatch,
) -> None:
    def contradictory_simulated(_attempt):
        return {
            "status": "simulated",
            "reason_codes": ["simulated_inert_adapter"],
            "admission_decision": "allow",
            "admission_reason_codes": ["manifest_grant_and_current_authority"],
            "simulated_invocation_count": 1,
            "released_simulated_result": True,
            "invocation_digest": "sha256:" + "1" * 64,
            "result_digest": "sha256:" + "2" * 64,
        }

    monkeypatch.setattr(
        c3_module, "evaluate_simulation_attempt", contradictory_simulated
    )
    by_id = _all_scenarios()

    for scenario_id in (
        "stale-alias-replay-stop",
        "clear-egress-budget-overflow-stop",
    ):
        result = evaluate_attempt(by_id[scenario_id])
        assert result["status"] == "reject", scenario_id
        assert result["reason_codes"] == ["closed_contract_rejection"], scenario_id
        assert result["pure_python_call_count"] == 1, scenario_id
        assert result["released_result_count"] == 0, scenario_id
        assert result["invocation_digest"] is None, scenario_id
        assert result["result_digest"] is None, scenario_id


def test_aes_c3_cumulative_sequences_reject_contradictory_inner_results(
    monkeypatch,
) -> None:
    boundary = _all_scenarios()["boundary-probe-denial-sequence-stop"]

    def permissive_c1(attempt):
        observed = copy.deepcopy(attempt["budget_state"]["observed"])
        observed["denied_operations"] += 1
        observed["boundary_probes"] += 1
        return {
            "decision": "allow",
            "reason_codes": ["manifest_grant_and_current_authority"],
            "after_observed": observed,
            "after_terminal_state": "active",
            "after_next_operation_permitted": True,
        }

    monkeypatch.setattr(c3_module, "evaluate_c1_attempt", permissive_c1)
    boundary_result = evaluate_attempt(boundary)
    assert boundary_result["status"] == "reject"
    assert boundary_result["pure_python_call_count"] == 0
    assert boundary_result["released_result_count"] == 0

    repeated = _all_scenarios()["repeated-adapter-failure-sequence-stop"]

    def released_c2(_attempt):
        return {
            "status": "simulated",
            "reason_codes": ["simulated_inert_adapter"],
            "admission_decision": "allow",
            "admission_reason_codes": ["manifest_grant_and_current_authority"],
            "simulated_invocation_count": 1,
            "released_simulated_result": True,
            "invocation_digest": "sha256:" + "3" * 64,
            "result_digest": "sha256:" + "4" * 64,
        }

    monkeypatch.setattr(c3_module, "evaluate_simulation_attempt", released_c2)
    repeated_result = evaluate_attempt(repeated)
    assert repeated_result["status"] == "reject"
    assert repeated_result["pure_python_call_count"] == 1
    assert repeated_result["released_result_count"] == 0


def test_aes_c3_regenerated_packet_is_stable() -> None:
    current = _load(SCENARIOS_PATH)
    regenerated = generate_scenarios()

    assert [s["scenario_id"] for s in regenerated["scenarios"]] == [
        s["scenario_id"] for s in current["scenarios"]
    ]
    for scenario in regenerated["scenarios"]:
        scenario_id = scenario["scenario_id"]
        expected = SCENARIO_EXPECTATIONS[scenario_id]
        result = evaluate_attempt(scenario)
        assert result["status"] == expected[0], scenario_id
        assert result["reason_codes"] == [expected[1]], scenario_id
        assert result["pure_python_call_count"] == expected[2], scenario_id
        assert result["released_result_count"] == expected[3], scenario_id


def test_aes_c3_opaque_payload_absent_from_invocation_adapter_and_c2_result() -> None:
    """The raw hostile payload never reaches invocation, adapter result or the
    returned C2 result for the opaque-value path."""
    by_id = _all_scenarios()
    scenario = by_id["environment-variable-reference-inert"]
    payload = scenario["payload_value"]
    calls: list = []
    original = c2_module._pure_inert_render

    def counting(invocation, fixture_value):
        calls.append(invocation)
        return original(invocation, fixture_value)

    c2_module._pure_inert_render = counting
    try:
        result = evaluate_attempt(scenario)
    finally:
        c2_module._pure_inert_render = original

    assert result["status"] == "contained"
    assert result["pure_python_call_count"] == 1
    assert result["released_result_count"] == 1
    assert len(calls) == 1
    invocation = calls[0]
    # The invocation carries only the candidate digest and fixed C2 inputs.
    assert payload not in json.dumps(invocation, sort_keys=True)
    assert payload not in json.dumps(result, sort_keys=True)
    # The raw payload never appears in the C3 evidence either.
    assert payload not in json.dumps(build_report(), sort_keys=True)


def test_aes_c3_each_contained_scenario_releases_digest_only() -> None:
    by_id = _all_scenarios()
    for scenario_id in (
        "exact-inert-control-contained",
        "environment-variable-reference-inert",
        "arbitrary-url-inert",
        "encoded-content-inert",
        "exception-text-inert",
    ):
        scenario = by_id[scenario_id]
        result = evaluate_attempt(scenario)
        assert result["status"] == "contained", scenario_id
        assert result["pure_python_call_count"] == 1, scenario_id
        assert result["released_result_count"] == 1, scenario_id
        assert result["invocation_digest"] is not None, scenario_id
        assert result["result_digest"] is not None, scenario_id
        assert result["contains_sensitive_values"] is False, scenario_id


def test_aes_c3_structural_attacks_reject_before_any_pure_call() -> None:
    by_id = _all_scenarios()
    structural_ids = [
        "environment-key-structural-reject",
        "graphql-mutation-command-reject",
        "sql-command-reject",
        "executable-selector-reject",
        "policy-amendment-reject",
    ]
    for scenario_id in structural_ids:
        scenario = by_id[scenario_id]
        result = evaluate_attempt(scenario)
        assert result["status"] == "reject", scenario_id
        assert result["reason_codes"] == ["closed_contract_rejection"], scenario_id
        assert result["pure_python_call_count"] == 0, scenario_id
        assert result["released_result_count"] == 0, scenario_id


def test_aes_c3_result_carriers_call_once_and_release_nothing() -> None:
    by_id = _all_scenarios()
    carrier_ids = [
        "clear-result-egress-stop",
        "encoded-result-egress-stop",
        "compressed-result-egress-stop",
        "chunked-result-egress-stop",
        "exception-result-egress-stop",
    ]
    calls: list = []
    original = c2_module._pure_inert_render

    def counting(invocation, fixture_value):
        calls.append(invocation)
        return original(invocation, fixture_value)

    c2_module._pure_inert_render = counting
    try:
        for scenario_id in carrier_ids:
            scenario = by_id[scenario_id]
            result = evaluate_attempt(scenario)
            assert result["status"] == "stop", scenario_id
            assert result["reason_codes"] == ["adapter_result_invalid"], scenario_id
            assert result["pure_python_call_count"] == 1, scenario_id
            assert result["released_result_count"] == 0, scenario_id
    finally:
        c2_module._pure_inert_render = original
    assert len(calls) == 5


def test_aes_c3_boundary_probe_denial_sequence_latches_terminal() -> None:
    scenario = _all_scenarios()["boundary-probe-denial-sequence-stop"]
    result = evaluate_attempt(scenario)

    assert result["status"] == "stop"
    assert result["reason_codes"] == ["denial_budget_exhausted"]
    assert result["pure_python_call_count"] == 0
    assert result["released_result_count"] == 0

    # Two boundary-probe denials reach ceiling 2; the third exact operation
    # stops before dispatch with zero pure calls.
    denied = 0
    probes = 0
    for _ in range(2):
        c1 = c3_module._c1_attempt("candidate-operation-identity-deny")
        c1["budget_state"]["observed"]["denied_operations"] = denied
        c1["budget_state"]["observed"]["boundary_probes"] = probes
        c1["budget_state"]["terminal_state"] = "active"
        c1["budget_state"]["next_operation_permitted"] = True
        r = c3_module.evaluate_c1_attempt(c1)
        denied = r["after_observed"]["denied_operations"]
        probes = r["after_observed"]["boundary_probes"]
    assert (denied, probes) == (2, 2)


def test_aes_c3_repeated_adapter_failure_sequence_calls_twice_releases_nothing() -> (
    None
):
    scenario = _all_scenarios()["repeated-adapter-failure-sequence-stop"]
    calls: list = []
    original = c2_module._pure_inert_render

    def counting(invocation, fixture_value):
        calls.append(invocation)
        return original(invocation, fixture_value)

    c2_module._pure_inert_render = counting
    try:
        result = evaluate_attempt(scenario)
    finally:
        c2_module._pure_inert_render = original

    assert result["status"] == "stop"
    assert result["reason_codes"] == ["repeated_failure_budget_exhausted"]
    assert result["pure_python_call_count"] == 2
    assert result["released_result_count"] == 0
    assert len(calls) == 2  # two malformed-result runs, the third makes no call


def test_aes_c3_egress_budget_exact_256_byte_accounting() -> None:
    by_id = _all_scenarios()
    for scenario_id in (
        "clear-egress-budget-overflow-stop",
        "encoded-egress-budget-overflow-stop",
        "compressed-egress-budget-overflow-stop",
        "chunked-egress-budget-overflow-stop",
        "exception-egress-budget-overflow-stop",
    ):
        scenario = by_id[scenario_id]
        assert scenario["payload_utf8_byte_count"] == 256, scenario_id
        result = evaluate_attempt(scenario)
        assert result["status"] == "stop", scenario_id
        assert result["reason_codes"] == ["egress_budget_exhausted"], scenario_id
        assert result["pure_python_call_count"] == 0, scenario_id
        assert result["released_result_count"] == 0, scenario_id
        # 12,033 observed + 256 proposed = 12,289 > 12,288 ceiling.
        assert 12033 + scenario["payload_utf8_byte_count"] == 12289


def test_aes_c3_stale_replay_context_and_supply_stop_with_zero_call() -> None:
    by_id = _all_scenarios()
    stop_ids = [
        "generation-superseded-replay-stop",
        "restart-generation-lease-replay-stop",
        "cross-bureau-lease-replay-stop",
        "stale-alias-replay-stop",
        "stale-token-replay-stop",
        "post-admission-revocation-stop",
        "post-admission-external-kill-stop",
        "candidate-context-binding-mismatch-stop",
        "proofreader-context-binding-mismatch-stop",
        "manifest-digest-mismatch-stop",
        "adapter-artifact-digest-mismatch-stop",
        "runtime-image-digest-mismatch-stop",
        "model-provider-contract-digest-mismatch-stop",
    ]
    for scenario_id in stop_ids:
        scenario = by_id[scenario_id]
        result = evaluate_attempt(scenario)
        assert result["status"] == "stop", scenario_id
        assert result["pure_python_call_count"] == 0, scenario_id
        assert result["released_result_count"] == 0, scenario_id
        assert result["contains_sensitive_values"] is False, scenario_id
