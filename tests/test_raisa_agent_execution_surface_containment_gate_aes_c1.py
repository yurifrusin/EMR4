"""Focused tests for the AES-C1 provider-free admission rehearsal."""

from __future__ import annotations

import copy
import json

from scripts.raisa_agent_execution_surface_containment_gate_aes_c0_acceptance import (
    validate_instance,
)
from scripts.raisa_agent_execution_surface_containment_gate_aes_c1_admission import (
    AES_C0_SCHEMA,
    BROKER_REASON_CODES,
    CONTRACT_PATH,
    SCENARIOS_PATH,
    SCENARIO_EXPECTATIONS,
    SCHEMA_PATH,
    _hostile_contract_mutations,
    _hostile_mutations,
    _load,
    build_report,
    compute_manifest_digest,
    digest_of,
    evaluate_attempt,
    generate_scenarios,
    validate_attempt,
    validate_contract,
    validate_hostile_contract_mutations,
    validate_hostile_mutations,
)


def _json_loads(value: str) -> dict:
    return json.loads(value)


def _json_dumps(value: dict) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _packet() -> tuple[dict, dict, dict]:
    return _load(CONTRACT_PATH), _load(SCHEMA_PATH), _load(SCENARIOS_PATH)


def test_aes_c1_report_passes_with_zero_runtime_provider_or_data() -> None:
    report = build_report()

    assert report["status"] == "passed"
    assert report["reasons"] == []
    assert report["scenario_count"] == 45
    assert report["allow_count"] == 2
    assert report["deny_count"] == 25
    assert report["stop_count"] == 18
    assert report["runtime_started"] is False
    assert report["provider_calls"] == 0
    assert report["adapters_executed"] == 0
    assert report["network_operations"] == 0
    assert report["database_operations"] == 0
    assert report["source_operations"] == 0
    assert report["tool_operations"] == 0
    assert report["command_operations"] == 0
    assert report["product_or_patient_data"] is False
    assert report["mutation_admitted"] == []
    assert report["mutation_rejected_count"] == len(_hostile_mutations())
    assert report["contract_mutation_admitted"] == []
    assert report["contract_mutation_rejected_count"] == len(
        _hostile_contract_mutations()
    )


def test_aes_c1_inherited_aes_c0_digests_match_frozen_hashes() -> None:
    contract, _, _ = _packet()
    inherited = contract["inherited_artifact_digests"]

    assert inherited == {
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/architecture-contract.json": (
            "sha256:403c7ddac2399760395d60a8094ffe42d2519a4a809bc8a59104acd2883eb9ae"
        ),
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/architecture-contract.schema.json": (
            "sha256:344d88c59a5d781ebb205de575b66f2e3d64f3878f73c9c0bf4d86eb996b1740"
        ),
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/authored-synthetic-contract-examples.json": (
            "sha256:f77801d2d752ca2daeed1b3116d78a965441bc1996f6b6da60eccf72fbee9f3e"
        ),
    }


def test_aes_c1_contract_and_packet_are_closed_and_exact() -> None:
    contract, schema, packet = _packet()

    assert validate_contract(contract, schema) == []
    assert schema["additionalProperties"] is False
    assert len(packet["scenarios"]) == 45
    ids = [scenario["scenario_id"] for scenario in packet["scenarios"]]
    assert len(set(ids)) == 45
    assert set(ids) == set(SCENARIO_EXPECTATIONS)
    assert set(contract["broker_reason_vocabulary"]) == set(BROKER_REASON_CODES)


def test_aes_c1_all_45_scenarios_match_expected_decisions() -> None:
    _, _, packet = _packet()
    by_id = {scenario["scenario_id"]: scenario for scenario in packet["scenarios"]}

    assert set(by_id) == set(SCENARIO_EXPECTATIONS)
    for scenario_id, (decision, reasons, after_terminal) in SCENARIO_EXPECTATIONS.items():
        result = evaluate_attempt(by_id[scenario_id])
        assert result["decision"] == decision, scenario_id
        assert result["reason_codes"] == reasons, scenario_id
        assert (result["after_next_operation_permitted"] is False) == after_terminal, (
            scenario_id
        )


