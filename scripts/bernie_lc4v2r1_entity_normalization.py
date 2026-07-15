#!/usr/bin/env python3
"""Fail-closed LC4V2R1 development entity/normalization audit.

The Sol-authored fixture is observation input only. Expected fields are scored
after ``extract_semantics`` returns and are never passed to extraction.

Usage:
    python scripts/bernie_lc4v2r1_entity_normalization.py
    python scripts/bernie_lc4v2r1_entity_normalization.py --write
    python scripts/bernie_lc4v2r1_entity_normalization.py --check
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

FIXTURE_PATH = ROOT / "tests/fixtures/bernie_lc4v2r1_development/entity_normalization_cases.json"
BASELINE_PATH = ROOT / "docs/bernie-lc4v2r1-baseline.json"
REPORT_PATH = ROOT / "docs/bernie-lc4v2r1-entity-normalization-report.json"

SCHEMA_VERSION = "lc4v2r1.entity_normalization_report.v1"
FIXTURE_SCHEMA_VERSION = "lc4v2r1.entity_normalization_development.v1"
EXPECTED_FIXTURE_SHA256 = "0f957518d1481ce831a55ca8d12388f245ae89ae516e96ef1d5037080d925afd"
EXPECTED_CASE_COUNT = 21
EXPECTED_BASELINE_SOURCE = "7abf3aa930c63af7e3729c307f2e172cff50f47f"
EXPECTED_BASELINE_FAILED_HASH = "ddfbc280bb822993"
EXPECTED_BASELINE_COUNTS = {
    "normalized_values": 17,
    "entity_semantics": 5,
    "requires_clarification": 17,
    "authority": 17,
    "tool_safety": 17,
    "claims_action_completed": 21,
    "complete": 4,
}
EXPECTED_ENTITY_KEYS = {
    "practitioner", "patient", "location", "appointment_type", "duration"
}
ALLOWED_RELATIONS = {"exact", "omitted", "ambiguous", "corrected", "negated"}
ALLOWED_NORMALIZED_KEYS = {
    "appointment_date", "earliest_time", "latest_time", "duration_minutes",
    "time_period",
}
MUTATING_TOOLS = {"create_booking", "update_appointment", "change_appointment_status"}
DIMENSIONS = (
    "normalized_values", "entity_semantics", "requires_clarification",
    "authority", "tool_safety", "claims_action_completed", "complete",
)

FIXTURE_TOP_KEYS = {
    "schema_version", "provenance", "adjudication", "reference_date", "cases"
}
CASE_KEYS = {
    "case_id", "utterances", "expected_normalized_values",
    "expected_entity_semantics", "expected_requires_clarification",
    "expected_authority", "mutating_tools_allowed",
}


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
    if set(fixture) != FIXTURE_TOP_KEYS:
        raise ValueError("fixture top-level schema drift")
    if fixture["schema_version"] != FIXTURE_SCHEMA_VERSION:
        raise ValueError("fixture schema_version drift")
    if fixture["provenance"] != "gold" or fixture["adjudication"] != "adjudicated":
        raise ValueError("fixture must remain Gold/adjudicated")
    if fixture["reference_date"] != "2026-07-15":
        raise ValueError("fixture reference_date drift")
    cases = fixture["cases"]
    if not isinstance(cases, list) or len(cases) != EXPECTED_CASE_COUNT:
        raise ValueError("fixture case count drift")

    ids: list[str] = []
    for index, case in enumerate(cases):
        if not isinstance(case, dict) or set(case) != CASE_KEYS:
            raise ValueError(f"case {index} schema drift")
        case_id = case["case_id"]
        if not isinstance(case_id, str) or not case_id:
            raise ValueError(f"case {index} has invalid case_id")
        ids.append(case_id)
        utterances = case["utterances"]
        if not isinstance(utterances, list) or not utterances or not all(
            isinstance(item, str) and item for item in utterances
        ):
            raise ValueError(f"case {case_id} has invalid utterances")
        normalized = case["expected_normalized_values"]
        if not isinstance(normalized, dict) or not set(normalized) <= ALLOWED_NORMALIZED_KEYS:
            raise ValueError(f"case {case_id} has invalid normalized-value schema")
        entities = case["expected_entity_semantics"]
        if not isinstance(entities, dict) or set(entities) != EXPECTED_ENTITY_KEYS:
            raise ValueError(f"case {case_id} must name all five entity slots")
        if not all(value in ALLOWED_RELATIONS for value in entities.values()):
            raise ValueError(f"case {case_id} has an unsupported entity relation")
        if type(case["expected_requires_clarification"]) is not bool:
            raise ValueError(f"case {case_id} has invalid clarification expectation")
        if case["expected_authority"] not in {"read", "clarify", "refuse"}:
            raise ValueError(f"case {case_id} has invalid authority expectation")
        if type(case["mutating_tools_allowed"]) is not bool:
            raise ValueError(f"case {case_id} has invalid tool-safety expectation")
    if len(ids) != len(set(ids)):
        raise ValueError("fixture contains duplicate case IDs")


def _validate_baseline(baseline: dict[str, Any]) -> None:
    required = {
        "schema_version", "development_only", "evidence", "parser_source_commit",
        "fixture_sha256", "case_count", "pass_counts", "failed_case_count",
        "failed_selection_hash", "findings", "protected_boundary",
    }
    if set(baseline) != required:
        raise ValueError("immutable baseline schema drift")
    if baseline["schema_version"] != "lc4v2r1.entity_normalization_baseline.v1":
        raise ValueError("immutable baseline version drift")
    if baseline["development_only"] is not True:
        raise ValueError("immutable baseline lost development-only marker")
    if baseline["parser_source_commit"] != EXPECTED_BASELINE_SOURCE:
        raise ValueError("immutable baseline source commit drift")
    if baseline["fixture_sha256"] != EXPECTED_FIXTURE_SHA256:
        raise ValueError("immutable baseline fixture hash drift")
    if baseline["case_count"] != EXPECTED_CASE_COUNT:
        raise ValueError("immutable baseline case count drift")
    if baseline["pass_counts"] != EXPECTED_BASELINE_COUNTS:
        raise ValueError("immutable baseline pass counts drift")
    if baseline["failed_case_count"] != 17:
        raise ValueError("immutable baseline failed count drift")
    if baseline["failed_selection_hash"] != EXPECTED_BASELINE_FAILED_HASH:
        raise ValueError("immutable baseline selection hash drift")
    findings = baseline["findings"]
    if not isinstance(findings, list) or len(findings) != EXPECTED_CASE_COUNT:
        raise ValueError("immutable baseline findings drift")
    failed_ids = [
        item["case_id"] for item in findings
        if isinstance(item, dict) and item.get("failed_dimensions")
    ]
    if len(failed_ids) != 17 or _selection_hash(failed_ids) != EXPECTED_BASELINE_FAILED_HASH:
        raise ValueError("immutable baseline findings do not bind the frozen selection")
    boundary = baseline["protected_boundary"]
    if boundary != {
        "holdout_v1_accessed": False,
        "holdout_v2_accessed": False,
        "provider_calls": False,
        "runtime_or_database_writes": False,
        "t3_5": "deferred",
    }:
        raise ValueError("immutable baseline protected boundary drift")


def _case_checks(case: dict[str, Any], result: SemanticExtraction) -> dict[str, bool]:
    checks = {
        "normalized_values": result.normalized_values == case["expected_normalized_values"],
        "entity_semantics": result.entity_semantics == case["expected_entity_semantics"],
        "requires_clarification": (
            result.requires_clarification is case["expected_requires_clarification"]
        ),
        "authority": result.authority_claim == case["expected_authority"],
        "tool_safety": (
            case["mutating_tools_allowed"]
            or not (set(result.selected_tool_sequence) & MUTATING_TOOLS)
        ),
        "claims_action_completed": result.claims_action_completed is False,
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
            variance_cases.append(case["case_id"])
        checks = _case_checks(case, first)
        for dimension, passed in checks.items():
            pass_counts[dimension] += int(passed)
        findings.append({
            "case_id": case["case_id"],
            "passed": checks,
            "failed_dimensions": [name for name, passed in checks.items() if not passed],
        })

    failed_ids = [item["case_id"] for item in findings if item["failed_dimensions"]]
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "development_only": True,
        "evidence": "synthetic_gold_adjudicated",
        "fixture_sha256": EXPECTED_FIXTURE_SHA256,
        "fixture_case_count": EXPECTED_CASE_COUNT,
        "immutable_baseline": {
            "parser_source_commit": baseline["parser_source_commit"],
            "pass_counts": baseline["pass_counts"],
            "failed_case_count": baseline["failed_case_count"],
            "failed_selection_hash": baseline["failed_selection_hash"],
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
            "baseline_is_exactly_bound": True,
            "all_relationships_allowed": True,
            "no_duplicate_case_ids": True,
            "all_dimensions_21_of_21": all(
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
        print(f"LC4V2R1 ERROR: {error}", file=sys.stderr)
        raise SystemExit(1) from error

    if args.write:
        if not _report_is_accepted(report):
            print("LC4V2R1 report is not accepted; refusing to write", file=sys.stderr)
            raise SystemExit(1)
        write_report(report)
        print(f"report_written={REPORT_PATH.relative_to(ROOT)}")
        print(f"report_hash={report['report_hash']}")
        return

    if args.check:
        passed = check_committed_report(report)
        print(f"lc4v2r1_check={'passed' if passed else 'failed'}")
        raise SystemExit(0 if passed else 1)

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
