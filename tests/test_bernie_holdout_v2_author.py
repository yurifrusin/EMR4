"""Pre-consumption checks for the protected Sol-authored v2 blueprint."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.services.bernie.holdout_v2_contract import (
    PRODUCTION_PROFILE,
    build_manifest,
    verify_manifest,
)
from scripts.bernie_holdout_v2_author import (
    BLUEPRINTS,
    build_groups,
    write_groups,
)


def test_exact_production_shape_and_unique_dialogues() -> None:
    groups = build_groups()
    assert len(groups) == 24
    scenarios = [scenario for group in groups for scenario in group.variants]
    assert len(scenarios) == 288
    assert len({scenario.scenario_id for scenario in scenarios}) == 288
    assert sum(len(scenario.dialogue_turns) > 1 for scenario in scenarios) == 72
    for group in groups:
        dialogue_fingerprints = {
            tuple(turn["utterance"] for turn in scenario.dialogue_turns)
            for scenario in group.variants
        }
        assert len(dialogue_fingerprints) == 12


def test_frozen_coverage_blueprint() -> None:
    assert {item.action for item in BLUEPRINTS} == {
        "create",
        "move",
        "resize",
        "cancel",
    }
    assert {item.temporal_relation for item in BLUEPRINTS} == {
        "exact",
        "not_before",
        "not_after",
        "interval",
        "approximate",
    }
    assert {item.diary_state for item in BLUEPRINTS} == {
        "empty",
        "exact_duplicate",
        "overlap",
        "same_day_distinct",
        "terminal",
        "stale",
        "concurrent",
        "roster_absent",
        "break",
        "no_slots",
        "elapsed_window",
    }
    assert {item.entity_state for item in BLUEPRINTS} == {
        "exact",
        "omitted",
        "ambiguous",
        "corrected",
        "negated",
        "mismatched",
    }


def test_language_and_dialogue_forms_cover_contract() -> None:
    scenarios = [scenario for group in build_groups() for scenario in group.variants]
    assert {scenario.language_form for scenario in scenarios} == {
        "plain",
        "paraphrase",
        "filler",
        "abbreviation",
        "typo",
        "speech_like",
        "punctuation_variant",
        "adversarial",
    }
    assert {scenario.dialogue_form for scenario in scenarios} == {
        "one_shot",
        "correction",
        "clarification",
        "repeated",
    }


def test_every_case_is_synthetic_gold_with_independent_evidence() -> None:
    for group in build_groups():
        for scenario in group.variants:
            assert scenario.provenance == "gold"
            assert scenario.adjudication == "adjudicated"
            assert scenario.initial_diary_state["synthetic"] is True
            assert scenario.source_spans
            assert "expected_outcome_kind" in scenario.model_fields_set
            assert "confirm_appointment" in scenario.forbidden_tool_calls


def test_authoring_is_deterministic() -> None:
    first = [group.model_dump(mode="json") for group in build_groups()]
    second = [group.model_dump(mode="json") for group in build_groups()]
    assert first == second


def test_written_corpus_builds_exact_manifest(tmp_path: Path) -> None:
    output = tmp_path / "fresh-v2"
    write_groups(output)
    manifest = build_manifest(output)
    assert manifest.group_count == PRODUCTION_PROFILE.group_count
    assert manifest.variant_count == PRODUCTION_PROFILE.variant_count
    assert manifest.multi_turn_count == PRODUCTION_PROFILE.multi_turn_count
    assert len(verify_manifest(manifest, output)) == 24


def test_author_refuses_existing_output(tmp_path: Path) -> None:
    output = tmp_path / "fresh-v2"
    output.mkdir()
    with pytest.raises(ValueError, match="overwrite"):
        write_groups(output)