def test_aes_c1_sentinel_normalized_manifest_digest_is_independent() -> None:
    _, _, packet = _packet()
    manifest = packet["scenarios"][0]["generation_manifest"]

    computed = compute_manifest_digest(manifest)
    assert computed == manifest["manifest_digest"]
    assert computed == manifest["supply_chain_identity"]["generation_manifest_digest"]
    assert computed == packet["scenarios"][0]["current_generation_state"][
        "current_manifest_digest"
    ]

    mutated = _json_loads(_json_dumps(manifest))
    mutated["purpose_code"] = "mutated-purpose"
    assert compute_manifest_digest(mutated) != computed


def test_aes_c1_candidate_and_budget_digests_are_independent() -> None:
    _, _, packet = _packet()
    scenario = packet["scenarios"][0]
    result = evaluate_attempt(scenario)

    decision = result["broker_decision"]
    assert decision["candidate_digest"] == digest_of(scenario["candidate"])
    ceilings = scenario["budget_state"]["ceilings"]
    assert decision["budget_before_digest"] == digest_of(
        {"ceilings": ceilings, "observed": scenario["budget_state"]["observed"]}
    )
    assert decision["budget_after_digest"] == digest_of(
        {
            "ceilings": ceilings,
            "observed": result["after_observed"],
            "terminal_state": result["after_terminal_state"],
            "next_operation_permitted": result["after_next_operation_permitted"],
        }
    )


def test_aes_c1_zero_disabled_does_not_pre_exhaust_unrelated_zero_counters() -> None:
    _, _, packet = _packet()
    by_id = {scenario["scenario_id"]: scenario for scenario in packet["scenarios"]}

    result = evaluate_attempt(by_id["zero-disabled-capability-stop"])
    assert result["decision"] == "stop"
    assert result["reason_codes"] == ["budget_exhausted"]
    assert result["after_next_operation_permitted"] is False
    assert result["after_observed"]["product_mutations"] == 0
    assert result["after_observed"]["command_confirmations"] == 0

    allow = evaluate_attempt(by_id["exact-inert-intersection-allow"])
    assert allow["decision"] == "allow"


def test_aes_c1_denial_ceiling_pair_is_terminal_and_blocks_following() -> None:
    _, _, packet = _packet()
    by_id = {scenario["scenario_id"]: scenario for scenario in packet["scenarios"]}

    current = evaluate_attempt(by_id["denial-ceiling-reached-after-deny"])
    assert current["decision"] == "deny"
    assert current["reason_codes"] == ["manifest_grant_missing"]
    assert current["after_next_operation_permitted"] is False
    assert current["after_observed"]["denied_operations"] == 3

    following = evaluate_attempt(by_id["attempt-after-denial-ceiling-stop"])
    assert following["decision"] == "stop"
    assert following["reason_codes"] == ["budget_exhausted"]
    assert following["after_next_operation_permitted"] is False


def test_aes_c1_every_decision_and_evidence_is_a_closed_aes_c0_message() -> None:
    _, _, packet = _packet()
    for scenario in packet["scenarios"]:
        result = evaluate_attempt(scenario)
        assert validate_instance(
            result["broker_decision"],
            AES_C0_SCHEMA["$defs"]["BrokerDecision"],
            root_schema=AES_C0_SCHEMA,
        ) == []
        assert validate_instance(
            result["evidence"],
            AES_C0_SCHEMA["$defs"]["AuditEvidenceEnvelope"],
            root_schema=AES_C0_SCHEMA,
        ) == []


def test_aes_c1_all_hostile_mutations_fail_closed_with_zero_admission() -> None:
    rejected, admitted = validate_hostile_mutations()

    assert len(_hostile_mutations()) == 24
    assert len(rejected) == 24
    assert admitted == []


