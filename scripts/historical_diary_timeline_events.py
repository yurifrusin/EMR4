"""Synthetic neutral event model for historical diary timeline deltas."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable


EVENT_NO_STRUCTURAL_CHANGE = "no_structural_change"
EVENT_SMALL_CONTENT_DELTA = "small_content_delta"
EVENT_LAYOUT_SHAPE_CHANGE = "layout_shape_change"
EVENT_TIME_GRID_DELTA = "time_grid_delta"
EVENT_LARGE_UNEXPLAINED_DELTA = "large_unexplained_delta"


@dataclass(frozen=True)
class NeutralSnapshot:
    char_count: int
    paragraph_count: int
    non_empty_line_count: int
    table_count: int
    table_cell_count: int
    time_like_token_count: int
    date_like_token_count: int
    table_dimension_signature: str
    structure_class: str


@dataclass(frozen=True)
class NeutralTransition:
    event_class: str
    char_count_abs_delta: int
    paragraph_count_abs_delta: int
    non_empty_line_count_abs_delta: int
    time_like_token_count_abs_delta: int
    date_like_token_count_abs_delta: int


def classify_transition(previous: NeutralSnapshot, current: NeutralSnapshot) -> NeutralTransition:
    char_delta = abs(current.char_count - previous.char_count)
    paragraph_delta = abs(current.paragraph_count - previous.paragraph_count)
    line_delta = abs(current.non_empty_line_count - previous.non_empty_line_count)
    time_delta = abs(current.time_like_token_count - previous.time_like_token_count)
    date_delta = abs(current.date_like_token_count - previous.date_like_token_count)

    if (
        current.table_count != previous.table_count
        or current.table_cell_count != previous.table_cell_count
        or current.table_dimension_signature != previous.table_dimension_signature
        or current.structure_class != previous.structure_class
    ):
        event_class = EVENT_LAYOUT_SHAPE_CHANGE
    elif char_delta == 0 and paragraph_delta == 0 and line_delta == 0 and time_delta == 0 and date_delta == 0:
        event_class = EVENT_NO_STRUCTURAL_CHANGE
    elif time_delta > 2 or date_delta > 1:
        event_class = EVENT_TIME_GRID_DELTA
    elif char_delta > 500 or paragraph_delta > 20 or line_delta > 20:
        event_class = EVENT_LARGE_UNEXPLAINED_DELTA
    else:
        event_class = EVENT_SMALL_CONTENT_DELTA

    return NeutralTransition(
        event_class=event_class,
        char_count_abs_delta=char_delta,
        paragraph_count_abs_delta=paragraph_delta,
        non_empty_line_count_abs_delta=line_delta,
        time_like_token_count_abs_delta=time_delta,
        date_like_token_count_abs_delta=date_delta,
    )


def summarize_timeline_events(root_label: str, snapshots: Iterable[NeutralSnapshot]) -> dict:
    snapshot_list = list(snapshots)
    transitions = [
        classify_transition(previous, current)
        for previous, current in zip(snapshot_list, snapshot_list[1:])
    ]
    event_counts = Counter(transition.event_class for transition in transitions)

    return {
        "privacy": {
            "emits_document_text": False,
            "emits_filenames": False,
            "emits_raw_paths": False,
            "emits_exact_document_timestamps": False,
            "emits_patient_or_staff_labels": False,
        },
        "event_model": {
            "version": 1,
            "sample_only": True,
            "output_class": "aggregate_neutral_timeline_events",
        },
        "roots": [
            {
                "root_label": root_label,
                "snapshot_count": len(snapshot_list),
                "transition_count": len(transitions),
                "event_class_distribution": [
                    {"value": event_class, "count": count}
                    for event_class, count in sorted(event_counts.items())
                ],
                "adjacent_neutral_delta_ranges": {
                    "char_count_abs_delta_range": _range(
                        transition.char_count_abs_delta for transition in transitions
                    ),
                    "paragraph_count_abs_delta_range": _range(
                        transition.paragraph_count_abs_delta for transition in transitions
                    ),
                    "non_empty_line_count_abs_delta_range": _range(
                        transition.non_empty_line_count_abs_delta for transition in transitions
                    ),
                    "time_like_token_count_abs_delta_range": _range(
                        transition.time_like_token_count_abs_delta for transition in transitions
                    ),
                    "date_like_token_count_abs_delta_range": _range(
                        transition.date_like_token_count_abs_delta for transition in transitions
                    ),
                },
            }
        ],
    }


def _range(values: Iterable[int]) -> dict | None:
    value_list = list(values)
    if not value_list:
        return None
    return {"min": min(value_list), "max": max(value_list)}
