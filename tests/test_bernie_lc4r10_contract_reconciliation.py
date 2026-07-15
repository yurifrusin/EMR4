from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.services.bernie.composed_corpus_evaluator import (
    deterministic_interpret,
    deterministic_replay,
    score_interpretation_replay_pair,
)
from app.services.bernie.scale_corpus import (
    DevelopmentOnlyLoader,
    LC4R10_RECONCILIATION_IDS,
    LC4R10_REPLAY_IDS,
    LC4R10_RESOLVED_CLARIFICATION_IDS,
    ReceptionScenarioSpec,
    generate_development_fixture,
    validate_variant,
)
from app.services.bernie.scaled_evaluator import (
    generate_scaled_evaluation_report,
)
from scripts.bernie_lc4r10_contract_reconciliation import (
    EXPECTED_SEMANTIC_COUNTS,
    REPORT_PATH,
    build_report,
    generator_is_reproducible,
)


@pytest.fixture(scope="module")
def corpus():
    return DevelopmentOnlyLoader().load_all()


@pytest.fixture(scope="module")
def scenarios(corpus):
    return {
        scenario.scenario_id: scenario
        for group in corpus.groups
        for scenario in group.all_variants
    }


def test_frozen_selection_counts_and_disjointness():
    assert len(LC4R10_RESOLVED_CLARIFICATION_IDS) == 53
    assert len(LC4R10_REPLAY_IDS) == 40
    assert len(LC4R10_RECONCILIATION_IDS) == 93
    assert not LC4R10_RESOLVED_CLARIFICATION_IDS & LC4R10_REPLAY_IDS


def test_expected_outcome_is_required_but_nullable(scenarios):
    payload = scenarios["lc4_dw1_dev_mt_001_03"].model_dump(mode="json")
    assert payload["expected_outcome_kind"] is None
    ReceptionScenarioSpec.model_validate(payload)
    missing = copy.deepcopy(payload)
    del missing["expected_outcome_kind"]
    with pytest.raises(ValidationError):
        ReceptionScenarioSpec.model_validate(missing)


def test_empty_non_null_outcome_is_rejected(scenarios):
    payload = scenarios["lc4_dw1_dev_mt_001_03"].model_dump(mode="json")
    payload["expected_outcome_kind"] = ""
    with pytest.raises(ValidationError):
        ReceptionScenarioSpec.model_validate(payload)


@pytest.mark.parametrize(
    ("scenario_id", "relation", "earliest", "latest", "duration", "duration_sem"),
    [
        ("lc4_dw1_dev_mt_001_01", "approximate", "14:30", "15:30", 15, "exact"),
        ("lc4_dw1_dev_mt_017_01", "exact", "16:00", "16:00", None, "omitted"),
        ("lc4_dw1_dev_mt_033_01", "exact", "15:00", "15:00", 30, "exact"),
        ("lc4_dw1_dev_mt_049_01", "exact", "15:00", "15:00", None, "omitted"),
    ],
)
def test_resolved_dialogue_templates(
    scenarios, scenario_id, relation, earliest, latest, duration, duration_sem
):
    scenario = scenarios[scenario_id]
    assert scenario.temporal_relation == relation
    assert scenario.earliest_time == earliest
    assert scenario.latest_time == latest
    assert scenario.duration_minutes == duration
    assert scenario.duration_semantics == duration_sem
    assert scenario.patient_semantics == "exact"
    assert scenario.practitioner_semantics == "exact"
    assert scenario.entity_state == "exact"
    assert scenario.expected_clarification is None
    assert scenario.clarification_choices == []


def test_resolved_dialogue_source_spans_are_lossless(scenarios):
    for scenario_id in LC4R10_RESOLVED_CLARIFICATION_IDS:
        scenario = scenarios[scenario_id]
        for spans in scenario.source_spans.values():
            for span in spans:
                utterance = scenario.dialogue_turns[span.turn_index]["utterance"]
                assert utterance[span.start : span.end] == span.text


def test_unselected_mt01_contract_is_unchanged(scenarios):
    scenario = scenarios["lc4_dw1_dev_mt_002_01"]
    assert scenario.expected_clarification == "Please clarify: which time works?"
    assert scenario.clarification_choices == ["10am", "2pm", "3pm", "4pm"]
    assert scenario.expected_tool_sequence == ["request_clarification"]


