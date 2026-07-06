"""Combined readiness checks for the Bernie interpretation harness."""

import json

from scripts.bernie_interpretation_readiness_check import (
    READINESS_SCHEMA_VERSION,
    build_readiness_status,
)


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