def test_aes_c1_contract_rejects_undeclared_nested_rules() -> None:
    contract, schema, _ = _packet()

    inherited_changed = copy.deepcopy(contract)
    inherited_key = next(iter(inherited_changed["inherited_artifact_digests"]))
    inherited_changed["inherited_artifact_digests"][inherited_key] = (
        "sha256:" + "9" * 64
    )
    assert validate_contract(inherited_changed, schema)

    manifest_extra = copy.deepcopy(contract)
    manifest_extra["manifest_digest_rule"]["forged_rule"] = "forged"
    assert validate_contract(manifest_extra, schema)

    precedence_changed = copy.deepcopy(contract)
    precedence_changed["decision_precedence"][0] = "0_forged_precedence"
    assert validate_contract(precedence_changed, schema)

    denial_policy_extra = copy.deepcopy(contract)
    denial_policy_extra["denial_counter_policy"]["forged_policy"] = True
    assert validate_contract(denial_policy_extra, schema)

    budget_dimensions_extra = copy.deepcopy(contract)
    budget_dimensions_extra["budget_dimensions"]["forged_dimension"] = ["forged"]
    assert validate_contract(budget_dimensions_extra, schema)

    zero_runtime_opened = copy.deepcopy(contract)
    zero_runtime_opened["zero_runtime_boundary"]["runtime_started"] = True
    assert validate_contract(zero_runtime_opened, schema)

    candidate_rule_extra = copy.deepcopy(contract)
    candidate_rule_extra["candidate_and_budget_digest_rule"]["forged_rule"] = "forged"
    assert validate_contract(candidate_rule_extra, schema)

    inherited_extra = copy.deepcopy(contract)
    inherited_extra["inherited_artifact_digests"]["forged/path.json"] = (
        "sha256:" + "0" * 64
    )
    assert validate_contract(inherited_extra, schema)


def test_aes_c1_all_hostile_contract_mutations_fail_closed() -> None:
    rejected, admitted = validate_hostile_contract_mutations()

    assert len(_hostile_contract_mutations()) == 8
    assert len(rejected) == 8
    assert admitted == []


def test_aes_c1_candidate_rejects_undeclared_typed_and_proposal_fields() -> None:
    _, _, packet = _packet()
    allow = next(
        s for s in packet["scenarios"]
        if s["scenario_id"] == "exact-inert-intersection-allow"
    )

    typed_extra = copy.deepcopy(allow)
    typed_extra["candidate"]["typed_arguments"]["unrecognized-benign-key"] = "x"
    assert validate_attempt(typed_extra)
    result = evaluate_attempt(typed_extra)
    assert result["decision"] == "deny"
    assert result["reason_codes"] == ["operation_identity_candidate_controlled"]

    proposal_extra = copy.deepcopy(allow)
    proposal_extra["candidate"]["proposal_fields"]["unrecognized-benign-key"] = "x"
    assert validate_attempt(proposal_extra)
    result = evaluate_attempt(proposal_extra)
    assert result["decision"] == "deny"
    assert result["reason_codes"] == ["operation_identity_candidate_controlled"]

    # The declared hostile operation_id remains schema-shaped but semantically
    # denied, preserving the frozen candidate-operation-identity-deny scenario.
    identity_deny = next(
        s for s in packet["scenarios"]
        if s["scenario_id"] == "candidate-operation-identity-deny"
    )
    assert validate_attempt(identity_deny) == []
    result = evaluate_attempt(identity_deny)
    assert result["decision"] == "deny"
    assert result["reason_codes"] == ["operation_identity_candidate_controlled"]


def test_aes_c1_regenerated_packet_is_stable() -> None:
    current = _load(SCENARIOS_PATH)
    regenerated = generate_scenarios()

    assert [s["scenario_id"] for s in regenerated["scenarios"]] == [
        s["scenario_id"] for s in current["scenarios"]
    ]
    for scenario in regenerated["scenarios"]:
        scenario_id = scenario["scenario_id"]
        expected = SCENARIO_EXPECTATIONS[scenario_id]
        result = evaluate_attempt(scenario)
        assert result["decision"] == expected[0]
        assert result["reason_codes"] == expected[1]
        assert (result["after_next_operation_permitted"] is False) == expected[2]
