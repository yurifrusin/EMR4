"""Content-blind tests for the frozen LC4V6 acceptance thresholds."""

from __future__ import annotations

from copy import deepcopy

import pytest

from app.services.bernie.lc4v6_acceptance_rule import decide_certification
from app.services.bernie.lc4v6_content_blind_framework import (
    ACTIONS,
    DIMENSIONS,
    FAILURE_LAYERS,
    BoundHashes,
    ScenarioContract,
    TypedObservation,
    aggregate_observations,
)


def _hashes() -> BoundHashes:
    return BoundHashes(*("sha256:" + str(index) * 64 for index in range(5)))


def _report() -> dict:
    actions = sorted(ACTIONS)
    observations = []
    for index in range(288):
        slices = {
            "family": f"group-{index // 12:03d}",
            "language_form": "opaque",
            "dialogue_form": "multi" if index % 12 < 3 else "one_shot",
            "temporal_relation": "opaque",
            "provenance": "gold",
            "adjudication": "adjudicated",
            "action": actions[index % 6],
        }
        scenario = ScenarioContract(
            f"opaque-{index:03d}",
            f"group-{index // 12:03d}",
            f"cell-{index:03d}",
            actions[index % 6],
            ("opaque",),
            "2026-07-16",
            {},
            slices,
        )
        for repeat in range(2):
            observations.append(
                TypedObservation(
                    scenario.scenario_id,
                    repeat,
                    {name: True for name in DIMENSIONS},
                    True,
                    {name: False for name in FAILURE_LAYERS},
                    slices,
                )
            )
    return aggregate_observations(observations, _hashes())


def test_exact_passing_report_certifies() -> None:
    decision = decide_certification(_report(), _hashes())
    assert decision.decision == "certification_pass"
    assert all(decision.evidence_gates.values())
    assert all(decision.product_gates.values())


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("complete_contract", "passed"), 547),
        (("safety", "passed"), 575),
        (("per_dimension", "intended_action", "passed"), 547),
        (("failure_layers", "interpretation"), 29),
        (("failure_layers", "policy"), 29),
        (("failure_layers", "integration"), 29),
        (("failure_layers", "safety"), 1),
    ],
)
def test_each_product_threshold_fails_without_changing_evidence(
    path: tuple[str, ...], value: int
) -> None:
    report = deepcopy(_report())
    target = report
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    if path[0] in {"complete_contract", "safety", "per_dimension"}:
        counts = target if path[0] != "per_dimension" else report["per_dimension"][path[1]]
        counts["failed"] = 576 - counts["passed"]
    decision = decide_certification(report, _hashes())
    assert decision.decision == "certification_fail"
    assert all(decision.evidence_gates.values())


def test_slice_below_ninety_percent_fails() -> None:
    report = deepcopy(_report())
    row = report["slices"]["family"][0]
    row["passed"] = 21
    row["failed"] = 3
    decision = decide_certification(report, _hashes())
    assert decision.decision == "certification_fail"
    assert decision.worst_slice_rate == 21 / 24


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("sample_count", 575),
        ("evaluation_exception_count", 1),
        ("missing_dimension_count", 1),
        ("case_level_artifact_count", 1),
        ("repeat_variance_count", 1),
    ],
)
def test_evidence_defect_never_becomes_product_failure(field: str, value: int) -> None:
    report = _report()
    report[field] = value
    assert decide_certification(report, _hashes()).decision == "evidence_invalid"


def test_hash_drift_is_evidence_invalid() -> None:
    report = _report()
    report["hashes"]["source"] = "sha256:" + "f" * 64
    assert decide_certification(report, _hashes()).decision == "evidence_invalid"
