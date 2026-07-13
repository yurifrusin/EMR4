"""Tests for the workflow-chain safe aggregate report."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.bernie_workflow_chain_report import (
    WF_CHAIN_REPORT_SCHEMA_VERSION,
    build_workflow_report,
    load_chain_fixtures,
)
from tests.workflow_chain.harness import (
    WF_CHAIN_REPORT_SCHEMA_VERSION as HARNESS_REPORT_VERSION,
    assert_workflow_chain_report_safety,
)


def test_workflow_report_loads_all_chains() -> None:
    chains = load_chain_fixtures(
        Path(__file__).parent / "fixtures" / "bernie_workflow_chains"
    )
    assert len(chains) >= 8
    for chain in chains:
        assert chain.chain_id
        assert len(chain.steps) >= 2


def test_workflow_report_builds_aggregate_without_utterance_text() -> None:
    report = build_workflow_report()
    serialized = json.dumps(report, sort_keys=True).casefold()

    assert report["schema_version"] == HARNESS_REPORT_VERSION
    assert report["source"] == "authored_synthetic_aggregate"
    assert report["chain_count"] >= 8
    assert report["step_count"] >= 20

    # Check that forbidden payload identifiers are not in report
    # (field names like "patient_id" appear in omitted_fields as expected schema)
    assert "book an appointment" not in serialized
    assert "cancel the booking" not in serialized
    assert "/api/" not in serialized
    assert "check in the patient" not in serialized
    assert "ignore the rules" not in serialized


def test_workflow_report_boundary_posture() -> None:
    report = build_workflow_report()
    assert report["boundaries"] == {
        "provider_calls": "prohibited",
        "route_calls": "prohibited",
        "database_access": "prohibited",
        "raw_trove_access": "prohibited",
        "runtime_memory": "prohibited",
    }


def test_workflow_report_has_frame_kind_and_resolution_counts() -> None:
    report = build_workflow_report()
    assert "frame_kind_counts" in report
    assert "resolution_counts" in report
    assert "chain_resolution_counts" in report
    assert set(report["frame_kind_counts"]) <= {
        "proposal",
        "read_request",
        "clarify",
        "refusal",
    }
    assert set(report["resolution_counts"]) <= {
        "resolved",
        "clarification_needed",
        "refused_planned",
        "refused_unsafe",
        "refused_unknown",
    }


def test_workflow_report_safety_assertion_passes() -> None:
    report = build_workflow_report()
    assert_workflow_chain_report_safety(report)


def test_workflow_report_rejects_missing_fixture_directory(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    from scripts.bernie_workflow_chain_report import load_chain_fixtures

    try:
        load_chain_fixtures(missing)
    except ValueError as exc:
        assert "does not exist" in str(exc)
    else:
        raise AssertionError("missing fixture directory was not rejected")


def test_workflow_report_rejects_empty_fixture_directory(tmp_path: Path) -> None:
    from scripts.bernie_workflow_chain_report import load_chain_fixtures

    try:
        load_chain_fixtures(tmp_path)
    except ValueError as exc:
        assert "No JSON fixtures" in str(exc)
    else:
        raise AssertionError("empty fixture directory was not rejected")


def test_workflow_report_rejects_non_directory_path(tmp_path: Path) -> None:
    from scripts.bernie_workflow_chain_report import load_chain_fixtures

    non_dir = tmp_path / "not_a_dir.txt"
    non_dir.write_text("{}", encoding="utf-8")

    try:
        load_chain_fixtures(non_dir)
    except ValueError as exc:
        assert "not a directory" in str(exc)
    else:
        raise AssertionError("non-directory path was not rejected")


def test_workflow_report_safety_rejects_payload_id_in_report() -> None:
    report = build_workflow_report()
    report["unsafe"] = "Contains- patient_id_123"

    try:
        assert_workflow_chain_report_safety(report)
    except AssertionError:
        pass
    else:
        raise AssertionError("forbidden payload reference was not rejected")


def test_workflow_report_safety_rejects_boundary_drift() -> None:
    report = build_workflow_report()
    report["boundaries"]["provider_calls"] = "allowed"

    try:
        assert_workflow_chain_report_safety(report)
    except AssertionError:
        pass
    else:
        raise AssertionError("runtime boundary drift was not rejected")


def test_workflow_report_omitted_fields_are_correct() -> None:
    report = build_workflow_report()
    assert report["omitted_fields"] == [
        "utterance",
        "patient_id",
        "practitioner_id",
        "appointment_id",
        "slot_id",
        "payload",
    ]


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_workflow_report_rejects_directory_without_chains(tmp_path: Path) -> None:
    _write_json(
        tmp_path / "empty_chains.json",
        {
            "schema_version": "bernie.workflow_chain_harness.v1",
            "source": "authored_synthetic",
            "chains": [],
        },
    )
    from scripts.bernie_workflow_chain_report import load_chain_fixtures

    try:
        load_chain_fixtures(tmp_path)
    except ValueError as exc:
        assert "No chains found" in str(exc)
    else:
        raise AssertionError("empty chains list was not rejected")


def test_workflow_report_rejects_invalid_schema_version(tmp_path: Path) -> None:
    _write_json(
        tmp_path / "bad_schema.json",
        {
            "schema_version": "bernie.unknown.v1",
            "source": "authored_synthetic",
            "chains": [
                {
                    "chain_id": "test",
                    "label": "test",
                    "steps": [
                        {
                            "step_label": "s1",
                            "utterance": "Book an appointment.",
                        }
                    ],
                }
            ],
        },
    )
    from scripts.bernie_workflow_chain_report import load_chain_fixtures

    try:
        load_chain_fixtures(tmp_path)
    except ValueError as exc:
        assert "schema_version" in str(exc)
    else:
        raise AssertionError("invalid schema version was not rejected")
