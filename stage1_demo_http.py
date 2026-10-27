"""Source-only standalone Stage 1 demo bridge; never include in production main.

The trusted isolated harness constructs this app with a pinned backend ASGI app,
fictional seeded request sessions and one real backend Receptionist bearer. It
sets a cookie out of band via `DemoIssuer.cookie_for`; there is deliberately no
public role/bootstrap endpoint. No application modules are imported here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import asyncio
import hashlib
import json
import math
import re
import secrets
from typing import Any, Awaitable, Callable
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
import httpx

from stage1_demo_adapter_core import AdapterRejected, MAX_BODY_BYTES, SessionBinding, admit_action
from stage1_staff_diary_read import list_path, render_staff_diary_read, unavailable as diary_unavailable
from stage1_demo_intent import interpret_words, IntentRejected
from stage1_demo_voice import (MAX_WAV_BYTES, VoiceInputRejected, VoiceRecognitionUnavailable,
                               ContainedVoiceRuntimeBinding, SpeechComponentVoiceBinding,
                               VoiceRuntimeBinding,
                               run_local_recognizer, target_for_persona,
                               validate_wav)
from stage1_mock_org_bridge import StaffMockBinding, StaffMockDenied


BASE = "/api/v1/appointments"
COOKIE = "stage1_demo_session"
STATIC = Path(__file__).parent / "static" / "demo"
UI_VIEW = STATIC
UI_CONTROLLER = STATIC
LOCAL_MINUTE = re.compile(r"(?:[01]\d|2[0-3]):[0-5]\d(?::00(?:\.0+)?)?\Z")
LAB_CATALOG_SHA = "8cc1ae403b898aecc8dca8f25e5f2c209b272c5a4fac6231e96f8e6ef238cf43"
LAB_SOURCE_SCHEMA = "emr4.stage1_outcome_integrated_seam_report.v1"
LAB_GRADE_SCHEMA = "emr4.appointment_outcome_report.v4"
NATIVE04_INPUTS = {
    "result": (25515, "857e3e0243476ba4b2a6024ae613f4598c7c2d321685ab2a500b754ffd363167"),
    "primary": (3457, "76a83146a5179dd9514c649ccb2c57a00a6cdd184dd7ce4e0605f02b7c470672"),
    "effect_review": (8060, "b8bb1b6e2de75bf0a5376c61287116564e8147bbada3149a5c25810c2bc30d06"),
    "existing_review": (10025, "909d7e8f51b2c3e2009c665194fc3219fa629cd564da296ec6ec14b7e60c0e70"),
}
LAB_PROGRESS_REPORT_SHA = "51ef618862352719a331237d286297dba2f4c0e6155d19c6d397ac141bfd3065"
LAB_PROGRESS_HISTORICAL_PREFIX_SHA = "68a797992a13809c0589e8fcfa58b392eadb824672437b7ef1d9ba2c3b70edbe"
def project_lab_progress(raw: bytes | None, digest: str | None) -> dict[str, Any] | None:
    """Closed projection of one trusted startup-pinned authored progress report.

    The immutable prefix freezes all five historical attempts and their worked
    examples. Later attempts are data in a separately reviewed report, pinned
    once at startup; a digest or effect-review SHA alone is not acceptance.
    Native04 provenance remains independently checked below.
    """
    if raw is None and digest is None:
        return None
    if (type(raw) is not bytes or not 1 <= len(raw) <= 65536 or
            type(digest) is not str or digest != LAB_PROGRESS_REPORT_SHA or
            hashlib.sha256(raw).hexdigest() != digest):
        raise ValueError("LAB_PROGRESS_BINDING_INVALID")

    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("LAB_PROGRESS_DUPLICATE_KEY")
            result[key] = value
        return result

    try:
        report = json.loads(raw.decode("utf-8"), object_pairs_hook=unique)
    except (UnicodeError, json.JSONDecodeError):
        raise ValueError("LAB_PROGRESS_JSON_INVALID") from None
    fixed = {"schema", "status", "catalog_sha256", "catalog_cases",
             "catalog_families", "baseline_dispositions", "attempts",
             "reused_examples", "worked_examples", "authored_catalog_sha256",
             "evidence_through", "native04_primary_sha256", "native04_result_sha256",
             "request_detail", "proposal_detail", "actual_model",
             "m1_model_binding", "generated_silence_voice", "genuine_ptt_voice",
             "whole_journey_grade", "display", "disclosure"}
    if (type(report) is not dict or set(report) != fixed or
            report["schema"] != "emr4.stage1_reliability_progress_report.v2" or
            type(report["status"]) is not str or
            report["status"] not in {"REVIEWED_NONPASS_EFFECT_ACCOUNTING",
                                      "REVIEWED_PARTIAL_EFFECT_ACCOUNTING",
                                      "REVIEWED_COMPLETE_EFFECT_ACCOUNTING"} or
            report["catalog_sha256"] != LAB_CATALOG_SHA or
            report["native04_primary_sha256"] != NATIVE04_INPUTS["primary"][1] or
            report["native04_result_sha256"] != NATIVE04_INPUTS["result"][1] or
            report["catalog_cases"] != 16 or report["catalog_families"] != 11 or
            type(report["authored_catalog_sha256"]) is not str or
            re.fullmatch(r"[0-9a-f]{64}", report["authored_catalog_sha256"]) is None or
            type(report["evidence_through"]) is not str or
            re.fullmatch(r"NATIVE[0-9]{2,3}_REVIEWED_[A-Z_]{1,48}", report["evidence_through"]) is None):
        raise ValueError("LAB_PROGRESS_UNSUPPORTED_REPORT")
    dispositions = report["baseline_dispositions"]
    if (type(dispositions) is not dict or set(dispositions) !=
            {"current_controls", "qualified_reused_boundaries", "not_run"} or
            any(type(value) is not int or not 0 <= value <= 16
                for value in dispositions.values()) or
            sum(dispositions.values()) != 16 or
            (report["status"] == "REVIEWED_COMPLETE_EFFECT_ACCOUNTING" and
             dispositions["not_run"] != 0)):
        raise ValueError("LAB_PROGRESS_DISPOSITIONS_INVALID")
    attempts = report["attempts"]
    examples = report["reused_examples"]
    worked = report["worked_examples"]
    if (type(attempts) is not list or len(attempts) < 5 or
            type(examples) is not list or len(examples) < 4 or
            type(worked) is not list or len(worked) < 4):
        raise ValueError("LAB_PROGRESS_HISTORICAL_PREFIX_INVALID")
    historical = {"attempts": attempts[:5], "reused_examples": examples[:4],
                  "worked_examples": worked[:4]}
    historical_bytes = json.dumps(historical, sort_keys=True, separators=(",", ":"),
                                  ensure_ascii=True).encode("utf-8")
    if hashlib.sha256(historical_bytes).hexdigest() != LAB_PROGRESS_HISTORICAL_PREFIX_SHA:
        raise ValueError("LAB_PROGRESS_HISTORICAL_PREFIX_INVALID")
    attempt_keys = {"name", "status", "selected_test_instances", "phase_reports",
                    "delivered_selected_records", "cases", "effect_review_sha256"}
    statuses = {"DELIVERED_VALID_CONTROLS", "PARTIAL_DELIVERED_CONTROLS",
                "NONPASS_NO_DELIVERED_SELECTED_RECORDS", "PRE_DOCKER_LAUNCH_FAILURE"}
    phases = {"PASSED", "FAILED", "NOT_RUN"}
    if len(attempts) > 32:
        raise ValueError("LAB_PROGRESS_ATTEMPTS_INVALID")
    seen_attempts: set[str] = set()
    delivered_ids: set[str] = set()
    for attempt in attempts:
        if (type(attempt) is not dict or set(attempt) != attempt_keys or
                type(attempt["name"]) is not str or
                re.fullmatch(r"Native[0-9]{2,3}", attempt["name"]) is None or
                attempt["name"] in seen_attempts or type(attempt["status"]) is not str or
                attempt["status"] not in statuses or
                type(attempt["effect_review_sha256"]) is not str or
                re.fullmatch(r"[0-9a-f]{64}", attempt["effect_review_sha256"]) is None or
                any(type(attempt[key]) is not int or not 0 <= attempt[key] <= 32
                    for key in ("selected_test_instances", "phase_reports",
                                "delivered_selected_records")) or
                type(attempt["cases"]) is not list or
                len(attempt["cases"]) != attempt["selected_test_instances"] or
                attempt["phase_reports"] > 3 * attempt["selected_test_instances"] or
                attempt["delivered_selected_records"] > attempt["selected_test_instances"] or
                (attempt["status"] == "DELIVERED_VALID_CONTROLS" and
                 attempt["selected_test_instances"] == 0) or
                (attempt["status"] == "NONPASS_NO_DELIVERED_SELECTED_RECORDS" and
                 attempt["selected_test_instances"] == 0)):
            raise ValueError("LAB_PROGRESS_ATTEMPTS_INVALID")
        seen_attempts.add(attempt["name"])
        seen_cases: set[str] = set()
        passed: set[str] = set()
        for case in attempt["cases"]:
            if (type(case) is not dict or set(case) != {"case_id", "call_phase"} or
                    type(case["case_id"]) is not str or
                    re.fullmatch(r"[a-z0-9-]{1,64}", case["case_id"]) is None or
                    case["case_id"] in seen_cases or
                    type(case["call_phase"]) is not str or case["call_phase"] not in phases):
                raise ValueError("LAB_PROGRESS_CASE_PHASES_INVALID")
            seen_cases.add(case["case_id"])
            if case["call_phase"] == "PASSED":
                passed.add(case["case_id"])
        if (attempt["delivered_selected_records"] > len(passed) or
                (passed and attempt["phase_reports"] < len(passed)) or
                (attempt["status"] == "DELIVERED_VALID_CONTROLS" and
                 (attempt["delivered_selected_records"] != len(passed) or
                  len(passed) != len(attempt["cases"]))) or
                (attempt["status"] == "PARTIAL_DELIVERED_CONTROLS" and
                 not 0 < attempt["delivered_selected_records"] < len(attempt["cases"])) or
                (attempt["status"] in {"NONPASS_NO_DELIVERED_SELECTED_RECORDS",
                                       "PRE_DOCKER_LAUNCH_FAILURE"} and
                 attempt["delivered_selected_records"] != 0) or
                (attempt["status"] == "PRE_DOCKER_LAUNCH_FAILURE" and
                 (attempt["selected_test_instances"] or attempt["phase_reports"]))):
            raise ValueError("LAB_PROGRESS_ATTEMPTS_INVALID")
        if attempt["status"] == "DELIVERED_VALID_CONTROLS":
            delivered_ids.update(passed)
        elif attempt["status"] == "PARTIAL_DELIVERED_CONTROLS":
            # The aggregate is insufficient to identify which passed call was
            # delivered; do not count it as a current named control here.
            pass
    if (attempts[0]["name"] != "Native04" or
            attempts[0]["effect_review_sha256"] != NATIVE04_INPUTS["effect_review"][1] or
            attempts[0]["delivered_selected_records"] != 2 or
            attempts[0]["cases"] != [
                {"case_id": "create-valid-01", "call_phase": "PASSED"},
                {"case_id": "move-valid-timeonly-01", "call_phase": "PASSED"}] or
            len(delivered_ids) != dispositions["current_controls"]):
        raise ValueError("LAB_PROGRESS_PROVENANCE_INVALID")
    if not report["evidence_through"].startswith(attempts[-1]["name"].upper() + "_REVIEWED_"):
        raise ValueError("LAB_PROGRESS_EVIDENCE_CURSOR_INVALID")
    example_keys = {"case_id", "disturbance", "actual_validation", "before_after", "outcome"}
    if (type(examples) is not list or len(examples) != dispositions["qualified_reused_boundaries"] or
            len(examples) > 16):
        raise ValueError("LAB_PROGRESS_EXAMPLES_INVALID")
    seen_examples: set[str] = set()
    for example in examples:
        if (type(example) is not dict or set(example) != example_keys or
                any(type(value) is not str or re.fullmatch(r"[A-Za-z0-9_-]{1,96}", value) is None
                    for value in example.values()) or
                example["case_id"] in seen_examples or
                example["case_id"] in delivered_ids or
                example["outcome"] != "QUALIFIED_REUSED_BOUNDARY_ONLY"):
            raise ValueError("LAB_PROGRESS_EXAMPLES_INVALID")
        seen_examples.add(example["case_id"])
    for example in examples[4:]:
        if (example["actual_validation"] not in
                {"REVIEWED_REFUSAL_UNCHANGED_SNAPSHOT", "SEPARATE_REFUSAL_TESTS"} or
                example["before_after"] not in
                {"REVIEWED_UNCHANGED_SNAPSHOT", "NOT_IN_DELIVERED_PROJECTION"}):
            raise ValueError("LAB_PROGRESS_EXAMPLES_INVALID")
    worked_keys = {"case_id", "evidence_kind", "authored_request",
                   "authored_expected_proposal", "proposal_observation",
                   "actual_validation", "before_after", "readback", "command_audit",
                   "outcome"}
    if type(worked) is not list or len(worked) > 16:
        raise ValueError("LAB_PROGRESS_WORKED_EXAMPLES_INVALID")
    seen_worked: set[str] = set()
    for index, item in enumerate(worked):
        if (type(item) is not dict or set(item) != worked_keys or
                type(item["before_after"]) is not dict or
                set(item["before_after"]) != {"before", "after"} or
                type(item["case_id"]) is not str or item["case_id"] in seen_worked or
                item["case_id"] not in delivered_ids | seen_examples or
                any(type(value) is not str or
                    re.fullmatch(r"[A-Za-z0-9 .,:;/'()_+\-]{1,512}", value) is None
                    for key, value in item.items() if key != "before_after") or
                any(type(value) is not str or
                    re.fullmatch(r"[A-Za-z0-9 .,:;/'()_+\-]{1,512}", value) is None
                    for value in item["before_after"].values()) or
                item["proposal_observation"] not in
                    {"NOT_IN_DELIVERED_PROJECTION", "OBSERVED_IN_REVIEWED_RECORD"}):
            raise ValueError("LAB_PROGRESS_WORKED_EXAMPLES_INVALID")
        current = item["case_id"] in delivered_ids
        if ((current and (item["evidence_kind"] not in
                         {"NATIVE04_DELIVERED_CONTROL", "CURRENT_DELIVERED_CONTROL"} or
                         item["outcome"] not in
                         {"DELIVERED_SOURCE_PROJECTION_EXTERNAL_RUNTIME_QUALIFIED_GRADE_UNKNOWN",
                          "CURRENT_DELIVERED_CONTROL_GRADE_UNKNOWN"})) or
                (not current and (item["evidence_kind"] != "QUALIFIED_REUSED_BOUNDARY" or
                                  item["outcome"] != "QUALIFIED_REUSED_BOUNDARY_ONLY")) or
                (item["evidence_kind"] == "NATIVE04_DELIVERED_CONTROL" and
                 item["case_id"] not in {"create-valid-01", "move-valid-timeonly-01"})):
            raise ValueError("LAB_PROGRESS_WORKED_CLASS_INVALID")
        if index >= 4 and (item["actual_validation"] not in
                {"REVIEWED_CALL_PASSED_GRADE_UNKNOWN", "REVIEWED_REFUSAL_UNCHANGED_SNAPSHOT"} or
                item["readback"] not in
                {"REVIEWED_SCOPED_READBACK", "NOT_IN_DELIVERED_PROJECTION"} or
                item["command_audit"] not in
                {"REVIEWED_ONE_COMMAND_ONE_AUDIT", "NOT_IN_DELIVERED_PROJECTION"}):
            raise ValueError("LAB_PROGRESS_WORKED_CLASS_INVALID")
        seen_worked.add(item["case_id"])
    field_values = {"request_detail": {"NOT_IN_DELIVERED_PROJECTION", "REVIEWED"},
                    "proposal_detail": {"NOT_IN_DELIVERED_PROJECTION", "REVIEWED"},
                    "actual_model": {"NOT_RUN", "REVIEWED"},
                    "m1_model_binding": {"OPEN", "REVIEWED"},
                    "generated_silence_voice": {"NOT_RUN_AS_SPEECH_TEST", "REVIEWED"},
                    "genuine_ptt_voice": {"NOT_RUN", "REVIEWED"},
                    "whole_journey_grade": {"UNKNOWN", "REVIEWED"},
                    "display": {"NOT_OBSERVED", "REVIEWED"},
                    "disclosure": {"NOT_OBSERVED", "REVIEWED"}}
    if any(type(report[key]) is not str or report[key] not in allowed
           for key, allowed in field_values.items()):
        raise ValueError("LAB_PROGRESS_STATUS_INVALID")
    return {"schema": "emr4.stage1_reliability_progress_view.v2",
            "report_basis": "STARTUP_PINNED_AUTHORED_REPORT",
            "catalog_cases": report["catalog_cases"],
            "catalog_families": report["catalog_families"],
            "authored_catalog_sha256": report["authored_catalog_sha256"],
            "evidence_through": report["evidence_through"],
            "baseline_dispositions": dispositions, "attempts": attempts,
            "reused_examples": examples, "worked_examples": worked,
            **{key: report[key] for key in field_values}}


def _lab_count(value: Any) -> bool:
    return type(value) is int and 0 <= value <= 10000


def _lab_counts(value: Any, keys: set[str]) -> dict[str, int]:
    if (type(value) is not dict or set(value) != keys or
            any(not _lab_count(item) for item in value.values())):
        raise ValueError("LAB_REPORT_UNSAFE_COUNTS")
    return value


def _lab_label(value: Any) -> str:
    if type(value) is not str or re.fullmatch(r"[A-Za-z0-9_./-]{1,64}", value) is None:
        raise ValueError("LAB_REPORT_UNSAFE_LABEL")
    return value


def project_reliability_lab(raw: bytes | None, digest: str | None) -> dict[str, Any]:
    """Project one startup-bound report; never return records or authority-bearing fields."""
    empty = {"schema": "emr4.stage1_reliability_lab_view.v1", "status": "NOT_RUN",
             "origin": "NOT_BOUND", "source_schema": None,
             "catalog_sha256": LAB_CATALOG_SHA,
             "catalog_cases": 16, "catalog_families": 11,
             "groups": [], "actual_model": "NOT_RUN", "voice": "NOT_RUN",
             "external_runtime_qualification": "NOT_BOUND",
             "worked_examples": "NOT_AVAILABLE_IN_BOUND_REPORT"}
    if raw is None and digest is None:
        return empty
    if (type(raw) is not bytes or not 0 < len(raw) <= 131072 or
            type(digest) is not str or re.fullmatch(r"[0-9a-f]{64}", digest) is None or
            hashlib.sha256(raw).hexdigest() != digest):
        raise ValueError("LAB_REPORT_BINDING_INVALID")
    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result = {}
        for key, item in pairs:
            if key in result:
                raise ValueError("LAB_REPORT_DUPLICATE_KEY")
            result[key] = item
        return result
    try:
        value = json.loads(raw, object_pairs_hook=unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("LAB_REPORT_JSON_INVALID") from None
    if (type(value) is not dict or set(value) != {
            "schema", "origin", "catalog_sha256", "catalog_cases",
            "catalog_assessment_cases", "catalog_challenge_cases", "catalog_families",
            "selected_case_capacity", "records", "unrun_baseline_or_model",
            "canonical_link_nonpass", "unresolved_patient_readback",
            "unresolved_singleton_readback", "supplied_record_grades",
            "grader_report", "actual_model", "voice", "external_runtime_qualification"} or
            value.get("schema") != LAB_SOURCE_SCHEMA or
            value.get("origin") != "UNQUALIFIED_SOURCE_SEAM" or
            value.get("catalog_sha256") != LAB_CATALOG_SHA or
            value.get("catalog_cases") != 16 or
            value.get("catalog_assessment_cases") != 6 or
            value.get("catalog_challenge_cases") != 10 or
            value.get("catalog_families") != 11 or
            value.get("selected_case_capacity") != 2 or
            value.get("actual_model") != "NOT_RUN" or value.get("voice") != "NOT_RUN" or
            value.get("external_runtime_qualification") != "NOT_BOUND" or
            not _lab_count(value.get("records")) or value["records"] > 2 or
            not _lab_count(value.get("supplied_record_grades")) or
            value["supplied_record_grades"] > value["records"] or
            any(not _lab_count(value.get(key)) or value[key] > value["records"]
                for key in ("unrun_baseline_or_model", "canonical_link_nonpass",
                    "unresolved_patient_readback", "unresolved_singleton_readback"))):
        raise ValueError("LAB_REPORT_UNSUPPORTED_SOURCE")
    report = value.get("grader_report")
    if value["supplied_record_grades"] == 0:
        if report is not None:
            raise ValueError("LAB_REPORT_GRADE_MISMATCH")
        return {**empty, "status": "BOUND_UNGRADED",
                "origin": "UNQUALIFIED_SOURCE_SEAM",
                "source_schema": LAB_SOURCE_SCHEMA,
                "records": value["records"], "unrun": value["unrun_baseline_or_model"],
                "canonical_link_nonpass": value["canonical_link_nonpass"],
                "unresolved_patient_readback": value["unresolved_patient_readback"],
                "unresolved_singleton_readback": value["unresolved_singleton_readback"]}
    if (type(report) is not dict or set(report) != {"schema", "groups", "warning"} or
            report.get("schema") != LAB_GRADE_SCHEMA or
            report.get("warning") !=
                "Descriptive synthetic evidence only; groups are not pooled into a risk rate or confidence claim." or
            type(report.get("groups")) is not list or not 1 <= len(report["groups"]) <= 2):
        raise ValueError("LAB_REPORT_GRADE_VERSION")
    groups = []
    outcome_keys = {"CORRECT", "INCORRECT", "UNKNOWN"}
    containment_keys = {"CONTAINED", "RECOVERED_BY_OBSERVED_HUMAN",
        "OUTCOME_CORRECT_CAUSE_UNRESOLVED", "NOT_CONTAINED", "UNRESOLVED"}
    proposal_keys = {"CORRECT", "WRONG_PROPOSAL", "WRONG_BUT_PERMITTED_EXPOSED",
        "CORRECT_NO_PROPOSAL", "CORRECT_CLARIFICATION", "CORRECT_OPTIONS_ONLY",
        "CORRECT_RECONCILIATION", "MISSING_PROPOSAL", "UNKNOWN"}
    for group in report["groups"]:
        if (type(group) is not dict or set(group) != {
                "catalog_sha256", "set_kind", "journey", "channel", "boundaries",
                "evidence_class", "configuration", "unique_cases", "unique_families",
                "episodes", "repeat_trials", "counts", "missing_count_observations",
                "final_outcomes", "semantic_proposals", "wrong_proposals_reaching_review",
                "proposal_review_observation_missing", "natural_error_containment",
                "deliberate_challenge_containment", "measured_latency_ms",
                "measured_cost_usd"}):
            raise ValueError("LAB_REPORT_GROUP_INVALID")
        for key in ("set_kind", "journey", "channel", "evidence_class"):
            _lab_label(group.get(key))
        if (group.get("catalog_sha256") != LAB_CATALOG_SHA or
                group["set_kind"] not in {"assessment", "challenge"} or
                group["journey"] not in {"create", "move"} or
                group["channel"] not in {"text", "voice"} or
                group["evidence_class"] != "SOURCE_ONLY_SUPPLIED_RECORD" or
                type(group.get("configuration")) is not dict or
                type(group.get("semantic_proposals")) is not dict or
                not _lab_count(group.get("wrong_proposals_reaching_review")) or
                not _lab_count(group.get("proposal_review_observation_missing")) or
                type(group.get("measured_latency_ms")) is not list or
                type(group.get("measured_cost_usd")) is not list or
                len(group["measured_latency_ms"]) > 2 or
                len(group["measured_cost_usd"]) > 2 or
                any(type(item) not in (int, float) or not math.isfinite(item) or
                    item < 0 for item in group["measured_latency_ms"] +
                    group["measured_cost_usd"]) or
                not _lab_count(group.get("unique_cases")) or
                not _lab_count(group.get("unique_families")) or
                not _lab_count(group.get("episodes")) or
                not _lab_count(group.get("repeat_trials")) or
                not 1 <= group["episodes"] <= 2 or
                not 1 <= group["unique_cases"] <= group["episodes"] or
                not 1 <= group["unique_families"] <= group["episodes"] or
                group["repeat_trials"] > group["episodes"] or
                type(group.get("boundaries")) is not list or
                any(type(boundary) is not str or boundary not in
                    {"actual_model", "integrated", "error_injection"}
                    for boundary in group["boundaries"])):
            raise ValueError("LAB_REPORT_GROUP_SCOPE")
        outcomes = _lab_counts(group.get("final_outcomes"), outcome_keys)
        proposals = _lab_counts(group.get("semantic_proposals"), proposal_keys)
        aggregate_counts = _lab_counts(group.get("counts"),
            {"eligible_attempts", "actual_commits", "model_error_episodes"})
        if (sum(outcomes.values()) != group["episodes"] or
                sum(proposals.values()) != group["episodes"] or
                group["wrong_proposals_reaching_review"] > group["episodes"] or
                group["proposal_review_observation_missing"] > group["episodes"]):
            raise ValueError("LAB_REPORT_OUTCOME_COUNT")
        missing = _lab_counts(group.get("missing_count_observations"),
            {"eligible_attempts", "actual_commits", "model_error_episodes"})
        if any(item > group["episodes"] for item in missing.values()):
            raise ValueError("LAB_REPORT_MISSING_COUNT")
        containment = {}
        for key in ("natural_error_containment", "deliberate_challenge_containment"):
            part = group.get(key)
            if (type(part) is not dict or set(part) != {"denominator", "status", "counts"} or
                    not _lab_count(part.get("denominator")) or
                    part["denominator"] > group["episodes"] or
                    part.get("status") != ("DESCRIPTIVE_COUNTS" if part["denominator"]
                         else "NOT_APPLICABLE")):
                raise ValueError("LAB_REPORT_CONTAINMENT_SCOPE")
            part_counts = _lab_counts(part.get("counts"), containment_keys)
            if sum(part_counts.values()) != part["denominator"]:
                raise ValueError("LAB_REPORT_CONTAINMENT_COUNT")
            containment[key] = {"denominator": part["denominator"],
                "status": part["status"], "counts": part_counts}
        groups.append({"set_kind": group["set_kind"], "journey": group["journey"],
            "channel": group["channel"], "evidence_class": group["evidence_class"],
            "boundaries": group["boundaries"],
            "unique_cases": group["unique_cases"],
            "unique_families": group["unique_families"],
            "episodes": group["episodes"], "repeat_trials": group["repeat_trials"],
            "final_outcomes": outcomes, "counts": aggregate_counts,
            "missing_count_observations": missing,
            **containment,
            "latency": "NOT_MEASURED" if not group.get("measured_latency_ms") else "MEASURED_VALUES_WITHHELD",
            "cost": "NOT_MEASURED" if not group.get("measured_cost_usd") else "MEASURED_VALUES_WITHHELD"})
    if sum(group["episodes"] for group in groups) != value["supplied_record_grades"]:
        raise ValueError("LAB_REPORT_EPISODE_COUNT")
    return {**empty, "status": "SUPPLIED_RECORD_GRADES_ONLY",
        "origin": "UNQUALIFIED_SOURCE_SEAM", "source_schema": LAB_SOURCE_SCHEMA,
        "records": value["records"],
        "unrun": value["unrun_baseline_or_model"],
        "canonical_link_nonpass": value["canonical_link_nonpass"],
        "unresolved_patient_readback": value["unresolved_patient_readback"],
        "unresolved_singleton_readback": value["unresolved_singleton_readback"],
        "groups": groups}


def project_native04_controls(result_raw: bytes | None, primary_raw: bytes | None,
                              effect_raw: bytes | None,
                              existing_raw: bytes | None) -> dict[str, Any] | None:
    """Project four exact startup-bound ordinary records; expose no raw records."""
    supplied = (result_raw, primary_raw, effect_raw, existing_raw)
    if all(item is None for item in supplied):
        return None
    if any(item is None for item in supplied):
        raise ValueError("LAB_NATIVE04_BINDING_INCOMPLETE")

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError("LAB_NATIVE04_DUPLICATE_KEY")
            value[key] = item
        return value

    decoded = {}
    for name, raw in zip(NATIVE04_INPUTS, supplied):
        size, digest = NATIVE04_INPUTS[name]
        if (type(raw) is not bytes or len(raw) != size or
                hashlib.sha256(raw).hexdigest() != digest):
            raise ValueError("LAB_NATIVE04_PIN_MISMATCH")
        try:
            decoded[name] = json.loads(raw, object_pairs_hook=unique_object)
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ValueError("LAB_NATIVE04_JSON_INVALID") from None

    result, primary = decoded["result"], decoded["primary"]
    effect, existing = decoded["effect_review"], decoded["existing_review"]
    if (type(result) is not dict or result.get("schema") != "stage1-child-result.v1" or
            result.get("status") != "PASS" or result.get("primary") != primary or
            result.get("primary_sha256") != NATIVE04_INPUTS["primary"][1] or
            type(primary) is not dict or primary.get("status") != "PASS" or
            primary.get("collection_attempts") != 1 or
            primary.get("collection_errors") != 0 or
            primary.get("internal_errors") != 0 or
            primary.get("collected") != [
                "test_stage1_outcome_matched_create.py::test_fictional_create_valid_01_canonical_request_confirm_readback",
                "test_stage1_outcome_matched_move.py::test_move_valid_timeonly_01_canonical_signed_confirm_and_readback"] or
            type(effect) is not dict or
            effect.get("schema") != "emr4.stage1_outcome_result_delivery_effect_review.v2" or
            effect.get("verdict") !=
                "PASS_NATIVE04_TWO_SYNTHETIC_CASES_DELIVERED_BOUNDED_EPISODE_PROJECTION_AND_CLEANUP" or
            effect.get("independent") is not True or
            effect.get("implementation_authorship") is not False or
            effect.get("decoded_stage1_result_sha256") != NATIVE04_INPUTS["result"][1] or
            effect.get("decoded_stage1_primary_sha256") != NATIVE04_INPUTS["primary"][1] or
            effect.get("reviewed_effect", {}).get("delivered_versioned_episode_records") != 2 or
            effect.get("reviewed_effect", {}).get("phase_reports") != 6 or
            effect.get("reviewed_effect", {}).get("cases") != primary["collected"] or
            effect.get("reviewed_effect", {}).get("new_unique_case_coverage") != 0 or
            type(existing) is not dict or
            existing.get("schema") != "emr4.stage1_outcome_existing_evidence_review.v1" or
            existing.get("catalogue", {}).get("sha256") != LAB_CATALOG_SHA):
        raise ValueError("LAB_NATIVE04_PROVENANCE_INVALID")
    dispositions = existing.get("case_dispositions")
    if (type(dispositions) is not list or len(dispositions) != 16 or
            len({item.get("case_id") for item in dispositions if type(item) is dict}) != 16):
        raise ValueError("LAB_NATIVE04_CASE_DISPOSITIONS")
    counts = {kind: sum(item.get("disposition") == kind for item in dispositions)
              for kind in ("CURRENT_INTEGRATED_EVIDENCE",
                           "QUALIFIED_REUSED_BOUNDARY_EVIDENCE", "NOT_RUN")}
    if counts != {"CURRENT_INTEGRATED_EVIDENCE": 2,
                  "QUALIFIED_REUSED_BOUNDARY_EVIDENCE": 4, "NOT_RUN": 10}:
        raise ValueError("LAB_NATIVE04_CASE_DISPOSITIONS")

    selected = primary.get("selected_results")
    if (type(selected) is not dict or
            selected.get("schema") != "emr4.stage1_outcome_selected_results.v1" or
            selected.get("status") != "SOURCE_PROJECTION_ONLY" or
            selected.get("origin") != "UNQUALIFIED_SOURCE_SEAM" or
            selected.get("summary") != {
                "episode_count": 2, "external_runtime_qualification": "NOT_BOUND",
                "final_grade": "UNKNOWN", "model": "NOT_RUN",
                "phase_reports": None, "voice": "NOT_RUN"} or
            type(selected.get("episodes")) is not list or
            len(selected["episodes"]) != 2):
        raise ValueError("LAB_NATIVE04_SOURCE_PROJECTION")

    def appointment(value: Any) -> dict[str, Any] | None:
        if value is None:
            return None
        if (type(value) is not dict or set(value) !=
                {"date", "start_local", "state_version", "status"} or
                type(value["date"]) is not str or
                re.fullmatch(r"20\d{2}-\d{2}-\d{2}", value["date"]) is None or
                type(value["start_local"]) is not str or
                re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", value["start_local"]) is None or
                not _lab_count(value["state_version"]) or
                value["status"] != "Booked"):
            raise ValueError("LAB_NATIVE04_APPOINTMENT")
        return {"date": value["date"], "start_local": value["start_local"],
                "status": "Booked"}

    controls = []
    expected = (("create-valid-01", "create"),
                ("move-valid-timeonly-01", "move"))
    for episode, (case_id, journey) in zip(selected["episodes"], expected):
        if (type(episode) is not dict or episode.get("case_id") != case_id or
                episode.get("journey") != journey or
                episode.get("mode") != "integrated" or
                episode.get("channel") != "text" or
                episode.get("repeat") != 1 or
                type(episode.get("observed")) is not dict):
            raise ValueError("LAB_NATIVE04_CONTROL_IDENTITY")
        observed = episode["observed"]
        before, after = observed.get("before"), observed.get("after")
        if (observed.get("status") != "SUPPLIED_RECORD_GRADED" or
                observed.get("grade") != "UNKNOWN" or
                observed.get("attempted") is not True or
                observed.get("display") != "NOT_OBSERVED" or
                observed.get("confirmation_human") != "UNKNOWN" or
                observed.get("canonical_link_issue_codes") != [] or
                observed.get("latency_ms") is not None or
                observed.get("usage") is not None or
                type(before) is not dict or type(after) is not dict or
                set(before) != {"appointment_count", "request_state", "selected_appointment"} or
                set(after) != set(before) or
                not _lab_count(before["appointment_count"]) or
                not _lab_count(after["appointment_count"]) or
                before["appointment_count"] > 2 or after["appointment_count"] > 2 or
                before["request_state"] not in (None, "submitted", "booked") or
                after["request_state"] not in (None, "submitted", "booked") or
                observed.get("new_command_count") != 1 or
                observed.get("new_audit_count") != 1 or
                observed.get("current_readback") not in ("TRUE", "UNKNOWN") or
                observed.get("patient_readback") not in ("TRUE", "UNKNOWN") or
                observed.get("source_readback") not in ("TRUE", "UNKNOWN")):
            raise ValueError("LAB_NATIVE04_CONTROL_OBSERVATION")
        controls.append({"case_id": case_id, "journey": journey,
            "before": {"appointment_count": before["appointment_count"],
                       "request_state": before["request_state"],
                       "appointment": appointment(before["selected_appointment"])},
            "after": {"appointment_count": after["appointment_count"],
                      "request_state": after["request_state"],
                      "appointment": appointment(after["selected_appointment"])},
            "new_command_count": 1, "new_audit_count": 1,
            "current_readback": observed["current_readback"],
            "patient_readback": observed["patient_readback"],
            "source_readback": observed["source_readback"],
            "grade": "UNKNOWN", "display": "NOT_OBSERVED",
            "request_detail": "NOT_IN_DELIVERED_PROJECTION",
            "proposal_detail": "NOT_IN_DELIVERED_PROJECTION",
            "validation_detail": "NOT_IN_DELIVERED_PROJECTION"})
    return {"schema": "emr4.stage1_reliability_native04_view.v1",
        "qualification": "EXTERNALLY_REVIEWED_RESULT_DELIVERY_ONLY",
        "effect_review_sha256": NATIVE04_INPUTS["effect_review"][1],
        "source_origin": "UNQUALIFIED_SOURCE_SEAM",
        "internal_runtime_binding": "NOT_BOUND", "internal_grade": "UNKNOWN",
        "actual_model": "NOT_RUN", "voice": "NOT_RUN",
        "current_controls": counts["CURRENT_INTEGRATED_EVIDENCE"],
        "qualified_reused_boundaries": counts["QUALIFIED_REUSED_BOUNDARY_EVIDENCE"],
        "not_run_catalog_cases": counts["NOT_RUN"],
        "new_unique_case_coverage": 0, "phase_reports_for_two_controls": 6,
        "controls": controls}


def local_minute(value: Any) -> str | None:
    return value[:5] if isinstance(value, str) and LOCAL_MINUTE.fullmatch(value) else None


def project_bureau_move(reply: Any, current: dict[str, Any],
                        correlation_id: str) -> dict[str, str] | None:
    """Project one clean Bureau option into editable fields, without authority.

    Multiple options need an explicit choice; the Bureau's first-slot summary
    is not such a choice. Rejected reply content is never returned to the UI.
    The later move proposal still rechecks the original appointment/version.
    Bureau display labels are never used as identity evidence or rendered;
    the screen keeps the current server-verified appointment's identity.
    """
    if type(reply) is not dict or any(reply.get(key) != value for key, value in {
            "contract_version": "reception.one.product-context-proposal.v1",
            "result": "proposal_ready", "planner_mode": "deterministic",
            "data_class": "authored_synthetic",
            "operation_id": "proposeAppointmentUpdate"}.items()):
        return None
    opaque_correlation = reply.get("correlation_id")
    request_digest = reply.get("request_correlation_sha256")
    if (type(opaque_correlation) is not str
            or re.fullmatch(r"synthetic-correlation-[0-9a-f]{20}", opaque_correlation) is None
            or type(request_digest) is not str
            or re.fullmatch(r"[0-9a-f]{64}", request_digest) is None
            or type(correlation_id) is not str
            or request_digest != hashlib.sha256(correlation_id.encode("utf-8")).hexdigest()):
        return None
    if (any(reply.get(key) is not True for key in (
                "safe", "requires_confirmation", "proposal_only", "database_reads_performed"))
            or any(reply.get(key) is not False for key in (
                "write_performed", "confirmation_performed", "model_database_access",
                "legacy_interpreter_gate_changed"))
            or type(reply.get("provider_calls")) is not int or reply["provider_calls"] != 0):
        return None
    notices = reply.get("warning_codes")
    required_notices = {"staff_confirmation_required", "staff_selection_required"}
    if (type(notices) is not list or len(notices) > 20
            or any(type(code) is not str for code in notices)
            or len(set(notices)) != len(notices)
            or not required_notices <= set(notices)
            or not set(notices) <= required_notices | {"no_reservation"}):
        return None
    review = reply.get("review")
    revision = reply.get("context_revision")
    if (type(revision) is not int or revision < 1 or type(review) is not dict
            or review.get("disposition") != "admit"
            or type(review.get("context_revision")) is not int
            or review.get("context_revision") != revision):
        return None
    selected = reply.get("selected_appointment")
    if (type(selected) is not dict or current.get("status") != "Booked"
            or selected.get("appointment_date") != current.get("date")
            or local_minute(selected.get("start_time_local")) != current.get("start_local")
            or selected.get("status") != "booked"
            or type(selected.get("duration_minutes")) is not int
            or selected["duration_minutes"] != current.get("duration_minutes")):
        return None
    slots = reply.get("candidate_slots")
    adapter = reply.get("adapter_review")
    if (type(slots) is not list or len(slots) != 1 or type(slots[0]) is not dict
            or type(adapter) is not dict or adapter.get("adapter_kind") != "update_proposal"
            or any(adapter.get(key) is not True for key in (
                "performed", "safe", "freshness_verified"))
            or any(adapter.get(key) is not False for key in (
                "confirmation_evidence_released", "write_performed"))
            or adapter.get("warning_codes") not in ([], ["no_reservation"])
            or adapter.get("block_codes") != []
            or type(adapter.get("candidate_count")) is not int
            or adapter["candidate_count"] != 1):
        return None
    slot = slots[0]
    target_date = reply.get("proposed_appointment_date")
    target_time = local_minute(reply.get("proposed_start_time_local"))
    duration = reply.get("proposed_duration_minutes")
    try:
        if type(target_date) is not str or date.fromisoformat(target_date).isoformat() != target_date:
            return None
    except ValueError:
        return None
    if (not target_time or slot.get("appointment_date") != target_date
            or local_minute(slot.get("start_time_local")) != target_time
            or type(duration) is not int or not 5 <= duration <= 180
            or duration != current.get("duration_minutes")
            or type(slot.get("duration_minutes")) is not int
            or slot["duration_minutes"] != duration
            or slot.get("warning_codes") not in ([], ["no_reservation"])):
        return None
    return {"target_date": target_date, "target_start_local": target_time}


@dataclass(frozen=True, repr=False)
class DemoSeed:
    persona: str
    request_id: str
    patient_capability: str | None = None
    staff_bearer: str | None = None
    staff_user_id: str | None = None
    seeded_appointment_id: str | None = None


@dataclass(frozen=True, repr=False)
class DemoConfig:
    profile: str
    environment: str
    listener_origin: str
    backend_app: Any
    practice_id: str
    patient_id: str
    patient_label: str
    practitioner_id: str
    practitioner_label: str
    appointment_type_id: str
    appointment_type_label: str
    location_id: str | None
    location_label: str
    timezone: str
    demo_clock: str
    seeds: tuple[DemoSeed, ...]
    # Trusted server fixture map. Staff never receives a patient capability in
    # its own session; the bridge uses the exact request's separate seed.
    request_capabilities: dict[str, str] = field(repr=False)
    # None until actual local installation, model and execution evidence are
    # independently bound by the trusted isolated harness.
    voice_runtime: VoiceRuntimeBinding | ContainedVoiceRuntimeBinding | SpeechComponentVoiceBinding | None = field(
        default=None, repr=False)
    # One optional, trusted startup-supplied versioned report. No HTTP upload,
    # caller path, evaluator or runtime measurement is created by this bridge.
    reliability_report_bytes: bytes | None = field(default=None, repr=False)
    reliability_report_sha256: str | None = field(default=None, repr=False)
    # Optional exact Native04 delivered projections and independent reviews.
    # The trusted startup supplies bytes; this bridge never opens their paths.
    reliability_native04_result_bytes: bytes | None = field(default=None, repr=False)
    reliability_native04_primary_bytes: bytes | None = field(default=None, repr=False)
    reliability_native04_effect_review_bytes: bytes | None = field(default=None, repr=False)
    reliability_existing_evidence_review_bytes: bytes | None = field(default=None, repr=False)
    # One pinned, pre-projected progress report. No report path or client data is read.
    reliability_progress_report_bytes: bytes | None = field(default=None, repr=False)
    reliability_progress_report_sha256: str | None = field(default=None, repr=False)
    # Trusted fixture only. The admitted mock integration must supply this;
    # None retains the canonical bridge's pre-integration behaviour.
    staff_mock_auth: StaffMockBinding | None = field(default=None, repr=False)
    # Absolute end of the trusted staff recording window; never extended by
    # token continuation. Required when staff_mock_auth is supplied.
    staff_human_window_ends_at: datetime | None = field(default=None, repr=False)
    # Only the separately reviewed owner-paced synthetic fixture opts in.
    owner_paced_window_seconds: int | None = None
    # Alternative trusted startup binding for the one isolated backend.
    # A request cannot choose this origin; ASGI and HTTP are exclusive.
    backend_loopback_origin: str | None = field(default=None, repr=False)
    # Supplied only by the trusted launcher for its reviewed owned-container
    # transport; no browser request can select or replace this callable.
    backend_exec_exchange: Callable[..., Awaitable[httpx.Response]] | None = field(
        default=None, repr=False)


@dataclass(repr=False)
class _Session:
    binding: SessionBinding
    staff_bearer: str | None
    seeded_appointment_id: str | None
    expires_at: datetime
    staff_mock_token: str | None = field(default=None, repr=False)
    staff_mock_expires_at: datetime | None = field(default=None, repr=False)
    proposal: dict[str, Any] | None = None
    uncertain: dict[str, Any] | None = None
    voice_nonce: str = field(default_factory=lambda: secrets.token_urlsafe(24), repr=False)


class DemoIssuer:
    """Trusted harness handle, not an HTTP endpoint or client role selector."""

    def __init__(self, config: DemoConfig):
        if (config.backend_exec_exchange is not None and
                (not callable(config.backend_exec_exchange)
                 or config.backend_loopback_origin is None
                 or config.backend_app is not None)):
            raise ValueError("DEMO_BACKEND_BINDING_INVALID")
        if config.backend_loopback_origin is None:
            if config.backend_app is None:
                raise ValueError("DEMO_BACKEND_BINDING_INVALID")
        else:
            origin = config.backend_loopback_origin
            match = (re.fullmatch(r"http://127\.0\.0\.1:([1-9][0-9]{0,4})", origin)
                     if type(origin) is str else None)
            if (config.backend_app is not None or match is None
                    or int(match.group(1)) > 65535):
                raise ValueError("DEMO_BACKEND_BINDING_INVALID")
        if (config.profile != "STAGE1_SYNTHETIC_DEMO" or config.environment != "dev"
                or not config.listener_origin.startswith("http://127.0.0.1:")
                or not config.seeds or len(config.seeds) > 3):
            raise ValueError("DEMO_PROFILE_CLOSED")
        patient_seeds = [s for s in config.seeds if s.persona == "patient"]
        staff_seeds = [s for s in config.seeds if s.persona == "staff"]
        if (len(patient_seeds) != 2 or len(staff_seeds) != 1
                or patient_seeds[0].request_id == patient_seeds[1].request_id
                or any(not s.patient_capability or s.staff_bearer for s in patient_seeds)
                or any(not s.staff_bearer or not s.staff_user_id or s.patient_capability for s in staff_seeds)
                or set(config.request_capabilities) != {s.request_id for s in patient_seeds}
                or any(config.request_capabilities[s.request_id] != s.patient_capability for s in patient_seeds)):
            raise ValueError("DEMO_SEEDS_INVALID")
        if config.staff_mock_auth is not None:
            fixed = config.staff_mock_auth
            now = datetime.now(timezone.utc)
            window_end = config.staff_human_window_ends_at
            limit = (86400 if config.owner_paced_window_seconds == 86400
                     else 3600 if config.owner_paced_window_seconds is None else 0)
            if (limit == 0 or
                    (limit == 86400 and config.timezone != "Australia/Brisbane") or
                    type(window_end) is not datetime or
                    window_end.tzinfo is None or
                    window_end.utcoffset() != timedelta(0) or
                    not now < window_end <= now + timedelta(seconds=limit)):
                raise ValueError("MOCK_HUMAN_WINDOW_INVALID")
            if (fixed.practice_id != config.practice_id or
                    fixed.staff_user_id != staff_seeds[0].staff_user_id):
                raise ValueError("MOCK_STAFF_BINDING_INVALID")
            try:
                fixed.require(practice_id=config.practice_id,
                              staff_user_id=staff_seeds[0].staff_user_id,
                              scope="demo:use")
                fixed.require(practice_id=config.practice_id,
                              staff_user_id=staff_seeds[0].staff_user_id,
                              scope="proposal:create")
            except StaffMockDenied as exc:
                raise ValueError("MOCK_STAFF_BINDING_INVALID") from exc
        elif (config.staff_human_window_ends_at is not None or
              config.owner_paced_window_seconds is not None):
            raise ValueError("MOCK_HUMAN_WINDOW_INVALID")
        self.config = config
        self.lab_view = project_reliability_lab(
            config.reliability_report_bytes, config.reliability_report_sha256)
        native04 = project_native04_controls(
            config.reliability_native04_result_bytes,
            config.reliability_native04_primary_bytes,
            config.reliability_native04_effect_review_bytes,
            config.reliability_existing_evidence_review_bytes)
        if native04 is not None:
            self.lab_view = {**self.lab_view,
                "schema": "emr4.stage1_reliability_lab_view.v2",
                "native04": native04}
        progress = project_lab_progress(
            config.reliability_progress_report_bytes,
            config.reliability_progress_report_sha256)
        if progress is not None:
            self.lab_view = {**self.lab_view,
                "schema": "emr4.stage1_reliability_lab_view.v3",
                "progress": progress}
        self._sessions: dict[str, _Session] = {}
        self._initial_booking: dict[str, dict[str, str]] = {}
        # Fixed staff journey only. These flags are set after existing typed
        # receipt/readback checks, and are never supplied by an HTTP caller.
        self._live_request_id = staff_seeds[0].request_id
        self._live_outcomes = {
            "request_submitted_verified": False,
            "booking_confirmed_verified": False,
            "move_confirmed_verified": False,
        }
        # Fixed, identifier-free shutdown diagnostic for the live request.
        # A read-only state observation never proves the original command.
        self._submit_diagnostic = {
            "submit_stage": "NONE",
            "submit_category": "NONE",
            "observed_request_state": "UNAVAILABLE",
        }
        for seed in config.seeds:
            token = secrets.token_urlsafe(32)
            binding = SessionBinding(
                persona=seed.persona, session_id=secrets.token_urlsafe(24),
                csrf=secrets.token_urlsafe(24), practice_id=config.practice_id,
                patient_id=config.patient_id, request_id=seed.request_id,
                patient_capability=seed.patient_capability,
                staff_user_id=seed.staff_user_id if seed.persona == "staff" else None,
            )
            mock_token = config.staff_mock_auth.token if seed.persona == "staff" and config.staff_mock_auth else None
            mock_expiry = config.staff_mock_auth.expiry_for(mock_token) if mock_token else None
            session_end = (config.staff_human_window_ends_at
                           if config.owner_paced_window_seconds == 86400
                           else datetime.now(timezone.utc) + timedelta(hours=2))
            self._sessions[token] = _Session(binding, seed.staff_bearer,
                seed.seeded_appointment_id, session_end,
                staff_mock_token=mock_token, staff_mock_expires_at=mock_expiry)

    def cookie_for(self, persona: str, request_id: str) -> tuple[str, str]:
        """Return name/value only to the reviewed local harness; do not log it."""
        for token, session in self._sessions.items():
            b = session.binding
            if b.persona == persona and b.request_id == request_id:
                return COOKIE, token
        raise ValueError("SESSION_NOT_CONFIGURED")

    def live_outcome_summary(self) -> dict[str, bool]:
        """Trusted shutdown projection; no appointment or session identifiers."""
        return {name: value is True for name, value in self._live_outcomes.items()}

    def submit_diagnostic_summary(self) -> dict[str, str]:
        """Trusted fixed-enum projection; no command key, payload or patient data."""
        return dict(self._submit_diagnostic)

    def issue_cookie(self, response: JSONResponse, persona: str, request_id: str) -> None:
        """Trusted fixture calls this out of band; no public issuance route."""
        name, value = self.cookie_for(persona, request_id)
        response.set_cookie(name, value,
                            max_age=86400 if self.config.owner_paced_window_seconds == 86400 else 7200,
                            httponly=True,
                            samesite="strict", secure=False, path="/demo/stage1")

    def cookie_session_for(self, request: Request) -> _Session:
        token = request.cookies.get(COOKIE)
        session = self._sessions.get(token or "")
        if session is None or datetime.now(timezone.utc) >= session.expires_at:
            raise HTTPException(status_code=404, detail="DEMO_SESSION_UNAVAILABLE")
        if (session.binding.persona == "staff" and
                self.config.staff_human_window_ends_at is not None and
                datetime.now(timezone.utc) >= self.config.staff_human_window_ends_at):
            raise HTTPException(status_code=403, detail="DEMO_HUMAN_WINDOW_ENDED")
        return session

    def session_for(self, request: Request) -> _Session:
        session = self.cookie_session_for(request)
        self.require_staff(session)
        return session

    def require_staff(self, session: _Session, scope: str = "demo:use") -> None:
        if session.binding.persona != "staff" or self.config.staff_mock_auth is None:
            return
        if (self.config.staff_human_window_ends_at is None or
                datetime.now(timezone.utc) >= self.config.staff_human_window_ends_at):
            raise HTTPException(status_code=403, detail="DEMO_HUMAN_WINDOW_ENDED")
        if (session.staff_mock_token is None or session.staff_mock_expires_at is None or
                datetime.now(timezone.utc) >= session.staff_mock_expires_at):
            raise HTTPException(status_code=403, detail="MOCK_STAFF_SESSION_EXPIRED")
        try:
            self.config.staff_mock_auth.require(
                practice_id=session.binding.practice_id,
                staff_user_id=session.binding.staff_user_id or "", scope=scope,
                token=session.staff_mock_token)
        except StaffMockDenied:
            raise HTTPException(status_code=403, detail="MOCK_STAFF_UNAVAILABLE") from None


def _owner_paced_practice_clock(now: datetime) -> str:
    if (type(now) is not datetime or now.tzinfo is None or
            now.utcoffset() != timedelta(0)):
        raise ValueError("DEMO_CLOCK_BOUNDARY_INVALID")
    # The selected synthetic practice uses Brisbane's fixed UTC+10 offset.
    return now.astimezone(timezone(timedelta(hours=10))).strftime("%Y-%m-%d %H:%M")


def create_stage1_demo_app(config: DemoConfig) -> tuple[FastAPI, DemoIssuer]:
    def practice_clock() -> str:
        if config.owner_paced_window_seconds == 86400:
            return _owner_paced_practice_clock(datetime.now(timezone.utc))
        return config.demo_clock
    """Create an isolated loopback ASGI app; caller owns listener binding."""
    issuer = DemoIssuer(config)
    def mark_submit(session: _Session, stage: str, category: str) -> None:
        if (session.binding.persona == "patient" and
                session.binding.request_id == issuer._live_request_id):
            issuer._submit_diagnostic["submit_stage"] = stage
            issuer._submit_diagnostic["submit_category"] = category
    app = FastAPI(title="Stage 1 synthetic local demo", docs_url=None, redoc_url=None,
                  openapi_url=None)
    voice_lock = asyncio.Lock()

    class _StaffMockChangedAfterDispatch(HTTPException):
        """An awaited backend request may already have applied its effect."""

        def __init__(self) -> None:
            super().__init__(status_code=503, detail="MOCK_STAFF_OUTCOME_UNAVAILABLE")

    def local(request: Request) -> None:
        server = request.scope.get("server")
        client = request.client
        if (not server or server[0] != "127.0.0.1" or client is None
                or client.host != "127.0.0.1" or request.headers.get("host") !=
                config.listener_origin.removeprefix("http://")):
            raise HTTPException(status_code=404, detail="DEMO_UNAVAILABLE")

    def no_store(data: Any, code: int = 200) -> JSONResponse:
        return JSONResponse(data, status_code=code,
            headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})

    async def _backend_exchange(method: str, path: str, *, headers: dict[str, str],
                                body=None, params=None) -> httpx.Response:
        # Every caller supplies an internal fixed-route suffix; the URL is
        # always relative to the one trusted startup-bound backend origin.
        if config.backend_exec_exchange is not None:
            return await config.backend_exec_exchange(
                method, BASE + path, headers=headers, body=body, params=params)
        transport = (httpx.ASGITransport(app=config.backend_app,
            client=("127.0.0.1", 12345), raise_app_exceptions=False)
            if config.backend_loopback_origin is None else None)
        origin = config.backend_loopback_origin or "http://127.0.0.1"
        async with httpx.AsyncClient(transport=transport, base_url=origin,
                follow_redirects=False, trust_env=False, timeout=10) as client:
            return await client.request(method, BASE + path, headers=headers,
                                        json=body, params=params)

    async def backend(method: str, path: str, session: _Session, *, body=None,
                      key: str | None = None, patient: bool = False) -> Any:
        headers = {"Cache-Control": "no-store"}
        if patient:
            capability = config.request_capabilities.get(session.binding.request_id)
            if not capability:
                raise HTTPException(status_code=404, detail="REQUEST_UNAVAILABLE")
            headers["X-Patient-Request-Capability"] = capability
        else:
            scope = "proposal:create" if method == "POST" else "demo:use"
            issuer.require_staff(session, scope)
            if not session.staff_bearer:
                raise HTTPException(status_code=403, detail="STAFF_UNAVAILABLE")
            headers["Authorization"] = "Bearer " + session.staff_bearer
        if key:
            headers["Idempotency-Key"] = key
        response = await _backend_exchange(method, path, headers=headers, body=body)
        if not patient:
            try:
                issuer.require_staff(session, scope)
            except HTTPException:
                raise _StaffMockChangedAfterDispatch() from None
        if response.status_code >= 400:
            # A current-authority refusal is definitive, never a lost reply.
            # Keep its body opaque and consistent with other stale/denied
            # backend outcomes at this demo boundary.
            status = {400: 400, 401: 403, 403: 403, 404: 404,
                      409: 409, 422: 422}.get(response.status_code, 503)
            detail = {400: "BACKEND_VALIDATION_INVALID", 422: "BACKEND_VALIDATION_INVALID",
                      403: "BACKEND_ACCESS_DENIED", 404: "BACKEND_RESOURCE_UNAVAILABLE",
                      409: "BACKEND_STATE_CHANGED", 503: "BACKEND_OUTCOME_UNCERTAIN"}[status]
            raise HTTPException(status_code=status, detail=detail)
        try:
            return response.json()
        except ValueError:
            raise HTTPException(status_code=503, detail="BACKEND_READBACK_UNAVAILABLE") from None

    async def patient_read(session: _Session) -> dict[str, Any]:
        return await backend("GET", f"/patient-requests/{session.binding.request_id}", session, patient=True)

    async def staff_request(session: _Session) -> dict[str, Any]:
        return await backend("GET", f"/staff/patient-requests/{session.binding.request_id}", session)

    async def appointment(session: _Session, appointment_id: str) -> dict[str, Any]:
        row = await backend("GET", f"/{appointment_id}", session)
        if row.get("id") != appointment_id or row.get("practice_id") != config.practice_id or row.get("patient_id") != config.patient_id:
            raise HTTPException(status_code=409, detail="APPOINTMENT_SCOPE_CHANGED")
        return row

    def present_appointment(row: dict[str, Any]) -> dict[str, Any]:
        if type(row.get("appointment_state_version")) is not int or row["appointment_state_version"] < 1:
            raise HTTPException(status_code=409, detail="APPOINTMENT_VERSION_UNAVAILABLE")
        practitioner = row.get("practitioner")
        kind = row.get("appointment_type")
        patient = row.get("patient")
        if (row.get("practitioner_id") != config.practitioner_id or
                row.get("appointment_type_id") != config.appointment_type_id or
                row.get("location_id") != config.location_id or
                not isinstance(practitioner, dict) or practitioner.get("id") != config.practitioner_id or
                not isinstance(kind, dict) or kind.get("id") != config.appointment_type_id or
                not isinstance(patient, dict) or patient.get("id") != config.patient_id):
            raise HTTPException(status_code=409, detail="APPOINTMENT_DIMENSIONS_CHANGED")
        patient_name = " ".join(part for part in (patient.get("first_name"), patient.get("last_name")) if part)
        practitioner_name = " ".join(part for part in (practitioner.get("first_name"), practitioner.get("last_name")) if part)
        type_name = kind.get("name")
        clock = local_minute(row.get("start_time_local"))
        if (not clock or patient_name != config.patient_label or
                practitioner_name != config.practitioner_label or
                type_name != config.appointment_type_label or not isinstance(type_name, str)
                or not type_name.strip() or not config.location_label.strip()):
            raise HTTPException(status_code=409, detail="APPOINTMENT_LABELS_UNAVAILABLE")
        return {"ref": row["id"], "date": row["appointment_date"],
                "start_local": clock, "zone": config.timezone,
                "status": row["status"], "state_version": row["appointment_state_version"],
                "patient_label": patient_name, "practitioner_label": practitioner_name,
                "type_label": type_name, "duration_minutes": row["duration_minutes"],
                "location_label": config.location_label if config.location_id else "No location assigned"}

    async def refreshed(session: _Session) -> dict[str, Any]:
        if session.binding.persona == "patient":
            if session.binding.request_id == issuer._live_request_id:
                issuer._submit_diagnostic["observed_request_state"] = "UNAVAILABLE"
            request = await patient_read(session)
            if session.binding.request_id == issuer._live_request_id:
                state = request.get("state") if type(request) is dict else None
                issuer._submit_diagnostic["observed_request_state"] = (
                    state.upper() if type(state) is str and
                    state in {"draft", "submitted", "booked"}
                    else "OTHER")
            options = (await backend("GET", f"/patient-requests/{session.binding.request_id}/options"
                       f"?request_version={request['request_version']}", session, patient=True)
                       if request.get("state") == "draft" else [])
            captured = issuer._initial_booking.get(session.binding.request_id)
            original = captured if (request.get("state") == "booked" and captured and
                captured["appointment_id"] == request.get("booked_appointment_id")) else None
            return {"request": request, "options": options, "original_booking": original}
        request = await staff_request(session)
        options: list[dict[str, Any]] = []
        if request.get("state") == "submitted":
            issuer.require_staff(session)
            capability = config.request_capabilities.get(session.binding.request_id)
            if not capability:
                raise HTTPException(status_code=404, detail="REQUEST_UNAVAILABLE")
            # Dedicated request capability belongs to trusted fixture, not the
            # staff browser session. Backend is the only option source.
            response = await _backend_exchange("GET",
                f"/patient-requests/{session.binding.request_id}/options",
                params={"request_version": request["request_version"]},
                headers={"X-Patient-Request-Capability": capability})
            issuer.require_staff(session)
            if response.status_code == 200:
                options = response.json()
        appointment_id = request.get("booked_appointment_id") or session.seeded_appointment_id
        current = present_appointment(await appointment(session, appointment_id)) if appointment_id else None
        captured = issuer._initial_booking.get(session.binding.request_id)
        original = captured if (request.get("state") == "booked" and captured and
            captured["appointment_id"] == request.get("booked_appointment_id")) else None
        return {"request": request, "options": options, "appointment": current,
                "original_booking": original}

    async def record_initial_create(session: _Session, result: dict[str, Any]) -> dict[str, Any]:
        result_id = result.get("appointment", {}).get("id")
        if not result_id:
            raise HTTPException(status_code=409, detail="CREATE_RESULT_UNAVAILABLE")
        current = present_appointment(await appointment(session, result_id))
        linked_request = await staff_request(session)
        receipt = result.get("confirmation_receipt")
        verification = receipt.get("verification") if isinstance(receipt, dict) else None
        try:
            correlation_valid = (isinstance(receipt["correlation_id"], str)
                and str(uuid.UUID(receipt["correlation_id"])) == receipt["correlation_id"])
            audit_valid = (isinstance(receipt["audit_event_id"], str)
                and str(uuid.UUID(receipt["audit_event_id"])) == receipt["audit_event_id"])
        except (KeyError, TypeError, ValueError, AttributeError):
            correlation_valid = audit_valid = False
        verified = isinstance(verification, dict) and all(
            verification.get(name) is True for name in (
                "actor_authenticated", "practice_scope_verified", "proposal_revalidated",
                "conflict_check_passed", "idempotency_verified", "audit_recorded",
                "signed_evidence_verified",
            )
        ) and verification.get("visual_diary_check_required") is False
        if (linked_request.get("state") != "booked" or
                linked_request.get("booked_appointment_id") != result_id or
                current["date"] != result["appointment"].get("appointment_date") or
                current["start_local"] != local_minute(result["appointment"].get("start_time_local")) or
                not isinstance(receipt, dict) or
                receipt.get("schema_version") != "appointment.confirmation_receipt.v1" or
                receipt.get("outcome") != "appointment_created" or
                receipt.get("appointment_id") != result_id or
                receipt.get("appointment_date") != current["date"] or
                local_minute(receipt.get("start_time_local")) != current["start_local"] or
                receipt.get("duration_minutes") != current["duration_minutes"] or
                receipt.get("status") != current["status"] or
                receipt.get("patient_display") != current["patient_label"] or
                receipt.get("practitioner_display") != current["practitioner_label"] or
                receipt.get("appointment_type") != current["type_label"] or
                not isinstance(receipt.get("confirmed_by_display"), str) or
                not receipt["confirmed_by_display"].strip() or
                (receipt.get("confirmed_by_role") is not None and
                 not isinstance(receipt.get("confirmed_by_role"), str)) or
                (receipt.get("session_id") is not None and
                 not isinstance(receipt.get("session_id"), str)) or
                not correlation_valid or not audit_valid or not verified):
            raise HTTPException(status_code=409, detail="REQUEST_COMMAND_LINK_MISMATCH")
        issuer._initial_booking[session.binding.request_id] = {
            "appointment_id": result_id, "date": current["date"],
            "start_local": current["start_local"], "zone": current["zone"],
            "source": "completed_create_command_result",
        }
        if session.binding.request_id == issuer._live_request_id:
            issuer._live_outcomes["booking_confirmed_verified"] = True
        return current

    async def verified_submission(session: _Session, result: Any,
                                  payload: dict[str, Any]) -> dict[str, Any]:
        # The backend receipt is the outcome of the exact original submit.
        # Its readback may already have advanced to booked, but the request
        # identity, submitted version and preferences must still agree.
        expected_version = payload["request_version"] + 1
        if (not isinstance(result, dict) or
                result.get("request_id") != session.binding.request_id or
                result.get("state") != "submitted" or
                type(result.get("request_version")) is not int or
                result["request_version"] != expected_version):
            mark_submit(session, "BACKEND_RESPONSE", "RECEIPT_MISMATCH")
            raise HTTPException(status_code=409, detail="REQUEST_RECEIPT_MISMATCH")
        mark_submit(session, "RECEIPT_VALIDATED", "READBACK_PENDING")
        try:
            snapshot = await refreshed(session)
        except Exception:
            mark_submit(session, "RECEIPT_VALIDATED", "READBACK_UNAVAILABLE")
            raise
        current = snapshot["request"]
        if (current.get("request_id") != session.binding.request_id or
                current.get("state") not in {"submitted", "booked"} or
                type(current.get("request_version")) is not int or
                current["request_version"] < expected_version or
                current.get("preference_date") != payload["date"] or
                local_minute(current.get("earliest_local")) != payload["earliest_local"] or
                local_minute(current.get("latest_local")) != payload["latest_local"]):
            mark_submit(session, "RECEIPT_VALIDATED", "READBACK_MISMATCH")
            raise HTTPException(status_code=409, detail="REQUEST_READBACK_MISMATCH")
        mark_submit(session, "READBACK_VERIFIED", "VERIFIED")
        return snapshot

    async def uncertain_snapshot(session: _Session) -> JSONResponse:
        def require_pending_staff() -> None:
            if session.binding.persona == "staff":
                try:
                    issuer.require_staff(session, "proposal:create")
                except HTTPException:
                    raise HTTPException(status_code=503,
                        detail="COMMAND_OUTCOME_UNCERTAIN") from None
        require_pending_staff()
        try:
            snapshot = await refreshed(session)
        except HTTPException:
            require_pending_staff()
            return no_store({"uncertain": True})
        require_pending_staff()
        return no_store({**snapshot, "uncertain": True})

    @app.post("/demo/stage1/continue")
    async def continue_staff_route(request: Request):
        """Human-selected continuation of this fixed synthetic staff fixture."""
        local(request)
        session = issuer.cookie_session_for(request)
        fixed = config.staff_mock_auth
        if (session.binding.persona != "staff" or fixed is None or
                session.binding.practice_id != fixed.practice_id or
                session.binding.staff_user_id != fixed.staff_user_id):
            raise HTTPException(status_code=404, detail="DEMO_SESSION_UNAVAILABLE")
        if (request.headers.get("origin") != config.listener_origin or
                request.headers.get("content-type") != "application/json" or
                not secrets.compare_digest(request.headers.get("x-csrf-token", ""),
                                           session.binding.csrf)):
            raise HTTPException(status_code=403, detail="DEMO_CONTINUATION_UNAVAILABLE")
        parts: list[bytes] = []
        size = 0
        async for chunk in request.stream():
            size += len(chunk)
            if size > 2:
                raise HTTPException(status_code=400, detail="DEMO_CONTINUATION_INVALID")
            parts.append(chunk)
        if b"".join(parts) != b"{}":
            raise HTTPException(status_code=400, detail="DEMO_CONTINUATION_INVALID")
        issuer.cookie_session_for(request)
        try:
            new_token, new_expiry = fixed.issue_current()
        except StaffMockDenied:
            raise HTTPException(status_code=403, detail="MOCK_STAFF_UNAVAILABLE") from None
        issuer.cookie_session_for(request)
        session.staff_mock_token = new_token
        session.staff_mock_expires_at = new_expiry
        return no_store({"continued": True,
            "mock_token_expires_at": new_expiry.isoformat(),
            "human_window_ends_at": config.staff_human_window_ends_at.isoformat()})

    @app.get("/demo/stage1/session")
    async def session_route(request: Request):
        local(request)
        session = issuer.session_for(request)
        voice_ready = (config.voice_runtime is not None and
            (config.voice_runtime.ready(session.binding.persona)
             if isinstance(config.voice_runtime, (ContainedVoiceRuntimeBinding, SpeechComponentVoiceBinding))
             else config.voice_runtime.ready()))
        mock_identity = (config.staff_mock_auth.projected_identity()
            if session.binding.persona == "staff" and config.staff_mock_auth is not None else None)
        return no_store({"persona": session.binding.persona, "csrf": session.binding.csrf,
            "zone": config.timezone, "demo_clock": practice_clock(),
            "voice_available": voice_ready, "voice_nonce": session.voice_nonce if voice_ready else None,
            "mock_identity": mock_identity,
            "mock_token_expires_at": session.staff_mock_expires_at.isoformat()
                if session.binding.persona == "staff" and session.staff_mock_expires_at else None,
            "human_window_ends_at": config.staff_human_window_ends_at.isoformat()
                if session.binding.persona == "staff" and config.staff_human_window_ends_at else None})

    @app.get("/demo/stage1/reliability")
    async def reliability_route(request: Request):
        local(request)
        session = issuer.session_for(request)
        if session.binding.persona != "staff" or not session.staff_bearer:
            raise HTTPException(status_code=404, detail="LAB_UNAVAILABLE")
        return no_store(issuer.lab_view)

    @app.get("/demo/stage1/")
    async def page(request: Request):
        local(request); issuer.session_for(request)
        return FileResponse(UI_VIEW / "stage1-interactive.html",
                            headers={"Cache-Control": "no-store"})

    @app.get("/demo/stage1/{asset}")
    async def asset(request: Request, asset: str):
        local(request); issuer.session_for(request)
        paths = {
            "stage1-interactive.css": UI_VIEW / "stage1-interactive.css",
            "stage1-interactive.js": UI_CONTROLLER / "stage1-interactive.js",
            "stage1-diary-view.js": UI_VIEW / "stage1-diary-view.js",
            "stage1-local-voice.js": STATIC / "stage1-local-voice.js",
        }
        if asset not in paths:
            raise HTTPException(status_code=404)
        return FileResponse(paths[asset], headers={"Cache-Control": "no-store"})

    @app.post("/demo/stage1/interpret")
    async def interpret_route(request: Request):
        local(request)
        session = issuer.session_for(request)
        if (request.headers.get("origin") != config.listener_origin or
                request.headers.get("content-type") != "application/json" or
                not secrets.compare_digest(request.headers.get("x-csrf-token", ""),
                                           session.binding.csrf)):
            raise HTTPException(status_code=403, detail="INTENT_SCOPE_UNAVAILABLE")
        parts: list[bytes] = []
        size = 0
        async for chunk in request.stream():
            size += len(chunk)
            if size > MAX_BODY_BYTES:
                raise HTTPException(status_code=413, detail="BODY_TOO_LARGE")
            parts.append(chunk)
        issuer.session_for(request)
        def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
            result: dict[str, Any] = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("DUPLICATE_FIELD")
                result[key] = value
            return result
        try:
            body = json.loads(b"".join(parts).decode("utf-8"), object_pairs_hook=unique)
        except (UnicodeError, ValueError):
            raise HTTPException(status_code=400, detail="INTENT_BODY_INVALID") from None
        if type(body) is not dict:
            raise HTTPException(status_code=400, detail="INTENT_BODY_INVALID")
        if body.get("kind") == "move":
            if (session.binding.persona != "staff" or set(body) != {
                    "kind", "words", "appointment_ref", "source_state_version"}
                    or type(body["words"]) is not str or not body["words"].strip()
                    or len(body["words"]) > 512
                    or type(body["appointment_ref"]) is not str
                    or type(body["source_state_version"]) is not int
                    or body["source_state_version"] < 1):
                raise HTTPException(status_code=400, detail="INTENT_BODY_INVALID")
            issuer.require_staff(session, "proposal:create")
            fresh = await refreshed(session)
            current = fresh.get("appointment")
            if (type(current) is not dict or current.get("ref") != body["appointment_ref"]
                    or current.get("state_version") != body["source_state_version"]):
                raise HTTPException(status_code=409, detail="APPOINTMENT_STATE_CHANGED")
            correlation_id = str(uuid.uuid4())
            try:
                reply = await backend("POST", "/proposals/reception-one/compose", session,
                    body={"contract_version": "reception.one.product-context-request.v1",
                          "instruction": body["words"], "reference_date": practice_clock()[:10],
                          "surface_id": "diary-main", "correlation_id": correlation_id,
                          "data_class": "authored_synthetic",
                          "selected_appointment_id": current["ref"],
                          "planner_mode": "deterministic"})
            except _StaffMockChangedAfterDispatch:
                raise HTTPException(status_code=403, detail="MOCK_STAFF_SESSION_EXPIRED") from None
            issuer.session_for(request)
            issuer.require_staff(session, "proposal:create")
            fields = project_bureau_move(reply, current, correlation_id)
            return no_store({"schema": "emr4.stage1_word_interpretation.v1", "kind": "move",
                "method": "BUREAU_DETERMINISTIC", "status": "PROPOSED" if fields else "CLARIFICATION",
                "fields": fields or {}, "missing": [] if fields else ["target_date", "target_start_local"],
                "selection": {"appointment_ref": current["ref"],
                              "source_state_version": current["state_version"]},
                "message": "BUREAU_REVIEWED_MOVE" if fields else "CLARIFY_SELECTED_MOVE"})
        if set(body) != {"kind", "words"} or body.get("kind") != "request":
            raise HTTPException(status_code=400, detail="INTENT_BODY_INVALID")
        try:
            proposal = interpret_words(body["kind"], body["words"],
                persona=session.binding.persona, demo_clock=practice_clock(),
                timezone=config.timezone)
        except IntentRejected:
            raise HTTPException(status_code=400, detail="INTENT_BODY_INVALID") from None
        if body["kind"] == "request" and proposal["status"] == "PROPOSED":
            current = await patient_read(session)
            offered = []
            if current.get("state") == "draft":
                offered = await backend("GET",
                    f"/patient-requests/{session.binding.request_id}/options"
                    f"?request_version={current['request_version']}",
                    session, patient=True)
            if (type(offered) is not list or
                    proposal["fields"]["date"] not in
                    {option.get("date") for option in offered if type(option) is dict}):
                proposal = {**proposal, "status": "CLARIFICATION", "fields": {},
                    "missing": ["date", "earliest_local", "latest_local"],
                    "message": "DATE_NOT_CURRENTLY_OFFERED"}
        return no_store(proposal)

    @app.post("/demo/stage1/voice")
    async def voice_route(request: Request):
        local(request)
        session = issuer.session_for(request)
        binding = config.voice_runtime
        if binding is None or not (binding.ready(session.binding.persona)
                if isinstance(binding, (ContainedVoiceRuntimeBinding, SpeechComponentVoiceBinding))
                else binding.ready()):
            return no_store({"error": "VOICE_UNAVAILABLE"}, 503)
        target = target_for_persona(session.binding.persona)
        if (request.headers.get("origin") != config.listener_origin
                or request.headers.get("content-type") != "audio/wav"
                or request.headers.get("x-voice-target") != target
                or not secrets.compare_digest(request.headers.get("x-csrf-token", ""),
                                               session.binding.csrf)
                or not secrets.compare_digest(request.headers.get("x-voice-nonce", ""),
                                               session.voice_nonce)):
            return no_store({"error": "VOICE_SCOPE_UNAVAILABLE"}, 403)
        presented_nonce = request.headers.get("x-voice-nonce", "")
        parts: list[bytes] = []
        size = 0
        async for chunk in request.stream():
            size += len(chunk)
            if size > MAX_WAV_BYTES:
                return no_store({"error": "VOICE_TOO_LARGE"}, 413)
            parts.append(chunk)
        issuer.session_for(request)
        raw = b"".join(parts)
        try:
            validate_wav(raw)
        except VoiceInputRejected:
            return no_store({"error": "VOICE_FORMAT_UNAVAILABLE"}, 400)
        if voice_lock.locked():
            return no_store({"error": "VOICE_BUSY"}, 429)
        try:
            async with voice_lock:
                # Recheck inside the lock: two clips can pass the initial check
                # before either obtains it. Only an accepted clip consumes nonce.
                if (not secrets.compare_digest(presented_nonce, session.voice_nonce)
                        or issuer.session_for(request) is not session):
                    return no_store({"error": "VOICE_SESSION_CHANGED"}, 409)
                session.voice_nonce = secrets.token_urlsafe(24)
                next_nonce = session.voice_nonce
                if isinstance(binding, (ContainedVoiceRuntimeBinding, SpeechComponentVoiceBinding)):
                    transcript = await asyncio.to_thread(
                        run_local_recognizer, raw, binding, session.binding.persona)
                else:
                    transcript = await asyncio.to_thread(run_local_recognizer, raw, binding)
        except (VoiceInputRejected, VoiceRecognitionUnavailable):
            return no_store({"error": "VOICE_RECOGNITION_UNAVAILABLE"}, 503)
        if (datetime.now(timezone.utc) >= session.expires_at
                or issuer.session_for(request) is not session
                or session.voice_nonce != next_nonce):
            return no_store({"error": "VOICE_SESSION_CHANGED"}, 409)
        return no_store({"text": transcript, "target": target})

    @app.post("/demo/stage1/action")
    async def action_route(request: Request):
        local(request)
        session = issuer.session_for(request)
        parts: list[bytes] = []
        size = 0
        async for chunk in request.stream():
            size += len(chunk)
            if size > MAX_BODY_BYTES:
                raise HTTPException(status_code=413, detail="BODY_TOO_LARGE")
            parts.append(chunk)
        issuer.session_for(request)
        raw = b"".join(parts)
        try:
            admitted = admit_action(profile=config.profile, enabled=True,
                listener_host=request.scope["server"][0], request_host=request.client.host,
                origin=request.headers.get("origin"), expected_origin=config.listener_origin,
                content_type=request.headers.get("content-type", ""),
                csrf_header=request.headers.get("x-csrf-token"), body_bytes=raw,
                binding=session.binding)
        except AdapterRejected:
            raise HTTPException(status_code=403, detail="DEMO_ACTION_UNAVAILABLE") from None
        action, body, key = admitted.action, admitted.body, admitted.idempotency_key
        if session.binding.persona == "staff" and action in {
                "propose_create", "propose_move", "confirm_create", "confirm_move",
                "reconcile"}:
            issuer.require_staff(session, "proposal:create")
        if action == "refresh":
            return no_store({**(await refreshed(session)), "uncertain": session.uncertain is not None})
        if action == "diary":
            # Fixed synthetic Receptionist only. Startup verifies this user's
            # bearer role and seeds the same active user in the owned database.
            fixed = config.staff_mock_auth
            if (session.binding.persona != "staff" or fixed is None
                    or not session.staff_bearer or not session.binding.staff_user_id
                    or session.binding.practice_id != config.practice_id
                    or fixed.staff_user_id != session.binding.staff_user_id
                    or fixed.practice_id != config.practice_id):
                return no_store(diary_unavailable())
            issuer.require_staff(session, "demo:use")
            first = date.fromisoformat(practice_clock()[:10])
            last = first + timedelta(days=7)
            try:
                path = list_path(first.isoformat(), last.isoformat(), config.timezone)
                response = await _backend_exchange("GET", path.removeprefix(BASE),
                    headers={"Authorization": "Bearer " + session.staff_bearer,
                             "Cache-Control": "no-store"})
                captured_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                issuer.require_staff(session, "demo:use")
                result = render_staff_diary_read(
                    response.content, status_code=response.status_code,
                    content_type=response.headers.get("content-type", ""),
                    tenant_id=config.practice_id,
                    actor_id=session.binding.staff_user_id,
                    authenticated_role="Receptionist",
                    date_from=first.isoformat(), date_to=last.isoformat(),
                    practice_timezone=config.timezone, captured_at=captured_at,
                    as_of=captured_at)
            except (httpx.TimeoutException, httpx.TransportError, ValueError):
                result = diary_unavailable()
            return no_store(result)
        if action == "reconcile":
            pending = session.uncertain
            if pending is None:
                return no_store({**(await refreshed(session)), "uncertain": False})
            # Explicit human check reuses the exact payload and key. Backend
            # request/command idempotency owns the replay decision; no new key
            # or alternate proposal is minted here.
            family = pending["family"]
            path = (f"/patient-requests/{session.binding.request_id}/submit" if family == "submit_request"
                    else "/proposals/create/confirm" if family == "create"
                    else "/proposals/update/confirm")
            if family == "submit_request":
                mark_submit(session, "DISPATCH_ATTEMPTED", "IN_PROGRESS")
            try:
                result = await backend("POST", path, session, body=pending["payload"],
                    key=pending["key"], patient=family == "submit_request")
            except (httpx.TimeoutException, httpx.TransportError):
                if family == "submit_request":
                    mark_submit(session, "DISPATCH_ATTEMPTED", "TRANSPORT_UNCERTAIN")
                return await uncertain_snapshot(session)
            except _StaffMockChangedAfterDispatch:
                raise HTTPException(status_code=503, detail="COMMAND_OUTCOME_UNCERTAIN") from None
            except HTTPException as exc:
                if family == "submit_request":
                    mark_submit(session, "BACKEND_RESPONSE",
                        "BACKEND_NONDEFINITIVE" if exc.status_code == 503
                        else "BACKEND_REJECTED")
                raise
            if family == "submit_request":
                mark_submit(session, "BACKEND_RESPONSE", "RECEIPT_PENDING")
            if family != "submit_request" and (result.get("safe") is not True
                    or not isinstance(result.get("appointment"), dict)):
                return await uncertain_snapshot(session)
            if family == "move" and result["appointment"].get("id") != pending["appointment_id"]:
                return await uncertain_snapshot(session)
            if family == "move":
                try:
                    current = present_appointment(await appointment(session, pending["appointment_id"]))
                except HTTPException:
                    return await uncertain_snapshot(session)
                if (current["ref"] != result["appointment"].get("id") or
                        current["date"] != result["appointment"].get("appointment_date") or
                        current["start_local"] != local_minute(result["appointment"].get("start_time_local"))):
                    return await uncertain_snapshot(session)
            if family == "create":
                try:
                    await record_initial_create(session, result)
                except HTTPException:
                    return await uncertain_snapshot(session)
            try:
                snapshot = (await verified_submission(session, result, pending["payload"])
                    if family == "submit_request" else await refreshed(session))
            except HTTPException:
                return await uncertain_snapshot(session)
            if session.binding.request_id == issuer._live_request_id:
                if family == "submit_request":
                    issuer._live_outcomes["request_submitted_verified"] = True
                elif (family == "move" and
                      issuer._initial_booking.get(session.binding.request_id, {}).get(
                          "appointment_id") == pending["appointment_id"]):
                    issuer._live_outcomes["move_confirmed_verified"] = True
            session.uncertain = None
            session.proposal = None
            return no_store({**snapshot, "uncertain": False})
        if session.uncertain is not None:
            raise HTTPException(status_code=409, detail="COMMAND_OUTCOME_UNCERTAIN")
        if action == "submit_request":
            if set(body) != {"date", "earliest_local", "latest_local", "request_version", "reason_code"}:
                raise HTTPException(status_code=400, detail="REQUEST_BODY_INVALID")
            payload = {**body, "schema_version": "patient.request_submission.v1",
                "request_id": session.binding.request_id, "authority": "request_only"}
            pending = {"family": "submit_request", "key": key, "payload": payload}
            mark_submit(session, "DISPATCH_ATTEMPTED", "IN_PROGRESS")
            try:
                result = await backend("POST", f"/patient-requests/{session.binding.request_id}/submit",
                    session, body=payload, key=key, patient=True)
            except (httpx.TimeoutException, httpx.TransportError):
                mark_submit(session, "DISPATCH_ATTEMPTED", "TRANSPORT_UNCERTAIN")
                session.uncertain = pending
                raise HTTPException(status_code=503, detail="COMMAND_OUTCOME_UNCERTAIN") from None
            except HTTPException as exc:
                if exc.status_code == 503:
                    mark_submit(session, "BACKEND_RESPONSE", "BACKEND_NONDEFINITIVE")
                    session.uncertain = pending
                else:
                    mark_submit(session, "BACKEND_RESPONSE", "BACKEND_REJECTED")
                raise
            mark_submit(session, "BACKEND_RESPONSE", "RECEIPT_PENDING")
            session.uncertain = pending
            snapshot = await verified_submission(session, result, payload)
            if session.binding.request_id == issuer._live_request_id:
                issuer._live_outcomes["request_submitted_verified"] = True
            response = no_store(snapshot)
            session.uncertain = None
            return response
        if action == "propose_create":
            if set(body) != {"request_version", "selected"}:
                raise HTTPException(status_code=400, detail="CREATE_BODY_INVALID")
            proposal = await backend("POST",
                f"/staff/patient-requests/{session.binding.request_id}/proposals/create",
                session, body=body)
            if proposal.get("safe") is not True or not isinstance(proposal.get("confirm_payload"), dict):
                return no_store({"safe": False})
            ref = secrets.token_urlsafe(24)
            session.proposal = {"family": "create", "ref": ref, "payload": proposal["confirm_payload"],
                "request_version": body["request_version"], "expires": datetime.now(timezone.utc) + timedelta(minutes=4)}
            return no_store({"safe": True, "proposal_ref": ref,
                "patient_label": config.patient_label, "practitioner_label": config.practitioner_label})
        if action == "propose_move":
            if set(body) != {"appointment_ref", "source_state_version", "target_date", "target_start_local"}:
                raise HTTPException(status_code=400, detail="MOVE_BODY_INVALID")
            current = await refreshed(session)
            appt = current.get("appointment")
            if not appt or body["appointment_ref"] != appt["ref"] or body["source_state_version"] != appt["state_version"]:
                raise HTTPException(status_code=409, detail="MOVE_SOURCE_CHANGED")
            payload = {"schema_version": "appointment.move_time_intent.v1",
                "tenant_id": config.practice_id, "actor_id": session.binding.staff_user_id,
                "role": "reception", "source_appointment_id": appt["ref"],
                "source_state_version": appt["state_version"], "source_revision": appt["state_version"],
                "target_date": body["target_date"], "target_start_local": body["target_start_local"],
                "authority": "proposal_only"}
            proposal_key = "stage1-move-proposal-" + secrets.token_urlsafe(24)
            proposal = await backend("POST", f"/proposals/move-time/{appt['ref']}", session, body=payload, key=proposal_key)
            if proposal.get("safe") is not True or not isinstance(proposal.get("confirm_payload"), dict):
                return no_store({"safe": False})
            ref = secrets.token_urlsafe(24)
            session.proposal = {"family": "move", "ref": ref, "payload": proposal["confirm_payload"],
                "appointment_id": appt["ref"], "source_state_version": appt["state_version"],
                "expires": datetime.now(timezone.utc) + timedelta(minutes=4)}
            return no_store({"safe": True, "proposal_ref": ref})
        if action in {"confirm_create", "confirm_move"}:
            proposal = session.proposal
            family = "create" if action == "confirm_create" else "move"
            if (set(body) != {"proposal_ref"} or proposal is None or proposal["family"] != family
                    or body["proposal_ref"] != proposal["ref"]
                    or datetime.now(timezone.utc) >= proposal["expires"]):
                raise HTTPException(status_code=409, detail="PROPOSAL_STALE")
            # The signed payload is backend-authored. Only the deliberate human
            # confirmation flag changes; all domain checks occur in backend.
            payload = {**proposal["payload"], "confirmed": True}
            route = "/proposals/create/confirm" if family == "create" else "/proposals/update/confirm"
            pending = {"family": family, "key": key, "payload": payload,
                "appointment_id": proposal.get("appointment_id")}
            try:
                result = await backend("POST", route, session, body=payload, key=key)
            except (httpx.TimeoutException, httpx.TransportError):
                session.uncertain = pending
                raise HTTPException(status_code=503, detail="COMMAND_OUTCOME_UNCERTAIN") from None
            except _StaffMockChangedAfterDispatch:
                session.uncertain = pending
                raise HTTPException(status_code=503, detail="COMMAND_OUTCOME_UNCERTAIN") from None
            except HTTPException as exc:
                if exc.status_code == 503:
                    session.uncertain = pending
                raise
            # A positive HTTP response is not proof of the effect. Retain the
            # original key and backend-authored payload until typed receipt and
            # fresh scoped readback both establish the committed outcome.
            session.uncertain = pending
            if result.get("safe") is not True or not isinstance(result.get("appointment"), dict):
                raise HTTPException(status_code=409, detail="CONFIRMATION_BLOCKED")
            result_id = result["appointment"].get("id")
            if family == "move" and result_id != proposal["appointment_id"]:
                raise HTTPException(status_code=409, detail="MOVE_IDENTITY_CHANGED")
            current = present_appointment(await appointment(session, result_id))
            if (current["date"] != result["appointment"].get("appointment_date")
                    or current["start_local"] != local_minute(result["appointment"].get("start_time_local"))):
                raise HTTPException(status_code=409, detail="COMMITTED_READBACK_MISMATCH")
            if family == "create":
                await record_initial_create(session, result)
            elif (session.binding.request_id == issuer._live_request_id and
                  issuer._initial_booking.get(session.binding.request_id, {}).get(
                      "appointment_id") == result_id):
                issuer._live_outcomes["move_confirmed_verified"] = True
            response = no_store({"outcome": "committed", "appointment": current})
            session.uncertain = None
            session.proposal = None
            return response
        raise HTTPException(status_code=404, detail="ACTION_UNAVAILABLE")

    return app, issuer
