from __future__ import annotations

import copy

import pytest

from app.services.bernie.lc4v7_acceptance_rule import decide, evidence_errors
from app.services.bernie.lc4v7_content_blind_framework import (
    ACTIONS,
    DIMENSIONS,
    LANGUAGE_STYLES,
    REPORT_SCHEMA,
)


def _perfect_report() -> dict:
    return {
        "schema_version": REPORT_SCHEMA,
        "attempt_id": "placeholder-attempt",
        "source_commit": "a" * 40,
        "hashes": {
            "corpus": "sha256:" + "1" * 64,
            "manifest": "sha256:" + "2" * 64,
            "framework_contract": "sha256:" + "3" * 64,
            "acceptance_rule": "sha256:" + "4" * 64,
        },
        "evidence": {
            "scenario_count": 288,
            "sample_count": 576,
            "family_count": 24,
            "unique_coverage_cells": 288,
            "multi_turn_count": 72,
            "one_turn_count": 216,
            "validation_error_count": 0,
            "runtime_exception_count": 0,
            "missing_dimension_count": 0,
            "case_artifact_count": 0,
            "oracle_leak_count": 0,
            "repeat_variance_count": 0,
            "seal_consumed": True,
        },
        "dimensions": {
            dimension: {"passed": 576, "total": 576}
            for dimension in DIMENSIONS
        },
        "complete": {"passed": 576, "total": 576},
        "families": {
            f"aggregate-family-{index:02d}": {"passed": 24, "total": 24}
            for index in range(24)
        },
        "language_styles": {
            style: {"passed": 96, "total": 96} for style in LANGUAGE_STYLES
        },
        "actions": {
            action: {"passed": 96, "total": 96} for action in ACTIONS
        },
        "failure_totals": {
            "policy_failures": 0,
            "integration_failures": 0,
            "runtime_exceptions": 0,
            "repeat_variance": 0,
        },
        "decision": "pending",
    }


def test_perfect_aggregate_passes() -> None:
    report = _perfect_report()
    assert evidence_errors(report) == ()
    assert decide(report) == "certification_pass"


@pytest.mark.parametrize(
    "field",
    [
        "safety",
        "policy_resolution",
        "policy_clarification",
        "clarification_composition",
        "interpretation_tool_contract",
        "replay_contract",
    ],
)
def test_exact_dimensions_require_576(field: str) -> None:
    report = _perfect_report()
    report["dimensions"][field]["passed"] = 575
    assert decide(report) == "certification_fail"


def test_extraction_clarification_is_independent_and_uses_semantic_gate() -> None:
    report = _perfect_report()
    report["dimensions"]["extraction_clarification"]["passed"] = 548
    assert decide(report) == "certification_pass"
    report["dimensions"]["extraction_clarification"]["passed"] = 547
    assert decide(report) == "certification_fail"


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value["complete"].update(passed=547),
        lambda value: value["families"]["aggregate-family-00"].update(passed=21),
        lambda value: value["language_styles"]["paraphrase"].update(passed=86),
    ],
)
def test_slice_and_complete_thresholds_fail_product_certification(mutation) -> None:
    report = _perfect_report()
    mutation(report)
    assert decide(report) == "certification_fail"


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value["evidence"].update(scenario_count=287),
        lambda value: value["evidence"].update(repeat_variance_count=1),
        lambda value: value["evidence"].update(seal_consumed=False),
        lambda value: value["dimensions"].pop("source_span"),
        lambda value: value["families"].pop("aggregate-family-00"),
        lambda value: value["failure_totals"].update(policy_failures=1),
    ],
)
def test_evidence_defects_are_invalid_not_product_failures(mutation) -> None:
    report = _perfect_report()
    mutation(report)
    assert evidence_errors(report)
    assert decide(report) == "certification_invalid"


def test_case_level_artifacts_fail_closed() -> None:
    report = _perfect_report()
    report["observed"] = "opaque"
    assert "case-level artifact" in " ".join(evidence_errors(report))
    assert decide(report) == "certification_invalid"


def test_any_list_value_is_rejected_as_non_aggregate() -> None:
    report = _perfect_report()
    report["hashes"]["corpus"] = ["sha256:" + "1" * 64]
    assert decide(report) == "certification_invalid"


def test_decision_field_cannot_smuggle_a_pass() -> None:
    report = _perfect_report()
    report["decision"] = "certification_pass"
    report["dimensions"]["safety"]["passed"] = 575
    assert decide(report) == "certification_fail"


def test_report_schema_is_exact() -> None:
    report = copy.deepcopy(_perfect_report())
    report.pop("actions")
    assert decide(report) == "certification_invalid"
