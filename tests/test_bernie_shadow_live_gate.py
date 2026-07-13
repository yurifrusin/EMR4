from __future__ import annotations

import copy
import json

import pytest

from scripts.bernie_shadow_live_gate_check import (
    assert_gate_blocked,
    build_gate_status,
    load_gate,
)


def test_live_replay_gate_is_blocked_and_valid():
    assert_gate_blocked(load_gate())


def test_status_is_aggregate_and_keeps_adapter_contract_work_moving():
    status = build_gate_status()
    assert status == {
        "schema_version": "bernie.shadow_live_replay_gate_status.v1",
        "decision": "blocked",
        "blocked_scope_count": 5,
        "required_review_count": 7,
        "allowed_development_use_count": 5,
        "forbidden_use_count": 7,
        "external_calls_ready": False,
        "runtime_authority_ready": False,
        "sprint_engine_state": "continuing_adapter_contract_work",
    }
    serialized = json.dumps(status)
    assert "patient_id" not in serialized
    assert "instruction" not in serialized


@pytest.mark.parametrize(
    "mutate",
    [
        lambda gate: gate.update(decision="approved"),
        lambda gate: gate["scope"].update(external_provider_prompt_calls=True),
        lambda gate: gate["required_before_unblocking"].pop(),
        lambda gate: gate["allowed_while_blocked"].append("external_prompt_execution"),
        lambda gate: gate["forbidden_while_blocked"].pop(),
    ],
)
def test_gate_checker_rejects_authority_or_contract_drift(mutate):
    gate = copy.deepcopy(load_gate())
    mutate(gate)
    with pytest.raises(AssertionError):
        assert_gate_blocked(gate)
