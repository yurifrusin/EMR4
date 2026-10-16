"""Source-only standalone Stage 1 demo bridge; never include in production main.

The trusted isolated harness constructs this app with a pinned backend ASGI app,
fictional seeded request sessions and one real backend Receptionist bearer. It
sets a cookie out of band via `DemoIssuer.cookie_for`; there is deliberately no
public role/bootstrap endpoint. No application modules are imported here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
import asyncio
import hashlib
import json
import math
import re
import secrets
from typing import Any
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
import httpx

from stage1_demo_adapter_core import AdapterRejected, MAX_BODY_BYTES, SessionBinding, admit_action
from stage1_demo_voice import (MAX_WAV_BYTES, VoiceInputRejected, VoiceRecognitionUnavailable,
                               ContainedVoiceRuntimeBinding, VoiceRuntimeBinding,
                               run_local_recognizer, target_for_persona,
                               validate_wav)


BASE = "/api/v1/appointments"
COOKIE = "stage1_demo_session"
STATIC = Path(__file__).parent / "static" / "demo"
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
LAB_PROGRESS_NATIVE07_EFFECT_SHA = "5bd59db323eb4da71b7b80ebf66aea88a3ef86fecd198b373523a58558103af7"
LAB_PROGRESS_NATIVE08_EFFECT_SHA = "62c2072574a9ded109d756a417810013068553554828e0cdf0c091de7dd2eb82"
LAB_PROGRESS_REPORT_SHA = "51ef618862352719a331237d286297dba2f4c0e6155d19c6d397ac141bfd3065"
LAB_WORKED_EXAMPLE_SHA = (
    "bb45fb0422d42c3bc2ad550c1833a3ead0237e2322cd236e372b70aaf40fb1ed",
    "1518da04fbfe56c0118091f3c868d773ed1dff98ac7716f58556d66bb99029c5",
    "2109fe40826f5ffd2b17703edaffb94cad5601501191bda2ee6abaaf4b2e9a1e",
    "aa66c550708842263910e7f305ede2261d173959fd342ab77698dbf616dbbfa8",
)


def project_lab_progress(raw: bytes | None, digest: str | None) -> dict[str, Any] | None:
    """Expose one exact startup-bound, closed projection; never open report paths."""
    if raw is None and digest is None:
        return None
    if (type(raw) is not bytes or not 1 <= len(raw) <= 16384 or
            type(digest) is not str or len(digest) != 64 or
            hashlib.sha256(raw).hexdigest() != digest or
            digest != LAB_PROGRESS_REPORT_SHA or
            LAB_PROGRESS_NATIVE07_EFFECT_SHA is None):
        raise ValueError("LAB_PROGRESS_BINDING_INVALID")

    def unique(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
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
            report["status"] != "REVIEWED_NONPASS_EFFECT_ACCOUNTING" or
            report["catalog_sha256"] != LAB_CATALOG_SHA or
            report["authored_catalog_sha256"] != "792b8d4cb627b721f607d1548b757f0b1960b2a2aa0b1592cd3674bc71bb071e" or
            report["evidence_through"] != "NATIVE08_REVIEWED_PRE_DOCKER" or
            report["native04_primary_sha256"] != NATIVE04_INPUTS["primary"][1] or
            report["native04_result_sha256"] != NATIVE04_INPUTS["result"][1] or
            report["catalog_cases"] != 16 or report["catalog_families"] != 11 or
            report["baseline_dispositions"] != {"current_controls": 2,
                "qualified_reused_boundaries": 4, "not_run": 10} or
            any(report[key] != value for key, value in {
                "request_detail": "NOT_IN_DELIVERED_PROJECTION",
                "proposal_detail": "NOT_IN_DELIVERED_PROJECTION",
                "actual_model": "NOT_RUN",
                "m1_model_binding": "OPEN",
                "generated_silence_voice": "NOT_RUN_AS_SPEECH_TEST",
                "genuine_ptt_voice": "NOT_RUN",
                "whole_journey_grade": "UNKNOWN", "display": "NOT_OBSERVED",
                "disclosure": "NOT_OBSERVED"}.items())):
        raise ValueError("LAB_PROGRESS_UNSUPPORTED_REPORT")
    attempts = report["attempts"]
    expected_attempts = (
        ("Native04", "DELIVERED_VALID_CONTROLS", 2, 6, 2,
         NATIVE04_INPUTS["effect_review"][1]),
        ("Native05", "NONPASS_NO_DELIVERED_SELECTED_RECORDS", 2, 6, 0,
         "c881ce80f6d14df14b2bd1613f2d02a7433752e2ff165aafebfed01ab0700f20"),
        ("Native06", "PRE_DOCKER_LAUNCH_FAILURE", 0, 0, 0,
         "003f06377fa76362325a6ecbcad1a6ce7983ee96c648b45c8e4d5454513f0899"))
    keys = {"name", "status", "selected_test_instances", "phase_reports",
            "delivered_selected_records", "cases", "effect_review_sha256"}
    if (type(attempts) is not list or len(attempts) != 5 or
            any(type(item) is not dict or set(item) != keys for item in attempts)):
        raise ValueError("LAB_PROGRESS_ATTEMPTS_INVALID")
    for item, expected in zip(attempts[:3], expected_attempts):
        if (any(type(item[key]) is not int for key in ("selected_test_instances",
                "phase_reports", "delivered_selected_records")) or
                tuple(item[key] for key in ("name", "status", "selected_test_instances",
                 "phase_reports", "delivered_selected_records", "effect_review_sha256")) != expected):
            raise ValueError("LAB_PROGRESS_ATTEMPTS_INVALID")
    valid_cases = {"Native04": (("create-valid-01", "PASSED"),
                                ("move-valid-timeonly-01", "PASSED")),
                   "Native05": (("create-duplicate-lost-response-09", "FAILED"),
                                ("move-duplicate-lost-response-10", "PASSED")),
                   "Native06": (),
                   "Native08": (),
                   "Native07": (("create-duplicate-lost-response-09", "FAILED"),
                                ("move-duplicate-lost-response-10", "PASSED"))}
    for item in attempts:
        cases = item["cases"]
        if (type(item["name"]) is not str or item["name"] not in valid_cases or
                type(cases) is not list or len(cases) != len(valid_cases[item["name"]]) or
                any(type(case) is not dict or set(case) != {"case_id", "call_phase"}
                    for case in cases) or
                tuple((case["case_id"], case["call_phase"]) for case in cases) !=
                    valid_cases[item["name"]]):
            raise ValueError("LAB_PROGRESS_CASE_PHASES_INVALID")
    native07 = attempts[3]
    if (native07["name"] != "Native07" or
            native07["effect_review_sha256"] != LAB_PROGRESS_NATIVE07_EFFECT_SHA or
            native07["status"] != "NONPASS_NO_DELIVERED_SELECTED_RECORDS" or
            tuple(native07[key] for key in ("selected_test_instances", "phase_reports",
                            "delivered_selected_records")) != (2, 6, 0) or
            any(type(native07[key]) is not int for key in
                ("selected_test_instances", "phase_reports", "delivered_selected_records"))):
        raise ValueError("LAB_PROGRESS_NATIVE07_INVALID")
    native08 = attempts[4]
    if (native08["name"] != "Native08" or
            native08["effect_review_sha256"] != LAB_PROGRESS_NATIVE08_EFFECT_SHA or
            native08["status"] != "PRE_DOCKER_LAUNCH_FAILURE" or
            tuple(native08[key] for key in ("selected_test_instances", "phase_reports",
                            "delivered_selected_records")) != (0, 0, 0) or
            any(type(native08[key]) is not int for key in
                ("selected_test_instances", "phase_reports", "delivered_selected_records"))):
        raise ValueError("LAB_PROGRESS_NATIVE08_INVALID")
    examples = report["reused_examples"]
    expected_examples = (
        ("move-attempted-identity-change-05", "NON_TIME_PAYLOAD_CHANGE",
         "HTTP_422_WITH_UNCHANGED_SNAPSHOT", "UNCHANGED_SNAPSHOT_DETAILS_NOT_DELIVERED"),
        ("move-stale-expired-authority-06", "STALE_OR_EXPIRED_AUTHORITY",
         "SEPARATE_REFUSAL_TESTS", "NOT_IN_DELIVERED_PROJECTION"),
        ("move-source-cancelled-08", "CANCELLED_SOURCE",
         "REJECTED_WITH_UNCHANGED_SNAPSHOT", "UNCHANGED_SNAPSHOT_DETAILS_NOT_DELIVERED"),
        ("move-duplicate-lost-response-10", "COMPLETED_REPLAY_WITHOUT_LOST_RESPONSE",
         "EQUAL_RESPONSE_UNCHANGED_SNAPSHOT_AND_CHANGED_BODY_CONFLICT",
         "UNCHANGED_SNAPSHOT_DETAILS_NOT_DELIVERED"))
    example_keys = {"case_id", "disturbance", "actual_validation", "before_after", "outcome"}
    if (type(examples) is not list or len(examples) != 4 or
            any(type(item) is not dict or set(item) != example_keys or
                tuple(item[key] for key in ("case_id", "disturbance",
                      "actual_validation", "before_after")) != expected or
                item["outcome"] != "QUALIFIED_REUSED_BOUNDARY_ONLY"
                for item, expected in zip(examples, expected_examples))):
        raise ValueError("LAB_PROGRESS_EXAMPLES_INVALID")
    worked = report["worked_examples"]
    worked_keys = {"case_id", "evidence_kind", "authored_request",
                   "authored_expected_proposal", "proposal_observation",
                   "actual_validation", "before_after", "readback", "command_audit",
                   "outcome"}
    worked_ids = ("create-valid-01", "move-valid-timeonly-01",
                  "move-attempted-identity-change-05", "move-source-cancelled-08")
    if (type(worked) is not list or len(worked) != 4 or
            any(type(item) is not dict or set(item) != worked_keys or
                item["case_id"] != case_id or
                type(item["before_after"]) is not dict or
                set(item["before_after"]) != {"before", "after"} or
                hashlib.sha256(json.dumps(item, sort_keys=True, separators=(",", ":"),
                    ensure_ascii=True).encode()).hexdigest() != expected_sha
                for item, case_id, expected_sha in zip(worked, worked_ids,
                                                       LAB_WORKED_EXAMPLE_SHA))):
        raise ValueError("LAB_PROGRESS_WORKED_EXAMPLES_INVALID")
    return {"schema": "emr4.stage1_reliability_progress_view.v2",
            "catalog_cases": 16, "catalog_families": 11,
            "authored_catalog_sha256": report["authored_catalog_sha256"],
            "evidence_through": report["evidence_through"],
            "baseline_dispositions": report["baseline_dispositions"],
            "attempts": attempts, "reused_examples": examples,
            "worked_examples": worked,
            "request_detail": report["request_detail"],
            "proposal_detail": report["proposal_detail"],
            "actual_model": "NOT_RUN", "m1_model_binding": "OPEN",
            "generated_silence_voice": "NOT_RUN_AS_SPEECH_TEST",
            "genuine_ptt_voice": "NOT_RUN",
            "whole_journey_grade": "UNKNOWN", "display": "NOT_OBSERVED",
            "disclosure": "NOT_OBSERVED"}


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
    voice_runtime: VoiceRuntimeBinding | ContainedVoiceRuntimeBinding | None = field(
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


@dataclass(repr=False)
class _Session:
    binding: SessionBinding
    staff_bearer: str | None
    seeded_appointment_id: str | None
    expires_at: datetime
    proposal: dict[str, Any] | None = None
    uncertain: dict[str, Any] | None = None
    voice_nonce: str = field(default_factory=lambda: secrets.token_urlsafe(24), repr=False)


class DemoIssuer:
    """Trusted harness handle, not an HTTP endpoint or client role selector."""

    def __init__(self, config: DemoConfig):
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
        for seed in config.seeds:
            token = secrets.token_urlsafe(32)
            binding = SessionBinding(
                persona=seed.persona, session_id=secrets.token_urlsafe(24),
                csrf=secrets.token_urlsafe(24), practice_id=config.practice_id,
                patient_id=config.patient_id, request_id=seed.request_id,
                patient_capability=seed.patient_capability,
                staff_user_id=seed.staff_user_id if seed.persona == "staff" else None,
            )
            self._sessions[token] = _Session(binding, seed.staff_bearer,
                seed.seeded_appointment_id, datetime.now(timezone.utc) + timedelta(hours=2))

    def cookie_for(self, persona: str, request_id: str) -> tuple[str, str]:
        """Return name/value only to the reviewed local harness; do not log it."""
        for token, session in self._sessions.items():
            b = session.binding
            if b.persona == persona and b.request_id == request_id:
                return COOKIE, token
        raise ValueError("SESSION_NOT_CONFIGURED")

    def issue_cookie(self, response: JSONResponse, persona: str, request_id: str) -> None:
        """Trusted fixture calls this out of band; no public issuance route."""
        name, value = self.cookie_for(persona, request_id)
        response.set_cookie(name, value, max_age=7200, httponly=True,
                            samesite="strict", secure=False, path="/demo/stage1")

    def session_for(self, request: Request) -> _Session:
        token = request.cookies.get(COOKIE)
        session = self._sessions.get(token or "")
        if session is None or datetime.now(timezone.utc) >= session.expires_at:
            raise HTTPException(status_code=404, detail="DEMO_SESSION_UNAVAILABLE")
        return session


def create_stage1_demo_app(config: DemoConfig) -> tuple[FastAPI, DemoIssuer]:
    """Create an isolated loopback ASGI app; caller owns listener binding."""
    issuer = DemoIssuer(config)
    app = FastAPI(title="Stage 1 synthetic local demo", docs_url=None, redoc_url=None,
                  openapi_url=None)
    voice_lock = asyncio.Lock()

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

    async def backend(method: str, path: str, session: _Session, *, body=None,
                      key: str | None = None, patient: bool = False) -> Any:
        headers = {"Cache-Control": "no-store"}
        if patient:
            capability = config.request_capabilities.get(session.binding.request_id)
            if not capability:
                raise HTTPException(status_code=404, detail="REQUEST_UNAVAILABLE")
            headers["X-Patient-Request-Capability"] = capability
        else:
            if not session.staff_bearer:
                raise HTTPException(status_code=403, detail="STAFF_UNAVAILABLE")
            headers["Authorization"] = "Bearer " + session.staff_bearer
        if key:
            headers["Idempotency-Key"] = key
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=config.backend_app,
                client=("127.0.0.1", 12345), raise_app_exceptions=False), base_url="http://127.0.0.1",
                follow_redirects=False, timeout=10) as client:
            response = await client.request(method, BASE + path, headers=headers, json=body)
        if response.status_code >= 400:
            # A current-authority refusal is definitive, never a lost reply.
            # Keep its body opaque and consistent with other stale/denied
            # backend outcomes at this demo boundary.
            raise HTTPException(status_code=409 if response.status_code in {400, 401, 403, 404, 409, 422} else 503,
                                detail="BACKEND_ACTION_UNAVAILABLE")
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
            request = await patient_read(session)
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
            capability = config.request_capabilities.get(session.binding.request_id)
            if not capability:
                raise HTTPException(status_code=404, detail="REQUEST_UNAVAILABLE")
            # Dedicated request capability belongs to trusted fixture, not the
            # staff browser session. Backend is the only option source.
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=config.backend_app,
                    client=("127.0.0.1", 12345), raise_app_exceptions=False), base_url="http://127.0.0.1",
                    follow_redirects=False, timeout=10) as client:
                response = await client.get(BASE + f"/patient-requests/{session.binding.request_id}/options",
                    params={"request_version": request["request_version"]},
                    headers={"X-Patient-Request-Capability": capability})
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
            raise HTTPException(status_code=409, detail="REQUEST_RECEIPT_MISMATCH")
        snapshot = await refreshed(session)
        current = snapshot["request"]
        if (current.get("request_id") != session.binding.request_id or
                current.get("state") not in {"submitted", "booked"} or
                type(current.get("request_version")) is not int or
                current["request_version"] < expected_version or
                current.get("preference_date") != payload["date"] or
                local_minute(current.get("earliest_local")) != payload["earliest_local"] or
                local_minute(current.get("latest_local")) != payload["latest_local"]):
            raise HTTPException(status_code=409, detail="REQUEST_READBACK_MISMATCH")
        return snapshot

    async def uncertain_snapshot(session: _Session) -> JSONResponse:
        try:
            return no_store({**(await refreshed(session)), "uncertain": True})
        except HTTPException:
            return no_store({"uncertain": True})

    @app.get("/demo/stage1/session")
    async def session_route(request: Request):
        local(request)
        session = issuer.session_for(request)
        voice_ready = (config.voice_runtime is not None and
            (config.voice_runtime.ready(session.binding.persona)
             if isinstance(config.voice_runtime, ContainedVoiceRuntimeBinding)
             else config.voice_runtime.ready()))
        return no_store({"persona": session.binding.persona, "csrf": session.binding.csrf,
            "zone": config.timezone, "demo_clock": config.demo_clock,
            "voice_available": voice_ready, "voice_nonce": session.voice_nonce if voice_ready else None})

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
        return FileResponse(STATIC / "stage1-interactive.html", headers={"Cache-Control": "no-store"})

    @app.get("/demo/stage1/{asset}")
    async def asset(request: Request, asset: str):
        local(request); issuer.session_for(request)
        if asset not in {"stage1-interactive.css", "stage1-interactive.js",
                         "stage1-local-voice.js"}:
            raise HTTPException(status_code=404)
        return FileResponse(STATIC / asset, headers={"Cache-Control": "no-store"})

    @app.post("/demo/stage1/voice")
    async def voice_route(request: Request):
        local(request)
        session = issuer.session_for(request)
        binding = config.voice_runtime
        if binding is None or not (binding.ready(session.binding.persona)
                if isinstance(binding, ContainedVoiceRuntimeBinding)
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
        # A nonce authorises exactly one bounded clip, never a domain action.
        session.voice_nonce = secrets.token_urlsafe(24)
        next_nonce = session.voice_nonce
        parts: list[bytes] = []
        size = 0
        async for chunk in request.stream():
            size += len(chunk)
            if size > MAX_WAV_BYTES:
                return no_store({"error": "VOICE_TOO_LARGE"}, 413)
            parts.append(chunk)
        raw = b"".join(parts)
        try:
            validate_wav(raw)
        except VoiceInputRejected:
            return no_store({"error": "VOICE_FORMAT_UNAVAILABLE"}, 400)
        if voice_lock.locked():
            return no_store({"error": "VOICE_BUSY"}, 429)
        try:
            async with voice_lock:
                if isinstance(binding, ContainedVoiceRuntimeBinding):
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
        if action == "refresh":
            return no_store({**(await refreshed(session)), "uncertain": session.uncertain is not None})
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
            try:
                result = await backend("POST", path, session, body=pending["payload"],
                    key=pending["key"], patient=family == "submit_request")
            except (httpx.TimeoutException, httpx.TransportError):
                return await uncertain_snapshot(session)
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
            try:
                result = await backend("POST", f"/patient-requests/{session.binding.request_id}/submit",
                    session, body=payload, key=key, patient=True)
            except (httpx.TimeoutException, httpx.TransportError):
                session.uncertain = pending
                raise HTTPException(status_code=503, detail="COMMAND_OUTCOME_UNCERTAIN") from None
            except HTTPException as exc:
                if exc.status_code == 503:
                    session.uncertain = pending
                raise
            session.uncertain = pending
            snapshot = await verified_submission(session, result, payload)
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
            response = no_store({"outcome": "committed", "appointment": current})
            session.uncertain = None
            session.proposal = None
            return response
        raise HTTPException(status_code=404, detail="ACTION_UNAVAILABLE")

    return app, issuer
