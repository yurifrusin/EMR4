"""Safe aggregate checker tests for the raw compat header rollout gate."""

import copy
import json

from scripts.raw_compat_header_rollout_gate_check import (
    DEFAULT_GATE_PATH,
    assert_rollout_gate_blocked,
    build_rollout_gate_status,
    load_rollout_gate,
)


def test_rollout_gate_checker_accepts_current_blocked_gate():
    gate = load_rollout_gate()

    assert_rollout_gate_blocked(gate)


def test_rollout_gate_status_is_safe_aggregate_only():
    status = build_rollout_gate_status()
    serialized = json.dumps(status, sort_keys=True).casefold()

    assert status == {
        "schema_version": "appointment.raw_compat_header_rollout_gate_status.v1",
        "gate_schema_version": "appointment.raw_compat_header_rollout_gate.v1",
        "decision": "blocked",
        "environment_count": 0,
        "required_review_count": 8,
        "allowed_current_uses_count": 5,
        "forbidden_use_count": 11,
        "pause_trigger_count": 4,
        "observability_ready": False,
        "rollout_ready": False,
        "sprint_engine_state": "continuing",
        "pause_required": False,
    }
    for fragment in [
        "/api/",
        "raw_compat_create",
        "raw_compat_update",
        "raw_compat_status",
        "raw_compat_delete",
        "docs/diary",
        "apiFetch",
        "local_data",
        "patient_id",
        "appointment_id",
    ]:
        assert fragment.casefold() not in serialized


def test_rollout_gate_checker_rejects_unblocked_decision():
    gate = load_rollout_gate()
    drifted = copy.deepcopy(gate)
    drifted["decision"] = "approved"

    try:
        assert_rollout_gate_blocked(drifted)
    except AssertionError:
        pass
    else:
        raise AssertionError("unblocked rollout gate decision was not rejected")


def test_rollout_gate_checker_rejects_non_empty_environments():
    gate = load_rollout_gate()
    drifted = copy.deepcopy(gate)
    drifted["rollout_surface"]["environments_can_default_header"].append("production")

    try:
        assert_rollout_gate_blocked(drifted)
    except AssertionError:
        pass
    else:
        raise AssertionError("non-empty header rollout environment list was not rejected")


def test_rollout_gate_checker_rejects_changed_required_list():
    gate = load_rollout_gate()
    drifted = copy.deepcopy(gate)
    drifted["required_before_unblocking"].append("new_requirement")

    try:
        assert_rollout_gate_blocked(drifted)
    except AssertionError:
        pass
    else:
        raise AssertionError("changed required-before-unblocking list was not rejected")


def test_rollout_gate_checker_rejects_changed_forbidden_list():
    gate = load_rollout_gate()
    drifted = copy.deepcopy(gate)
    drifted["forbidden_current_uses"] = drifted["forbidden_current_uses"][:-1]

    try:
        assert_rollout_gate_blocked(drifted)
    except AssertionError:
        pass
    else:
        raise AssertionError("changed forbidden-current-uses list was not rejected")


def test_rollout_gate_checker_rejects_unblocking_signal_true():
    gate = load_rollout_gate()
    drifted = copy.deepcopy(gate)
    drifted["observability_and_audit_signals"][
        "required_before_unblocking_any_environment"
    ]["operational_telemetry_ready"] = True

    try:
        assert_rollout_gate_blocked(drifted)
    except AssertionError:
        pass
    else:
        raise AssertionError("true unblocking observability signal was not rejected")


def test_rollout_gate_status_derives_readiness_booleans_from_gate(monkeypatch):
    gate = load_rollout_gate()
    gate["rollout_surface"]["environments_can_default_header"].append("staging")
    gate["observability_and_audit_signals"][
        "required_before_unblocking_any_environment"
    ]["operational_telemetry_ready"] = True

    def fake_assert_rollout_gate_blocked(_gate):
        return None

    def fake_load_rollout_gate(_path):
        return gate

    monkeypatch.setattr(
        "scripts.raw_compat_header_rollout_gate_check.assert_rollout_gate_blocked",
        fake_assert_rollout_gate_blocked,
    )
    monkeypatch.setattr(
        "scripts.raw_compat_header_rollout_gate_check.load_rollout_gate",
        fake_load_rollout_gate,
    )

    status = build_rollout_gate_status(DEFAULT_GATE_PATH.parent / "unused.json")

    assert status["observability_ready"] is True
    assert status["rollout_ready"] is True
    assert status["environment_count"] == 1


def test_rollout_gate_checker_rejects_missing_pause_trigger():
    gate = load_rollout_gate()
    drifted = copy.deepcopy(gate)
    drifted["sprint_engine_pause_required_if"] = drifted[
        "sprint_engine_pause_required_if"
    ][:-1]

    try:
        assert_rollout_gate_blocked(drifted)
    except AssertionError:
        pass
    else:
        raise AssertionError("missing sprint pause trigger was not rejected")
