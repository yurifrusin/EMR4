"""Golden fake-provider evidence snapshot for Bernie scenario fixtures."""

import json
from pathlib import Path

from scripts.bernie_scenario_evidence_snapshot import (
    DEFAULT_SNAPSHOT_PATH,
    EVIDENCE_TYPE,
    SNAPSHOT_SCHEMA_VERSION,
    assert_evidence_snapshot_safety,
    assert_matches_blocked_fake_provider_snapshot,
    build_evidence_snapshot,
)


def _snapshot() -> dict[str, object]:
    return json.loads(DEFAULT_SNAPSHOT_PATH.read_text(encoding="utf-8"))


def test_scenario_evidence_snapshot_counts_current_fixture_corpus():
    snapshot = build_evidence_snapshot()

    assert snapshot["schema_version"] == SNAPSHOT_SCHEMA_VERSION
    assert snapshot["scenario_yaml_fixture_count"] == 56
    assert snapshot["interpret_fixture_count"] == 31
    assert snapshot["harness_demo_fixture_count"] == 2
    assert snapshot["non_interpret_fixture_count"] == 23
    assert snapshot["fixtures_since_last_backend_pass"] == 10


def test_scenario_evidence_snapshot_labels_fake_provider_only():
    snapshot = build_evidence_snapshot()

    assert snapshot["evidence_type"] == EVIDENCE_TYPE
    assert snapshot["fake_provider_evidence"] is True
    assert snapshot["route_level_backend_evidence"] is True
    assert snapshot["live_provider_evidence"] is False
    assert snapshot["provider_quality_evidence"] is False
    assert snapshot["provider_calls_performed"] is False


def test_scenario_evidence_snapshot_keeps_provider_and_runtime_gates_closed():
    snapshot = build_evidence_snapshot()

    assert snapshot["default_provider"] == "disabled"
    assert snapshot["runtime_or_provider_wiring_ready"] is False
    assert snapshot["live_provider_enabled"] is False
    assert snapshot["route_behavior_changed"] is False
    assert snapshot["database_access_performed"] is False
    assert snapshot["memory_or_rag_access_performed"] is False
    assert snapshot["historical_diary_material_access_performed"] is False
    assert snapshot["raw_trove_access_ready"] is False
    assert snapshot["runtime_gate_decision"] == "blocked"


def test_scenario_evidence_snapshot_safety_assertion_accepts_current_snapshot():
    assert_evidence_snapshot_safety(build_evidence_snapshot())


def test_scenario_evidence_snapshot_contains_no_text_paths_or_payload_fragments():
    serialized = json.dumps(build_evidence_snapshot(), sort_keys=True).casefold()

    for fragment in [
        "book margaret",
        "actually make it",
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


def test_generated_scenario_evidence_matches_blocked_snapshot():
    generated = build_evidence_snapshot()

    assert generated == _snapshot()
    assert_matches_blocked_fake_provider_snapshot(generated)


def test_scenario_evidence_snapshot_rejects_missing_or_empty_directory(tmp_path):
    missing = tmp_path / "missing"

    try:
        build_evidence_snapshot(missing)
    except ValueError as exc:
        assert "does not exist" in str(exc)
    else:
        raise AssertionError("missing scenario fixture directory was not rejected")

    try:
        build_evidence_snapshot(tmp_path)
    except ValueError as exc:
        assert "No YAML scenario fixtures" in str(exc)
    else:
        raise AssertionError("empty scenario fixture directory was not rejected")


def test_scenario_evidence_snapshot_rejects_unblocked_or_live_labels():
    snapshot = build_evidence_snapshot()
    snapshot["live_provider_evidence"] = True

    try:
        assert_evidence_snapshot_safety(snapshot)
    except AssertionError:
        pass
    else:
        raise AssertionError("live-provider evidence label was not rejected")

    snapshot = build_evidence_snapshot()
    snapshot["runtime_or_provider_wiring_ready"] = True

    try:
        assert_evidence_snapshot_safety(snapshot)
    except AssertionError:
        pass
    else:
        raise AssertionError("runtime/provider readiness was not rejected")


def test_scenario_evidence_snapshot_rejects_missing_committed_snapshot(tmp_path):
    missing_snapshot = tmp_path / "missing_snapshot.json"

    try:
        assert_matches_blocked_fake_provider_snapshot(
            build_evidence_snapshot(),
            snapshot_path=missing_snapshot,
        )
    except ValueError as exc:
        assert "does not exist" in str(exc)
    else:
        raise AssertionError("missing scenario evidence snapshot was not rejected")
