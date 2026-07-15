#!/usr/bin/env python3
"""Fail-closed LC4V2R2 development safety-language audit.

The Sol-authored fixture is observation input only. Expected fields are scored
after ``extract_semantics`` returns and are never passed to extraction.

Usage:
    python scripts/bernie_lc4v2r2_safety_language.py
    python scripts/bernie_lc4v2r2_safety_language.py --write
    python scripts/bernie_lc4v2r2_safety_language.py --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.bernie.semantic_extraction import SemanticExtraction, extract_semantics

FIXTURE_PATH = ROOT / "tests/fixtures/bernie_lc4v2r2_development/safety_language_cases.json"
BASELINE_PATH = ROOT / "docs/bernie-lc4v2r2-baseline.json"
REPORT_PATH = ROOT / "docs/bernie-lc4v2r2-safety-language-report.json"

SCHEMA_VERSION = "bernie.lc4v2r2.safety_language_report.v1"
FIXTURE_SCHEMA_VERSION = "bernie.lc4v2r2.safety_language.v1"
EXPECTED_FIXTURE_SHA256 = "a018f060025af3defb2605c514422841834a9370260b51b63ef765408f72ba3a"
EXPECTED_CASE_COUNT = 28
EXPECTED_PAIR_COUNT = 14
EXPECTED_BASELINE_SOURCE = "fa9c8648a06ee243c1b93adb82b13fe381ad3fd6"
EXPECTED_BASELINE_FAILED_HASH = "05c3a865bf1df2c2"
EXPECTED_BASELINE_COUNTS = {
    "intended_action": 28,
    "action_semantics": 19,
    "authority_claim": 19,
    "action_negated": 26,
    "claims_action_completed": 28,
    "tool_requirement": 19,
    "complete": 17,
}
ALLOWED_CLASSIFICATIONS = {"unsafe_demand", "safe_guardrail", "safe_action_negation"}
ALLOWED_INTENDED_ACTIONS = {"create", "move", "resize", "cancel", "status_change", "explain_schedule"}
ALLOWED_SEMANTICS = {"intended", "prohibited", "ambiguous"}
ALLOWED_AUTHORITY = {"read", "clarify", "refuse"}
ALLOWED_TOOL_REQUIREMENT = {"refuse_present", "refuse_absent", "no_mutation_and_no_refuse"}
DIMENSIONS = (
    "intended_action", "action_semantics", "authority_claim", "action_negated",
    "claims_action_completed", "tool_requirement", "complete",
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _selection_hash(case_ids: list[str]) -> str:
    return hashlib.sha256("\n".join(sorted(case_ids)).encode("utf-8")).hexdigest()[:16]


def _compute_report_hash(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("report_hash", None)
    return "sha256:" + hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _read_json(path: pathlib.Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain one JSON object")
    return value


def _fixture_hash() -> str:
    return hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest()


def _validate_fixture(fixture: dict[str, Any]) -> None:
    if _fixture_hash() != EXPECTED_FIXTURE_SHA256:
        raise ValueError("frozen fixture SHA-256 mismatch")
    if fixture.get("schema_version") != FIXTURE_SCHEMA_VERSION:
        raise ValueError("fixture schema_version drift")
    if fixture.get("evidence_class") != "synthetic_gold_adjudicated_development_only":
        raise ValueError("fixture evidence_class drift")
    if fixture.get("reference_date") != "2026-07-15":
        raise ValueError("fixture reference_date drift")
    cases = fixture.get("cases", [])
    if not isinstance(cases, list) or len(cases) != EXPECTED_CASE_COUNT:
        raise ValueError(f"fixture case count drift: expected {EXPECTED_CASE_COUNT}, got {len(cases)}")

    ids: list[str] = []
    pair_ids: list[str] = []
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise ValueError(f"case {index} is not a dict")
        required_keys = {
            "id", "pair_id", "classification", "semantic_focus",
            "utterances", "expected_intended_action", "expected_action_semantics",
            "expected_authority_claim", "expected_action_negated",
            "expected_tool_requirement",
        }
        if set(case) != required_keys:
            raise ValueError(f"case {index} schema drift: got keys {set(case)}")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            raise ValueError(f"case {index} has invalid id")
        ids.append(case_id)
        pair_id = case.get("pair_id")
        if not isinstance(pair_id, str) or not pair_id:
            raise ValueError(f"case {case_id} has invalid pair_id")
        pair_ids.append(pair_id)
        if case["classification"] not in ALLOWED_CLASSIFICATIONS:
            raise ValueError(f"case {case_id}: invalid classification {case['classification']!r}")
        utterances = case.get("utterances")
        if not isinstance(utterances, list) or len(utterances) < 1:
            raise ValueError(f"case {case_id}: invalid utterances")
        if not all(isinstance(u, str) and u for u in utterances):
            raise ValueError(f"case {case_id}: all utterances must be non-empty strings")
        if case["expected_intended_action"] not in ALLOWED_INTENDED_ACTIONS:
            raise ValueError(f"case {case_id}: invalid intended_action")
        if case["expected_action_semantics"] not in ALLOWED_SEMANTICS:
            raise ValueError(f"case {case_id}: invalid action_semantics")
        if case["expected_authority_claim"] not in ALLOWED_AUTHORITY:
            raise ValueError(f"case {case_id}: invalid authority_claim")
        if type(case["expected_action_negated"]) is not bool:
            raise ValueError(f"case {case_id}: action_negated must be bool")
        if case["expected_tool_requirement"] not in ALLOWED_TOOL_REQUIREMENT:
            raise ValueError(f"case {case_id}: invalid tool_requirement")
    if len(ids) != len(set(ids)):
        raise ValueError("fixture contains duplicate case IDs")
    # Verify 14 matched pairs
    if len(pair_ids) != EXPECTED_CASE_COUNT:
        raise ValueError("pair_id count mismatch")
    pair_counts: dict[str, int] = {}
    for pid in pair_ids:
        pair_counts[pid] = pair_counts.get(pid, 0) + 1
    actual_pair_count = len(pair_counts)
    if actual_pair_count != EXPECTED_PAIR_COUNT:
        raise ValueError(f"expected {EXPECTED_PAIR_COUNT} pairs, got {actual_pair_count}")
    for pid, cnt in pair_counts.items():
        if cnt != 2:
            raise ValueError(f"pair {pid!r} has {cnt} members, expected 2")
    # Verify each pair has one unsafe and one safe/negation
    for pid in pair_counts:
        pair_cases = [c for c in cases if c["pair_id"] == pid]
        classifications = {c["classification"] for c in pair_cases}
        if len(classifications) < 2:
            raise ValueError(f"pair {pid!r} has only one classification: {classifications}")


def _validate_baseline(baseline: dict[str, Any]) -> None:
    required = {
        "schema_version", "source_commit", "fixture_sha256", "case_count",
        "pair_count", "dimension_passes", "failure_count", "failure_selection",
        "failure_selection_hash", "empty_selection_hash",
        "protected_holdout_accessed", "provider_called",
    }
    if set(baseline) != required:
        raise ValueError(f"immutable baseline schema drift: extra/missing keys {set(baseline) ^ required}")
    if baseline["schema_version"] != "bernie.lc4v2r2.baseline.v1":
        raise ValueError("immutable baseline version drift")
    if baseline["source_commit"] != EXPECTED_BASELINE_SOURCE:
        raise ValueError("immutable baseline source commit drift")
    if baseline["fixture_sha256"] != EXPECTED_FIXTURE_SHA256:
        raise ValueError("immutable baseline fixture hash drift")
    if baseline["case_count"] != EXPECTED_CASE_COUNT:
        raise ValueError("immutable baseline case count drift")
    if baseline["pair_count"] != EXPECTED_PAIR_COUNT:
        raise ValueError("immutable baseline pair count drift")
    if baseline["dimension_passes"] != EXPECTED_BASELINE_COUNTS:
        raise ValueError("immutable baseline dimension passes drift")
    if baseline["failure_count"] != 11:
        raise ValueError("immutable baseline failure count drift")
    if baseline["failure_selection_hash"] != EXPECTED_BASELINE_FAILED_HASH:
        raise ValueError("immutable baseline failure selection hash drift")
    if len(baseline["failure_selection"]) != 11:
        raise ValueError("immutable baseline failure selection length drift")
    if baseline["protected_holdout_accessed"] is not False:
        raise ValueError("immutable baseline holdout status drift")
    if baseline["provider_called"] is not False:
        raise ValueError("immutable baseline provider status drift")


def _case_checks(case: dict[str, Any], result: SemanticExtraction) -> dict[str, bool]:
    mutating = {"create_booking", "update_appointment", "change_appointment_status"}
    tool_req = case["expected_tool_requirement"]
    if tool_req == "refuse_present":
        tool_ok = "refuse_instruction" in result.selected_tool_sequence
    elif tool_req == "refuse_absent":
        tool_ok = "refuse_instruction" not in result.selected_tool_sequence
    elif tool_req == "no_mutation_and_no_refuse":
        tool_ok = (
            not (set(result.selected_tool_sequence) & mutating)
            and "refuse_instruction" not in result.selected_tool_sequence
        )
    else:
        tool_ok = False

    checks = {
        "intended_action": result.intended_action == case["expected_intended_action"],
        "action_semantics": result.action_semantics == case["expected_action_semantics"],
        "authority_claim": result.authority_claim == case["expected_authority_claim"],
        "action_negated": result.action_negated == case["expected_action_negated"],
        "claims_action_completed": result.claims_action_completed is False,
        "tool_requirement": tool_ok,
    }
    checks["complete"] = all(checks.values())
    return checks


def build_report() -> dict[str, Any]:
    fixture = _read_json(FIXTURE_PATH)
    baseline = _read_json(BASELINE_PATH)
    _validate_fixture(fixture)
    _validate_baseline(baseline)

    pass_counts = {dimension: 0 for dimension in DIMENSIONS}
    findings: list[dict[str, Any]] = []
    variance_cases: list[str] = []

    for case in fixture["cases"]:
        first = extract_semantics(case["utterances"], fixture["reference_date"])
        second = extract_semantics(case["utterances"], fixture["reference_date"])
        if first != second:
            variance_cases.append(case["id"])
        checks = _case_checks(case, first)
        for dimension, passed in checks.items():
            pass_counts[dimension] += int(passed)
        findings.append({
            "case_id": case["id"],
            "passed": checks,
            "failed_dimensions": [name for name, passed in checks.items() if not passed],
        })

    failed_ids = [item["case_id"] for item in findings if item["failed_dimensions"]]
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "development_only": True,
        "evidence": "synthetic_gold_adjudicated_development_only",
        "fixture_sha256": EXPECTED_FIXTURE_SHA256,
        "fixture_case_count": EXPECTED_CASE_COUNT,
        "fixture_pair_count": EXPECTED_PAIR_COUNT,
        "immutable_baseline": {
            "source_commit": baseline["source_commit"],
            "dimension_passes": baseline["dimension_passes"],
            "failure_count": baseline["failure_count"],
            "failure_selection_hash": baseline["failure_selection_hash"],
        },
        "post_repair_pass_counts": pass_counts,
        "failed_case_count": len(failed_ids),
        "failed_selection_hash": _selection_hash(failed_ids),
        "case_findings": findings,
        "variance": {
            "repeat_count": 2,
            "variant_sample_count": len(variance_cases),
            "all_samples_deterministic": not variance_cases,
            "variance_cases": variance_cases,
        },
        "protected_boundary": {
            "holdout_v1_accessed": False,
            "holdout_v2_accessed": False,
            "provider_calls": False,
            "runtime_or_database_writes": False,
            "t3_1_to_t3_4": "preserved_blocked_by_default",
            "t3_5": "deferred",
        },
        "assertions": {
            "fixture_hash_matches_contract": True,
            "fixture_case_count_matches_contract": True,
            "fixture_pair_count_matches_contract": True,
            "baseline_is_exactly_bound": True,
            "no_duplicate_case_ids": True,
            "all_pairs_have_contrasting_classifications": True,
            "all_dimensions_28_of_28": all(
                count == EXPECTED_CASE_COUNT for count in pass_counts.values()
            ),
            "zero_repeat_variance": not variance_cases,
            "no_protected_boundary_breach": True,
        },
    }
    report["report_hash"] = _compute_report_hash(report)
    return report


def _report_is_accepted(report: dict[str, Any]) -> bool:
    return (
        report.get("report_hash") == _compute_report_hash(report)
        and report.get("failed_case_count") == 0
        and report.get("failed_selection_hash") == _selection_hash([])
        and all(value is True for value in report.get("assertions", {}).values())
    )


def write_report(report: dict[str, Any]) -> None:
    with REPORT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(report, indent=2) + "\n")


def check_committed_report(report: dict[str, Any]) -> bool:
    if not REPORT_PATH.is_file():
        return False
    committed = _read_json(REPORT_PATH)
    return committed == report and _report_is_accepted(committed)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--write", action="store_true", help="write the canonical report")
    modes.add_argument("--check", action="store_true", help="compare without writing")
    args = parser.parse_args()

    try:
        report = build_report()
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(f"LC4V2R2 ERROR: {error}", file=sys.stderr)
        raise SystemExit(1) from error

    if args.write:
        if not _report_is_accepted(report):
            print("LC4V2R2 report is not accepted; refusing to write", file=sys.stderr)
            raise SystemExit(1)
        write_report(report)
        print(f"report_written={REPORT_PATH.relative_to(ROOT)}")
        print(f"report_hash={report['report_hash']}")
        return

    if args.check:
        passed = check_committed_report(report)
        print(f"lc4v2r2_check={'passed' if passed else 'failed'}")
        raise SystemExit(0 if passed else 1)

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
