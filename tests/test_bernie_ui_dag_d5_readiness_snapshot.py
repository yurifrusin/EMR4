import json
import subprocess
import sys

import pytest

from scripts.bernie_ui_dag_d5_readiness_snapshot import (
    DEFAULT_BLOCKED_SNAPSHOT_PATH,
    assert_d5_readiness_snapshot_safety,
    assert_matches_blocked_d5_readiness_snapshot,
    build_d5_readiness_snapshot,
)


def test_d5_readiness_snapshot_matches_committed_blocked_snapshot():
    snapshot = build_d5_readiness_snapshot()

    assert_d5_readiness_snapshot_safety(snapshot)
    assert_matches_blocked_d5_readiness_snapshot(snapshot)
    assert snapshot == json.loads(DEFAULT_BLOCKED_SNAPSHOT_PATH.read_text(encoding="utf-8"))


def test_d5_readiness_snapshot_says_ui_ready_but_backend_delivery_blocked():
    snapshot = build_d5_readiness_snapshot()

    assert snapshot["ui_consumer_ready"] is True
    assert snapshot["route_intercepted_ui_evidence_only"] is True
    assert snapshot["backend_response_delivery_ready"] is False
    assert snapshot["backend_response_delivery_approved"] is False
    assert snapshot["implementation_authorized"] is False
    assert snapshot["approval_scope_true_count"] == 0
    assert snapshot["readiness_label"] == "ui_consumer_ready_backend_delivery_blocked"
    assert snapshot["next_required_decision"] == "explicit_d5_approval"


def test_d5_readiness_snapshot_keeps_provider_memory_write_and_external_gates_closed():
    snapshot = build_d5_readiness_snapshot()

    assert snapshot["runtime_or_provider_wiring_ready"] is False
    assert snapshot["raw_trove_access_ready"] is False
    assert snapshot["runtime_gate_decision"] == "blocked"
    assert snapshot["default_provider"] == "disabled"
    assert snapshot["live_provider_enabled"] is False
    assert snapshot["provider_calls_performed"] is False
    assert snapshot["write_authority_ready"] is False
    assert snapshot["external_patient_client_ready"] is False
    assert snapshot["closed_gate_scope_count"] == 8


def test_d5_readiness_snapshot_contains_no_route_payload_or_local_fragments():
    serialized = json.dumps(build_d5_readiness_snapshot(), sort_keys=True).casefold()

    for fragment in [
        "/api/",
        "supervised-booking",
        "confirm_payload",
        "appointment_id",
        "patient_id",
        "practitioner_id",
        "local_data",
        "raw diary",
    ]:
        assert fragment not in serialized


def test_d5_readiness_snapshot_safety_rejects_unblocked_backend_delivery():
    snapshot = build_d5_readiness_snapshot()
    snapshot["backend_response_delivery_ready"] = True

    with pytest.raises(AssertionError):
        assert_d5_readiness_snapshot_safety(snapshot)


def test_d5_readiness_snapshot_cli_emits_safe_aggregate_json():
    result = subprocess.run(
        [
            sys.executable,
            "scripts/bernie_ui_dag_d5_readiness_snapshot.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload == build_d5_readiness_snapshot()
    assert payload["schema_version"] == "bernie.ui_dag.d5_readiness_snapshot.v1"
