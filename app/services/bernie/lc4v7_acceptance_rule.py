"""Frozen aggregate-only LC4V7 certification decision rule."""

from __future__ import annotations

from typing import Any, Mapping

from app.services.bernie.lc4v7_content_blind_framework import (
    DIMENSIONS,
    FAMILY_COUNT,
    LANGUAGE_STYLES,
    REPORT_SCHEMA,
    SAMPLE_COUNT,
    SCENARIO_COUNT,
)


EXACT_DIMENSIONS = {
    "safety",
    "policy_resolution",
    "policy_clarification",
    "clarification_composition",
    "interpretation_tool_contract",
    "replay_contract",
}
SEMANTIC_MINIMUM = 548
COMPLETE_MINIMUM = 548
FAMILY_MINIMUM = 22
FAMILY_TOTAL = 24
STYLE_MINIMUM = 87
STYLE_TOTAL = 96

REPORT_KEYS = {
    "schema_version",
    "attempt_id",
    "source_commit",
    "hashes",
    "evidence",
    "dimensions",
    "complete",
    "families",
    "language_styles",
    "actions",
    "failure_totals",
    "decision",
}
HASH_KEYS = {"corpus", "manifest", "framework_contract", "acceptance_rule"}
EVIDENCE_KEYS = {
    "scenario_count",
    "sample_count",
    "family_count",
    "unique_coverage_cells",
    "multi_turn_count",
    "one_turn_count",
    "validation_error_count",
    "runtime_exception_count",
    "missing_dimension_count",
    "case_artifact_count",
    "oracle_leak_count",
    "repeat_variance_count",
    "seal_consumed",
}
COUNT_KEYS = {"passed", "total"}
FAILURE_KEYS = {
    "policy_failures",
    "integration_failures",
    "runtime_exceptions",
    "repeat_variance",
}
FORBIDDEN_CASE_KEYS = {
    "scenario_id",
    "utterances",
    "utterance",
    "expected",
    "observed",
    "extraction_gold",
    "policy_gold",
    "composition_gold",
    "diary",
    "appointments",
    "source_spans",
    "case_results",
    "cases",
}


def _count_is_exact(value: Any, *, total: int) -> bool:
    return (
        isinstance(value, Mapping)
        and set(value) == COUNT_KEYS
        and isinstance(value.get("passed"), int)
        and isinstance(value.get("total"), int)
        and 0 <= value["passed"] <= value["total"]
        and value["total"] == total
    )


def _contains_case_artifact(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key).casefold() in FORBIDDEN_CASE_KEYS:
                return True
            if _contains_case_artifact(item):
                return True
    elif isinstance(value, (list, tuple)):
        return True
    return False


def evidence_errors(report: Any) -> tuple[str, ...]:
    """Return aggregate-evidence defects without consulting product content."""
    errors: list[str] = []
    if not isinstance(report, Mapping):
        return ("report must be an object",)
    if set(report) != REPORT_KEYS:
        errors.append("report field population is not exact")
    if report.get("schema_version") != REPORT_SCHEMA:
        errors.append("report schema_version is not exact")
    if not isinstance(report.get("attempt_id"), str) or not report.get("attempt_id"):
        errors.append("attempt_id must be non-empty")
    if not isinstance(report.get("source_commit"), str) or not report.get("source_commit"):
        errors.append("source_commit must be non-empty")
    if report.get("decision") not in {
        "pending",
        "certification_invalid",
        "certification_fail",
        "certification_pass",
    }:
        errors.append("decision value is invalid")

    hashes = report.get("hashes")
    if (
        not isinstance(hashes, Mapping)
        or set(hashes) != HASH_KEYS
        or any(not isinstance(value, str) or not value.startswith("sha256:") for value in hashes.values())
    ):
        errors.append("report hashes are invalid")

    evidence = report.get("evidence")
    if not isinstance(evidence, Mapping) or set(evidence) != EVIDENCE_KEYS:
        errors.append("evidence field population is not exact")
    else:
        expected = {
            "scenario_count": SCENARIO_COUNT,
            "sample_count": SAMPLE_COUNT,
            "family_count": FAMILY_COUNT,
            "unique_coverage_cells": SCENARIO_COUNT,
            "multi_turn_count": 72,
            "one_turn_count": 216,
            "validation_error_count": 0,
            "runtime_exception_count": 0,
            "missing_dimension_count": 0,
            "case_artifact_count": 0,
            "oracle_leak_count": 0,
            "repeat_variance_count": 0,
            "seal_consumed": True,
        }
        for key, value in expected.items():
            if evidence.get(key) != value:
                errors.append(f"evidence gate failed: {key}")

    dimensions = report.get("dimensions")
    if not isinstance(dimensions, Mapping) or set(dimensions) != set(DIMENSIONS):
        errors.append("dimension population is not exact")
    else:
        for dimension in DIMENSIONS:
            if not _count_is_exact(dimensions[dimension], total=SAMPLE_COUNT):
                errors.append(f"dimension count is invalid: {dimension}")
    if not _count_is_exact(report.get("complete"), total=SAMPLE_COUNT):
        errors.append("complete count is invalid")

    families = report.get("families")
    if not isinstance(families, Mapping) or len(families) != FAMILY_COUNT:
        errors.append("family aggregate population is not exact")
    elif any(not _count_is_exact(value, total=FAMILY_TOTAL) for value in families.values()):
        errors.append("family aggregate count is invalid")

    styles = report.get("language_styles")
    if not isinstance(styles, Mapping) or set(styles) != set(LANGUAGE_STYLES):
        errors.append("language aggregate population is not exact")
    elif any(not _count_is_exact(value, total=STYLE_TOTAL) for value in styles.values()):
        errors.append("language aggregate count is invalid")

    actions = report.get("actions")
    if (
        not isinstance(actions, Mapping)
        or len(actions) != 6
        or any(not _count_is_exact(value, total=96) for value in actions.values())
    ):
        errors.append("action aggregate population is invalid")

    failures = report.get("failure_totals")
    if not isinstance(failures, Mapping) or set(failures) != FAILURE_KEYS:
        errors.append("failure total population is not exact")
    elif any(value != 0 for value in failures.values()):
        errors.append("failure totals are non-zero")

    if _contains_case_artifact(report):
        errors.append("case-level artifact detected")
    return tuple(dict.fromkeys(errors))


def product_errors(report: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    dimensions = report["dimensions"]
    for dimension in DIMENSIONS:
        passed = dimensions[dimension]["passed"]
        if dimension in EXACT_DIMENSIONS:
            if passed != SAMPLE_COUNT:
                errors.append(f"exact dimension gate missed: {dimension}")
        elif passed < SEMANTIC_MINIMUM:
            errors.append(f"semantic dimension gate missed: {dimension}")
    if report["complete"]["passed"] < COMPLETE_MINIMUM:
        errors.append("complete gate missed")
    for family, count in report["families"].items():
        if count["passed"] < FAMILY_MINIMUM:
            errors.append(f"family gate missed: {family}")
    for style, count in report["language_styles"].items():
        if count["passed"] < STYLE_MINIMUM:
            errors.append(f"language gate missed: {style}")
    return tuple(errors)


def decide(report: Any) -> str:
    if evidence_errors(report):
        return "certification_invalid"
    if product_errors(report):
        return "certification_fail"
    return "certification_pass"


__all__ = [
    "COMPLETE_MINIMUM",
    "EXACT_DIMENSIONS",
    "FAMILY_MINIMUM",
    "SEMANTIC_MINIMUM",
    "STYLE_MINIMUM",
    "decide",
    "evidence_errors",
    "product_errors",
]
