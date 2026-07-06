"""Runtime gate checker tests for the Bernie interpretation harness."""

import copy
import json

from scripts.bernie_interpretation_runtime_gate_check import (
    assert_runtime_gate_blocked,
    build_runtime_gate_status,
    load_runtime_gate,
)


def test_runtime_gate_checker_accepts_current_blocked_gate():
    gate = load_runtime_gate()

    assert_runtime_gate_blocked(gate)


def test_runtime_gate_status_is_safe_aggregate_only():
    status = build_runtime_gate_status()
    serialized = json.dumps(status, sort_keys=True).casefold()

    assert status == {
        "schema_version": "bernie.interpretation_harness_runtime_gate_status.v1",
        "gate_schema_version": "bernie.interpretation_harness_runtime_gate.v1",
        "decision": "blocked",
        "blocked_scope_count": 6,
        "required_review_count": 8,
        "forbidden_use_count": 8,
        "pause_trigger_count": 4,
        "sprint_engine_state": "continuing",
        "pause_required": False,
    }
    for fragment in [
        "patient_id",
        "practitioner_id",
        "appointment_id",
        "payload",
        "/api/",
        "local_data",
    ]:
        assert fragment not in serialized


def test_runtime_gate_checker_rejects_unblocked_decision():
    gate = load_runtime_gate()
    drifted = copy.deepcopy(gate)
    drifted["decision"] = "approved"

    try:
        assert_runtime_gate_blocked(drifted)
    except AssertionError:
        pass
    else:
        raise AssertionError("unblocked runtime gate decision was not rejected")


def test_runtime_gate_checker_rejects_true_scope_value():
    gate = load_runtime_gate()
    drifted = copy.deepcopy(gate)
    drifted["scope"]["provider_dry_run_wiring"] = True

    try:
        assert_runtime_gate_blocked(drifted)
    except AssertionError:
        pass
    else:
        raise AssertionError("true runtime gate scope value was not rejected")


def test_runtime_gate_checker_rejects_missing_pause_trigger():
    gate = load_runtime_gate()
    drifted = copy.deepcopy(gate)
    drifted["sprint_engine_pause_required_if"] = drifted[
        "sprint_engine_pause_required_if"
    ][:-1]

    try:
        assert_runtime_gate_blocked(drifted)
    except AssertionError:
        pass
    else:
        raise AssertionError("missing sprint pause trigger was not rejected")
