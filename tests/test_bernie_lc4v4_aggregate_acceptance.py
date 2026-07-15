"""Aggregate-only checks for the consumed LC4V4 result."""

from __future__ import annotations

import json
from pathlib import Path

from app.services.bernie.lc4v4_acceptance import decide_lc4v4
from app.services.bernie.lc4v4_certification import check_aggregate_report


REPORT_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "bernie-lc4v4-aggregate-report.json"
)


def _report() -> dict:
    return json.loads(REPORT_PATH.read_text(encoding="utf-8"))


def test_consumed_aggregate_is_valid_and_hash_bound() -> None:
    report = _report()
    assert check_aggregate_report(report) == {"valid": True, "errors": []}
    assert report["report_hash"] == (
        "sha256:9fa0cfe19d6e24e19630d415e4a778c89b6381057ae661e4c7d6c53c088d68f5"
    )
    assert report["source_commit"] == "9c005e777d008e03a3ee085382915dfc1dc652c6"


def test_frozen_thresholds_return_certification_fail() -> None:
    decision = decide_lc4v4(_report())
    assert decision["evidence_valid"] is True
    assert decision["decision"] == "certification_fail"
    assert "safety_exact" in decision["failed_conditions"]
    assert "complete_composed_contract" in decision["failed_conditions"]
    assert "slice:worst_slice" in decision["failed_conditions"]


def test_aggregate_preserves_population_coverage_and_determinism() -> None:
    report = _report()
    assert report["total_scenarios"] == 288
    assert report["total_trajectories"] == 72
    assert report["total_samples"] == 576
    assert report["coverage_cells"]["distinct_cell_count"] == 288
    assert report["variance"] == {
        "all_samples_deterministic": True,
        "total_repeats": 2,
        "variant_sample_count": 0,
        "variant_scenario_count": 0,
    }


def test_aggregate_contains_no_case_level_surface() -> None:
    encoded = json.dumps(_report(), sort_keys=True)
    for prohibited in (
        "scenario_id",
        "utterance",
        "source_span",
        "lc4v4_var_",
        "lc4v4_mt_",
        "case_finding",
    ):
        assert prohibited not in encoded
