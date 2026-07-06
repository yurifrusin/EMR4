"""Combined readiness checks for the Bernie interpretation harness."""

import json

from scripts.bernie_interpretation_readiness_check import (
    READINESS_SCHEMA_VERSION,
    assert_matches_blocked_readiness_snapshot,
    build_readiness_status,
)
from scripts.bernie_interpretation_runtime_gate_check import DEFAULT_GATE_PATH


def test_readiness_status_combines_report_and_runtime_gate_safely():
    status = build_readiness_status()

    assert status == {
        "schema_version": READINESS_SCHEMA_VERSION,
        "harness_report_schema_version": "bernie.interpretation_harness_report.v1",
        "runtime_gate_status_schema_version": (
            "bernie.interpretation_harness_runtime_gate_status.v1"
        ),
        "case_count": 44,
        "contract_count": 7,
        "dispatch_count": 7,
        "frame_kind_count": 4,
        "runtime_gate_decision": "blocked",
        "runtime_gate_pause_required": False,
        "sprint_engine_state": "continuing",
        "runtime_or_provider_wiring_ready": False,
        "raw_trove_access_ready": False,
    }


def test_readiness_status_contains_no_fixture_text_or_payload_fields():
    serialized = json.dumps(build_readiness_status(), sort_keys=True).casefold()

    for fragment in [
        "book an appointment",
        "which patient",
        "ignore the rules",
        "patient_id",
        "practitioner_id",
        "appointment_id",
        "payload",
        "/api/",
        "local_data",
        "h15",
        "h_series",
    ]:
        assert fragment not in serialized


def test_readiness_status_does_not_authorize_runtime_provider_or_trove_access():
    status = build_readiness_status()

    assert status["runtime_gate_decision"] == "blocked"
    assert status["runtime_or_provider_wiring_ready"] is False
    assert status["raw_trove_access_ready"] is False
    assert status["sprint_engine_state"] == "continuing"


def test_readiness_status_derives_scope_readiness_from_runtime_gate(monkeypatch):
    gate_status = {
        "schema_version": "bernie.interpretation_harness_runtime_gate_status.v1",
        "decision": "blocked",
        "pause_required": False,
        "runtime_or_provider_wiring_ready": True,
        "raw_trove_access_ready": True,
    }

    monkeypatch.setattr(
        "scripts.bernie_interpretation_readiness_check.build_runtime_gate_status",
        lambda _path: gate_status,
    )

    status = build_readiness_status()

    assert status["runtime_or_provider_wiring_ready"] is True
    assert status["raw_trove_access_ready"] is True


def test_readiness_status_rejects_unblocked_runtime_gate(tmp_path):
    gate = json.loads(DEFAULT_GATE_PATH.read_text(encoding="utf-8"))
    gate["decision"] = "approved"
    gate_path = tmp_path / "runtime_gate.json"
    gate_path.write_text(json.dumps(gate), encoding="utf-8")

    try:
        build_readiness_status(gate_path=gate_path)
    except AssertionError:
        pass
    else:
        raise AssertionError("unblocked runtime gate was not rejected")


def test_readiness_status_rejects_missing_fixture_directory(tmp_path):
    missing_fixture_dir = tmp_path / "missing"

    try:
        build_readiness_status(fixture_dir=missing_fixture_dir)
    except ValueError as exc:
        assert "does not exist" in str(exc)
    else:
        raise AssertionError("missing readiness fixture directory was not rejected")


def test_readiness_status_rejects_empty_fixture_directory(tmp_path):
    try:
        build_readiness_status(fixture_dir=tmp_path)
    except ValueError as exc:
        assert "No JSON fixtures" in str(exc)
    else:
        raise AssertionError("empty readiness fixture directory was not rejected")


def test_readiness_status_rejects_snapshot_mismatch(tmp_path):
    snapshot = build_readiness_status()
    snapshot["runtime_or_provider_wiring_ready"] = True
    snapshot_path = tmp_path / "blocked_readiness_status.json"
    snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")

    try:
        assert_matches_blocked_readiness_snapshot(
            build_readiness_status(),
            snapshot_path=snapshot_path,
        )
    except AssertionError:
        pass
    else:
        raise AssertionError("readiness snapshot mismatch was not rejected")


def test_readiness_status_rejects_missing_snapshot(tmp_path):
    missing_snapshot = tmp_path / "missing_snapshot.json"

    try:
        assert_matches_blocked_readiness_snapshot(
            build_readiness_status(),
            snapshot_path=missing_snapshot,
        )
    except ValueError as exc:
        assert "does not exist" in str(exc)
    else:
        raise AssertionError("missing readiness snapshot was not rejected")
