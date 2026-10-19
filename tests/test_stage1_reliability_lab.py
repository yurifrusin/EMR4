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
    assert view["report_basis"] == "STARTUP_PINNED_AUTHORED_REPORT"
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
    with pytest.raises(ValueError, match="LAB_PROGRESS_HISTORICAL_PREFIX_INVALID"):
        lab.project_lab_progress(altered, digest)


def test_authored_expectation_cannot_be_relabelled_as_observed_proposal(monkeypatch):
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    report["worked_examples"][0]["proposal_observation"] = "OBSERVED"
    altered = json.dumps(report, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(altered).hexdigest()
    monkeypatch.setattr(lab, "LAB_PROGRESS_REPORT_SHA", digest)
    with pytest.raises(ValueError, match="LAB_PROGRESS_HISTORICAL_PREFIX_INVALID"):
        lab.project_lab_progress(altered, digest)


def _project_changed(monkeypatch, report):
    raw = json.dumps(report, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    monkeypatch.setattr(lab, "LAB_PROGRESS_REPORT_SHA", digest)
    return lab.project_lab_progress(raw, digest)


def test_future_authored_report_shape_requires_a_new_bound_digest(monkeypatch):
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    report["attempts"].append({"name": "Native09", "status": "PRE_DOCKER_LAUNCH_FAILURE",
        "selected_test_instances": 0, "phase_reports": 0,
        "delivered_selected_records": 0, "cases": [], "effect_review_sha256": "a" * 64})
    report["evidence_through"] = "NATIVE09_REVIEWED_PRE_DOCKER"
    view = _project_changed(monkeypatch, report)
    assert view["attempts"][-1]["name"] == "Native09"
    assert view["baseline_dispositions"]["not_run"] == 10


@pytest.mark.parametrize("index,field,value", [
    (0, "effect_review_sha256", "a" * 64),
    (1, "delivered_selected_records", 1),
    (2, "status", "DELIVERED_VALID_CONTROLS"),
    (3, "phase_reports", 0),
    (4, "name", "Native99"),
])
def test_all_historical_attempts_remain_immutable(monkeypatch, index, field, value):
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    report["attempts"][index][field] = value
    with pytest.raises(ValueError, match="LAB_PROGRESS_HISTORICAL_PREFIX_INVALID"):
        _project_changed(monkeypatch, report)


def _future_report():
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    report["attempts"].append({"name": "Native09", "status": "DELIVERED_VALID_CONTROLS",
        "selected_test_instances": 1, "phase_reports": 3,
        "delivered_selected_records": 1,
        "cases": [{"case_id": "create-new-control-11", "call_phase": "PASSED"}],
        "effect_review_sha256": "a" * 64})
    report["baseline_dispositions"] = {"current_controls": 3,
        "qualified_reused_boundaries": 4, "not_run": 9}
    report["evidence_through"] = "NATIVE09_REVIEWED_POST_DOCKER"
    return report


def test_future_counts_must_match_phase_and_evidence_cursor(monkeypatch):
    report = _future_report()
    assert _project_changed(monkeypatch, report)["baseline_dispositions"]["current_controls"] == 3
    report["attempts"][-1]["phase_reports"] = 0
    with pytest.raises(ValueError, match="LAB_PROGRESS_ATTEMPTS_INVALID"):
        _project_changed(monkeypatch, report)
    report["attempts"][-1]["phase_reports"] = 3
    report["evidence_through"] = "NATIVE08_REVIEWED_PRE_DOCKER"
    with pytest.raises(ValueError, match="LAB_PROGRESS_EVIDENCE_CURSOR_INVALID"):
        _project_changed(monkeypatch, report)


def test_zero_execution_cannot_claim_delivered_or_new_worked_class(monkeypatch):
    report = _future_report()
    report["attempts"][-1].update({"selected_test_instances": 0,
        "phase_reports": 0, "delivered_selected_records": 0, "cases": []})
    report["baseline_dispositions"]["current_controls"] = 2
    report["baseline_dispositions"]["not_run"] = 10
    with pytest.raises(ValueError, match="LAB_PROGRESS_ATTEMPTS_INVALID"):
        _project_changed(monkeypatch, report)
    report = _future_report()
    worked = dict(report["worked_examples"][2])
    worked["case_id"] = "create-new-control-11"
    worked["actual_validation"] = "REVIEWED_CALL_PASSED_GRADE_UNKNOWN"
    worked["readback"] = "REVIEWED_SCOPED_READBACK"
    worked["command_audit"] = "REVIEWED_ONE_COMMAND_ONE_AUDIT"
    report["worked_examples"].append(worked)
    with pytest.raises(ValueError, match="LAB_PROGRESS_WORKED_CLASS_INVALID"):
        _project_changed(monkeypatch, report)


@pytest.mark.parametrize("change", [
    lambda r: r["attempts"][4].update({"name": "Native04"}),
    lambda r: r["attempts"][4].update({"selected_test_instances": True}),
    lambda r: r["attempts"][3]["cases"][0].update({"call_phase": "SUCCESS"}),
    lambda r: r["reused_examples"][0].update({"before_after": "<script>"}),
    lambda r: r["worked_examples"][0].update({"authored_request": "<script>"}),
])
def test_malformed_or_unsafe_reviewed_report_refused(monkeypatch, change):
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    change(report)
    with pytest.raises(ValueError, match="LAB_PROGRESS_"):
        _project_changed(monkeypatch, report)


def test_duplicate_json_key_refused_even_with_matching_pin(monkeypatch):
    raw = REPORT.read_bytes()
    altered = raw.replace(b'"schema": "emr4.stage1_reliability_progress_report.v2",',
        b'"schema": "emr4.stage1_reliability_progress_report.v2", "schema": "fake",', 1)
    digest = hashlib.sha256(altered).hexdigest()
    monkeypatch.setattr(lab, "LAB_PROGRESS_REPORT_SHA", digest)
    with pytest.raises(ValueError, match="LAB_PROGRESS_DUPLICATE_KEY"):
        lab.project_lab_progress(altered, digest)
