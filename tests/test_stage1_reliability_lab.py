"""Direct, offline checks for the optional bounded Reliability Lab progress view."""

import hashlib
import json
from pathlib import Path

import pytest

import stage1_demo_http as lab


REPORT = Path(__file__).resolve().parents[1] / "docs" / "demo" / "stage1-reliability-results.json"


def test_reviewed_progress_keeps_attempts_distinct_from_delivered_episodes():
    raw = REPORT.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == lab.LAB_PROGRESS_REPORT_SHA
    view = lab.project_lab_progress(raw, digest)
    assert view["baseline_dispositions"] == {
        "current_controls": 2, "qualified_reused_boundaries": 4, "not_run": 10}
    assert [(attempt["name"], attempt["selected_test_instances"],
             attempt["phase_reports"], attempt["delivered_selected_records"])
            for attempt in view["attempts"]] == [
                ("Native04", 2, 6, 2), ("Native05", 2, 6, 0),
                ("Native06", 0, 0, 0), ("Native07", 2, 6, 0),
                ("Native08", 0, 0, 0)]
    assert view["attempts"][3]["cases"] == [
        {"case_id": "create-duplicate-lost-response-09", "call_phase": "FAILED"},
        {"case_id": "move-duplicate-lost-response-10", "call_phase": "PASSED"}]
    assert view["attempts"][4]["cases"] == []
    assert view["evidence_through"] == "NATIVE08_REVIEWED_PRE_DOCKER"
    assert [item["case_id"] for item in view["worked_examples"]] == [
        "create-valid-01", "move-valid-timeonly-01",
        "move-attempted-identity-change-05", "move-source-cancelled-08"]
    create, move, identity, cancelled = view["worked_examples"]
    assert create["before_after"] == {
        "before": "appointments 0; request submitted",
        "after": "appointments 1; request booked; 2026-10-15 14:30; Booked; version 1"}
    assert move["before_after"] == {
        "before": "appointments 1; 2026-10-14 15:00; Booked; version 7",
        "after": "appointments 1; 2026-10-15 14:30; Booked; version 8"}
    assert all(item["proposal_observation"] == "NOT_IN_DELIVERED_PROJECTION"
               for item in view["worked_examples"])
    assert create["command_audit"] == move["command_audit"] == (
        "ONE_COMMAND_ONE_AUDIT_IN_DELIVERED_PROJECTION")
    assert all(item["outcome"] == "QUALIFIED_REUSED_BOUNDARY_ONLY"
               for item in (identity, cancelled))
    assert view["whole_journey_grade"] == "UNKNOWN"
    assert view["actual_model"] == view["genuine_ptt_voice"] == "NOT_RUN"
    assert view["display"] == view["disclosure"] == "NOT_OBSERVED"
    assert not ({"raw", "request", "proposal", "token", "audio", "transcript"} & set(view))


def test_unbound_or_changed_report_cannot_be_displayed():
    assert lab.project_lab_progress(None, None) is None
    raw = REPORT.read_bytes()
    with pytest.raises(ValueError, match="LAB_PROGRESS_BINDING_INVALID"):
        lab.project_lab_progress(raw + b" ", hashlib.sha256(raw + b" ").hexdigest())


def test_failed_test_cannot_be_relabelled_as_delivered_record(monkeypatch):
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    report["attempts"][3]["delivered_selected_records"] = 1
    altered = json.dumps(report, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(altered).hexdigest()
    monkeypatch.setattr(lab, "LAB_PROGRESS_REPORT_SHA", digest)
    with pytest.raises(ValueError, match="LAB_PROGRESS_NATIVE07_INVALID"):
        lab.project_lab_progress(altered, digest)


def test_authored_expectation_cannot_be_relabelled_as_observed_proposal(monkeypatch):
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    report["worked_examples"][0]["proposal_observation"] = "OBSERVED"
    altered = json.dumps(report, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(altered).hexdigest()
    monkeypatch.setattr(lab, "LAB_PROGRESS_REPORT_SHA", digest)
    with pytest.raises(ValueError, match="LAB_PROGRESS_WORKED_EXAMPLES_INVALID"):
        lab.project_lab_progress(altered, digest)
