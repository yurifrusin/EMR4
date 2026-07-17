from __future__ import annotations

import pytest

from app.services.bernie.composed_corpus_evaluator import deterministic_interpret
from app.services.bernie.scale_corpus import (
    DevelopmentOnlyLoader,
    LC4R10_RECONCILIATION_IDS,
)
from app.services.bernie.synthetic_noise_robustness import build_evaluation_scenarios


SCENARIOS = {
    candidate["candidate_id"]: scenario
    for candidate, _seed, scenario in build_evaluation_scenarios()
}


def _interpret(candidate_id: str):
    return deterministic_interpret(SCENARIOS[candidate_id])


@pytest.mark.parametrize(
    ("candidate_id", "expected_action"),
    [
        ("sol_bernie_noise_seed_081_01", "explain_schedule"),
        ("sol_bernie_noise_seed_082_02", "explain_schedule"),
        ("sol_bernie_noise_seed_083_01", "explain_schedule"),
        ("sol_bernie_noise_seed_088_02", "explain_schedule"),
        ("sol_bernie_noise_seed_033_01", "resize"),
        ("sol_bernie_noise_seed_043_02", "resize"),
        ("sol_bernie_noise_seed_065_02", "status_change"),
        ("sol_bernie_noise_seed_075_01", "status_change"),
        ("sol_bernie_noise_seed_002_01", "create"),
        ("sol_bernie_noise_seed_018_02", "move"),
        ("sol_bernie_noise_seed_056_01", "cancel"),
    ],
)
def test_supported_staff_action_surfaces(
    candidate_id: str,
    expected_action: str,
) -> None:
    assert _interpret(candidate_id).intended_action == expected_action


@pytest.mark.parametrize(
    ("candidate_id", "relation", "earliest", "latest"),
    [
        ("sol_bernie_noise_seed_004_01", "not_before", "15:00", None),
        ("sol_bernie_noise_seed_007_02", "not_after", None, "17:00"),
        ("sol_bernie_noise_seed_021_01", "not_before", "15:00", None),
        ("sol_bernie_noise_seed_024_02", "not_after", None, "17:00"),
        ("sol_bernie_noise_seed_029_01", "approximate", "15:00", "15:00"),
        ("sol_bernie_noise_seed_029_02", "approximate", "15:00", "15:00"),
        ("sol_bernie_noise_seed_039_01", "not_after", None, "17:00"),
        ("sol_bernie_noise_seed_052_02", "not_before", "15:00", None),
        ("sol_bernie_noise_seed_070_01", "not_before", "15:00", None),
        ("sol_bernie_noise_seed_072_02", "not_after", None, "17:00"),
    ],
)
def test_supported_staff_temporal_surfaces(
    candidate_id: str,
    relation: str,
    earliest: str | None,
    latest: str | None,
) -> None:
    interpretation = _interpret(candidate_id)
    assert interpretation.temporal_relation == relation
    assert interpretation.normalized_values.get("earliest_time") == earliest
    assert interpretation.normalized_values.get("latest_time") == latest


@pytest.mark.parametrize(
    "candidate_id",
    [
        "sol_bernie_noise_seed_081_01",
        "sol_bernie_noise_seed_065_02",
        "sol_bernie_noise_seed_021_01",
        "sol_bernie_noise_seed_029_01",
    ],
)
def test_parser_does_not_invent_unsurfaced_duration(candidate_id: str) -> None:
    interpretation = _interpret(candidate_id)
    assert "duration_minutes" not in interpretation.normalized_values


def test_resize_rule_repairs_only_supported_ordinary_development_variants() -> None:
    affected_ids = {
        f"lc4_dw1_dev_mt_{group_index:03d}_{variant_index:02d}"
        for group_index in range(33, 49)
        for variant_index in (2, 3)
    }
    corpus = DevelopmentOnlyLoader().load_all()
    scenarios = {
        scenario.scenario_id: scenario
        for group in corpus.groups
        for scenario in group.all_variants
    }
    assert affected_ids.isdisjoint(LC4R10_RECONCILIATION_IDS)
    for scenario_id in affected_ids:
        scenario = scenarios[scenario_id]
        assert scenario.intended_action == "resize"
        assert deterministic_interpret(scenario).intended_action == "resize"
