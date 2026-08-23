import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from orchestration_harness import historical_diary_local_measured_privacy_probe as probe
from tests.test_raisa_local_only_bounded_historical_diary_snapshot_measured_privacy_probe import (
    _fixed_keys,
    synthetic_extraction,
)


PLAN = Path(
    "docs/raisa-local-only-historical-diary-document-story-time-coordinate-recovery-rehearsal-plan.md"
)
THREAT = Path(
    "docs/security/raisa-local-only-historical-diary-document-story-time-coordinate-recovery-rehearsal-threat-model-delta.md"
)
GATE = Path(
    "orchestration/continuity/raisa-local-only-historical-diary-structural-time-axis-recovery-rehearsal/historical-derived-scenario-first-use-gate.json"
)
EXTRACTOR = Path("scripts/historical_diary_local_measured_privacy_probe.ps1")


def _coordinate(*, page: int = 1, vertical: int = 100):
    return probe.PrivateSegmentCoordinate(
        segment_ordinal=0,
        coordinate_available=True,
        page_ordinal=page,
        vertical_quarter_points=vertical,
    )


def _anchor(minute: int, *, page: int = 1, vertical: int = 100):
    return probe.PrivateStoryTimeAnchor(
        time_minute=minute,
        page_ordinal=page,
        vertical_quarter_points=vertical,
    )


def test_plan_and_threat_freeze_synthetic_first_coordinate_boundary():
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")

    assert "2026-08-24-story-coordinate-v1" in plan
    assert "same adjusted page" in plan
    assert "16 quarter-points (4 points)" in plan
    assert "main-story raw paragraph text must never cross" in plan
    assert "one fresh terminal permits one content run only" in threat.casefold()


def test_private_coordinate_schema_requires_paired_values_and_sequential_ordinals():
    with pytest.raises(ValidationError, match="segment_coordinate_pair_invalid"):
        probe.PrivateSegmentCoordinate(
            segment_ordinal=0,
            coordinate_available=True,
            page_ordinal=1,
            vertical_quarter_points=None,
        )

    source = synthetic_extraction()
    payload = source.model_dump(mode="json")
    payload["snapshots"][0]["cells"][0]["segment_coordinates"][1][
        "segment_ordinal"
    ] = 7
    with pytest.raises(ValidationError, match="segment_coordinate_sequence_invalid"):
        probe.PrivateExtraction.model_validate(payload)


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        ("00:00", 0),
        ("9.15", 555),
        ("12:00 am", 0),
        ("12:00 PM", 720),
        ("1:05pm", 785),
        ("13:00 pm", None),
        ("booking 09:00", None),
        ("24:00", None),
    ],
)
def test_time_parser_is_complete_token_and_am_pm_exact(token, expected):
    assert probe._time_minute(token) == expected


def test_mapper_accepts_zero_boundary_and_identical_duplicates():
    assert probe._story_coordinate_mapping(_coordinate(), (_anchor(540),)) == (
        540,
        "explicit_story_same_page_coordinate",
        "mapped_zero_distance",
    )
    assert probe._story_coordinate_mapping(
        _coordinate(vertical=116), (_anchor(540), _anchor(540))
    ) == (
        540,
        "explicit_story_same_page_coordinate",
        "mapped_within_four_points",
    )


def test_mapper_rejects_over_distance_cross_page_and_different_time_tie():
    assert probe._story_coordinate_mapping(
        _coordinate(vertical=117), (_anchor(540),)
    ) == (None, "unmapped", "nearest_anchor_over_distance")
    assert probe._story_coordinate_mapping(
        _coordinate(page=2), (_anchor(540, page=1),)
    ) == (None, "unmapped", "same_page_anchor_unavailable")
    assert probe._story_coordinate_mapping(
        _coordinate(vertical=100),
        (_anchor(540, vertical=96), _anchor(555, vertical=104)),
    ) == (None, "unmapped", "different_time_nearest_tie")


def test_mapper_accepts_same_minute_tie_but_never_unavailable_coordinate():
    assert probe._story_coordinate_mapping(
        _coordinate(vertical=100),
        (_anchor(540, vertical=96), _anchor(540, vertical=104)),
    ) == (
        540,
        "explicit_story_same_page_coordinate",
        "mapped_within_one_point",
    )
    unavailable = probe.PrivateSegmentCoordinate(
        segment_ordinal=0,
        coordinate_available=False,
        page_ordinal=None,
        vertical_quarter_points=None,
    )
    assert probe._story_coordinate_mapping(unavailable, (_anchor(540),)) == (
        None,
        "unmapped",
        "coordinate_unavailable",
    )


def test_projection_and_public_reading_never_emit_coordinates_or_distances(monkeypatch):
    _fixed_keys(monkeypatch)
    projection, reading = probe.project_and_measure(synthetic_extraction())
    private = projection.model_dump(mode="json")
    rendered = json.dumps(private, sort_keys=True)

    assert "page_ordinal" not in rendered
    assert "vertical_quarter_points" not in rendered
    assert reading["privacy"]["page_coordinate_or_distance_emitted"] is False
    assert reading["utility"]["mapping_outcome_counts"] == {
        "mapped_zero_distance": 7
    }


def test_extractor_keeps_story_text_local_and_emits_only_typed_anchor_coordinates():
    source = EXTRACTOR.read_text(encoding="utf-8")

    assert "$document.StoryRanges.Item(1)" in source
    assert "$paragraphRange.Information(12)" in source
    assert "$Range.Information(1)" in source
    assert "$Range.Information(6)" in source
    assert "time_minute = [int]$timeMinute" in source
    assert "story_text =" not in source.casefold()
    assert "story_time_anchors =" in source


def test_first_use_gate_exists_now_but_stays_closed_after_measurement():
    gate = json.loads(GATE.read_text(encoding="utf-8"))

    assert gate["status"] == "closed_pending_candidate_specific_evaluation"
    assert gate["authority"]["opened_by_time_axis_success"] is False
    assert gate["authority"]["provider_model_or_runtime_use"] is False
    assert "wholly_authored_synthetic_tests" in gate["does_not_apply_to"]
