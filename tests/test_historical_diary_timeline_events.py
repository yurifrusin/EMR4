from scripts.historical_diary_output_safety import validate_historical_diary_output
from scripts.historical_diary_timeline_events import (
    EVENT_LARGE_UNEXPLAINED_DELTA,
    EVENT_LAYOUT_SHAPE_CHANGE,
    EVENT_NO_STRUCTURAL_CHANGE,
    EVENT_SMALL_CONTENT_DELTA,
    EVENT_TIME_GRID_DELTA,
    NeutralSnapshot,
    classify_transition,
    summarize_timeline_events,
)


def snapshot(**overrides):
    values = {
        "char_count": 3200,
        "paragraph_count": 230,
        "non_empty_line_count": 160,
        "table_count": 2,
        "table_cell_count": 14,
        "time_like_token_count": 78,
        "date_like_token_count": 13,
        "table_dimension_signature": "1x11+1x3",
        "structure_class": "strong_diary_grid",
    }
    values.update(overrides)
    return NeutralSnapshot(**values)


def test_classifies_no_structural_change():
    transition = classify_transition(snapshot(), snapshot())

    assert transition.event_class == EVENT_NO_STRUCTURAL_CHANGE


def test_classifies_small_content_delta():
    transition = classify_transition(
        snapshot(),
        snapshot(char_count=3260, paragraph_count=232, non_empty_line_count=161),
    )

    assert transition.event_class == EVENT_SMALL_CONTENT_DELTA


def test_classifies_layout_shape_change():
    transition = classify_transition(
        snapshot(),
        snapshot(table_cell_count=15, table_dimension_signature="1x12+1x3"),
    )

    assert transition.event_class == EVENT_LAYOUT_SHAPE_CHANGE


def test_classifies_time_grid_delta_before_large_delta():
    transition = classify_transition(
        snapshot(),
        snapshot(char_count=3600, time_like_token_count=83),
    )

    assert transition.event_class == EVENT_TIME_GRID_DELTA


def test_classifies_large_unexplained_delta():
    transition = classify_transition(
        snapshot(),
        snapshot(char_count=4100, paragraph_count=260, non_empty_line_count=190),
    )

    assert transition.event_class == EVENT_LARGE_UNEXPLAINED_DELTA


def test_summarizes_timeline_events_as_validator_safe_payload():
    payload = summarize_timeline_events(
        "synthetic_pilot",
        [
            snapshot(),
            snapshot(),
            snapshot(char_count=3260, paragraph_count=232),
            snapshot(table_cell_count=15, table_dimension_signature="1x12+1x3"),
        ],
    )

    validate_historical_diary_output(payload)
    root = payload["roots"][0]

    assert root["snapshot_count"] == 4
    assert root["transition_count"] == 3
    assert root["event_class_distribution"] == [
        {"value": EVENT_LAYOUT_SHAPE_CHANGE, "count": 1},
        {"value": EVENT_NO_STRUCTURAL_CHANGE, "count": 1},
        {"value": EVENT_SMALL_CONTENT_DELTA, "count": 1},
    ]
    assert root["adjacent_neutral_delta_ranges"]["char_count_abs_delta_range"] == {
        "min": 0,
        "max": 60,
    }
