"""Safe aggregate report tests for the Bernie interpretation harness."""

import json

from scripts.bernie_interpretation_harness_report import (
    REPORT_SCHEMA_VERSION,
    assert_harness_report_safety,
    build_harness_report,
)


def test_harness_report_counts_authored_cases_without_utterance_text():
    report = build_harness_report()
    serialized = json.dumps(report, sort_keys=True).casefold()

    assert report["schema_version"] == REPORT_SCHEMA_VERSION
    assert report["source"] == "authored_synthetic_aggregate"
    assert report["case_fixture_count"] == 4
    assert report["case_count"] == 44
    assert report["contract_count"] == 7
    assert set(report["frame_kind_counts"]) == {
        "clarify",
        "proposal",
        "read_request",
        "refusal",
    }
    assert "utterance" in report["omitted_fields"]
    assert "book an appointment" not in serialized
    assert "which patient" not in serialized
    assert "ignore the rules" not in serialized
    assert_harness_report_safety(report)


def test_harness_report_boundary_posture_is_no_runtime_authority():
    report = build_harness_report()

    assert report["boundaries"] == {
        "provider_calls": "prohibited",
        "route_calls": "prohibited",
        "database_access": "prohibited",
        "raw_trove_access": "prohibited",
        "runtime_memory": "prohibited",
    }
    assert report["omitted_fields"] == [
        "utterance",
        "patient_id",
        "practitioner_id",
        "appointment_id",
        "payload",
    ]


def test_harness_report_contract_dispatches_match_dispatch_counts():
    report = build_harness_report()

    assert set(report["contract_dispatches"]) == set(report["dispatch_counts"])
    assert report["dispatch_counts"]["request_clarification"] == 4
    assert report["frame_kind_counts"]["clarify"] == 4


def test_harness_report_safety_rejects_embedded_utterance_text():
    report = build_harness_report()
    report["unsafe_sample"] = "Book an appointment in the afternoon."

    try:
        assert_harness_report_safety(report)
    except AssertionError:
        pass
    else:
        raise AssertionError("unsafe report text was not rejected")


def test_harness_report_safety_rejects_runtime_boundary_drift():
    report = build_harness_report()
    report["boundaries"]["provider_calls"] = "allowed"

    try:
        assert_harness_report_safety(report)
    except AssertionError:
        pass
    else:
        raise AssertionError("runtime boundary drift was not rejected")


def test_harness_report_safety_rejects_contract_dispatch_drift():
    report = build_harness_report()
    report["contract_dispatches"] = report["contract_dispatches"][:-1]

    try:
        assert_harness_report_safety(report)
    except AssertionError:
        pass
    else:
        raise AssertionError("contract dispatch drift was not rejected")
