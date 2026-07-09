import json
import subprocess
import sys

import pytest

from scripts.bernie_ui_dag_d5_response_shape_report import (
    DEFAULT_SNAPSHOT_PATH,
    assert_matches_committed_response_shape_report,
    assert_response_shape_report_safety,
    build_response_shape_report,
)


def test_response_shape_report_matches_committed_snapshot():
    report = build_response_shape_report()

    assert_response_shape_report_safety(report)
    assert_matches_committed_response_shape_report(report)
    assert report == json.loads(DEFAULT_SNAPSHOT_PATH.read_text(encoding="utf-8"))


def test_response_shape_report_records_backend_field_contract_without_payload_fragments():
    report = build_response_shape_report()

    assert report["single_response_assembly_point"] is True
    assert report["response_field_present_when_snapshot_exists"] is True
    assert report["response_field_null_without_snapshot"] is True
    assert report["display_model_schema_version"] == "bernie.ui_view_model.v1"
    assert report["client_confirmation_request_state_default"] == "idle"
    assert report["backend_delivery_test_count"] == 2

    serialized = json.dumps(report, sort_keys=True).casefold()
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


def test_response_shape_report_keeps_expansion_gates_closed():
    report = build_response_shape_report()

    assert report["closed_scope_count"] == report["closed_scope_total"]
    assert report["provider_or_live_provider_wiring_ready"] is False
    assert report["memory_or_rag_wiring_ready"] is False
    assert report["graphql_delivery_ready"] is False
    assert report["write_authority_ready"] is False
    assert report["external_patient_client_ready"] is False
    assert report["additional_route_delivery_ready"] is False
    assert report["next_required_decision"] == "separate_review_for_any_scope_expansion"


def test_response_shape_report_safety_rejects_write_authority():
    report = build_response_shape_report()
    report["write_authority_ready"] = True

    with pytest.raises(AssertionError):
        assert_response_shape_report_safety(report)


def test_response_shape_report_cli_emits_safe_snapshot():
    result = subprocess.run(
        [sys.executable, "scripts/bernie_ui_dag_d5_response_shape_report.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload == build_response_shape_report()