def test_group_override_is_exactly_allowlisted(corpus, scenarios):
    selected = scenarios["lc4_dw1_dev_mt_017_01"]
    group = next(group for group in corpus.groups if group.spec.group_index == 17)
    assert validate_variant(selected, group.spec) == []
    unselected = scenarios["lc4_dw1_dev_mt_020_01"]
    group = next(group for group in corpus.groups if group.spec.group_index == 20)
    assert validate_variant(unselected, group.spec) == []


def test_reversal_is_explicit_no_outcome(scenarios):
    scenario = scenarios["lc4_dw1_dev_mt_001_03"]
    assert scenario.expected_outcome_kind is None
    assert scenario.expected_tool_sequence == ["search_patients"]
    assert scenario.expected_appointment_deltas == []
    assert scenario.expected_audit_deltas == []
    interpretation = deterministic_interpret(scenario)
    assert interpretation.action_negated is True
    replay = deterministic_replay(scenario, interpretation)
    assert replay.downstream_outcome is None
    assert replay.appointment_deltas == ()
    assert replay.audit_deltas == ()


def test_corrected_overlap_uses_candidate_selection(scenarios):
    scenario = scenarios["lc4_dw1_dev_mt_003_02"]
    assert scenario.expected_outcome_kind == "candidate_selection_required"
    assert scenario.expected_tool_sequence == [
        "search_patients", "find_slots", "create_booking"
    ]
    assert scenario.expected_appointment_deltas == []
    assert scenario.expected_audit_deltas == []


def test_null_outcomes_are_delta_free(scenarios):
    selected = [scenarios[scenario_id] for scenario_id in LC4R10_RECONCILIATION_IDS]
    null_outcomes = [s for s in selected if s.expected_outcome_kind is None]
    assert len(null_outcomes) == 56
    assert all(not s.expected_appointment_deltas for s in null_outcomes)
    assert all(not s.expected_audit_deltas for s in null_outcomes)


def test_all_93_reconciled_contracts_pass(scenarios):
    for scenario_id in LC4R10_RECONCILIATION_IDS:
        scenario = scenarios[scenario_id]
        interpretation = deterministic_interpret(scenario)
        replay = deterministic_replay(scenario, interpretation)
        result = score_interpretation_replay_pair(
            scenario, interpretation, replay
        )
        assert result.all_passed, scenario_id


def test_create_state_policy_preserves_valid_and_fail_closed_cases(scenarios):
    valid = scenarios["lc4_dw1_dev_var_004_01"]
    terminal = scenarios["lc4_dw1_dev_var_005_01"]
    stale = scenarios["lc4_dw1_dev_var_006_01"]
    concurrent = scenarios["lc4_dw1_dev_var_007_01"]
    for scenario in (valid, terminal):
        replay = deterministic_replay(scenario, deterministic_interpret(scenario))
        assert replay.downstream_outcome == "appointment_created"
    for scenario in (stale, concurrent):
        replay = deterministic_replay(scenario, deterministic_interpret(scenario))
        assert replay.downstream_outcome is None
        assert replay.appointment_deltas == ()


def test_scaled_repeat_preserves_negation_and_safety():
    report = generate_scaled_evaluation_report()
    assert report["per_dimension"]["safety"] == {
        "passed": 2304, "failed": 0, "total": 2304
    }


def test_semantic_counts_and_variance():
    report = generate_scaled_evaluation_report()
    observed = {
        key: value["passed"] // 2
        for key, value in report["per_dimension"]["semantic_fields"].items()
    }
    assert observed == EXPECTED_SEMANTIC_COUNTS
    assert report["variance"]["variant_sample_count"] == 0
    assert report["variance"]["all_samples_deterministic"] is True


def test_report_is_recomputed_and_committed():
    committed = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    assert build_report() == committed
    assert committed["all_assertions_passed"] is True
    assert committed["corrected_contract_results"]["dimension_pass_counts"][
        "all_passed"
    ] == 93


def test_generator_is_byte_reproducible():
    assert generator_is_reproducible()


def test_generated_fixture_filename_set(tmp_path: Path):
    generate_development_fixture(tmp_path)
    assert len(list(tmp_path.glob("lc4_dw1_dev_group_*.json"))) == 96
    assert (tmp_path / "lc4_development_manifest.json").is_file()
