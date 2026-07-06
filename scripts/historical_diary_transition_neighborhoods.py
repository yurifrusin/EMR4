"""Create safe neutral neighborhoods around notable diary transitions."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.historical_diary_event_summary_dry_run import _snapshots_from_ordered_root
from scripts.historical_diary_large_delta_triage import _neutral_counts, _single_range
from scripts.historical_diary_output_safety import (
    load_json,
    validate_historical_diary_output,
)
from scripts.historical_diary_timeline_events import (
    EVENT_LARGE_UNEXPLAINED_DELTA,
    EVENT_TIME_GRID_DELTA,
    classify_transition,
)


DEFAULT_OUTPUT = Path(
    "local_data/historical-diary-trove/inventory/transition_neighborhoods_h14.json"
)
DEFAULT_TARGET_EVENT_CLASSES = {
    EVENT_LARGE_UNEXPLAINED_DELTA,
    EVENT_TIME_GRID_DELTA,
}


def build_transition_neighborhoods(
    payload: dict[str, Any],
    *,
    radius: int = 1,
    target_event_classes: set[str] | None = None,
) -> dict[str, Any]:
    validate_historical_diary_output(payload)
    if radius < 0:
        raise ValueError("radius must be non-negative")

    target_classes = target_event_classes or DEFAULT_TARGET_EVENT_CLASSES
    roots = []

    for root in payload.get("roots", []):
        snapshots = _snapshots_from_ordered_root(root)
        ordered_items = sorted(
            root.get("ordered_neutral_snapshots", []),
            key=lambda snapshot: int(snapshot["sequence_index"]),
        )
        transitions = [
            classify_transition(before_snapshot, after_snapshot)
            for before_snapshot, after_snapshot in zip(snapshots, snapshots[1:])
        ]
        neighborhoods = []

        for center_index, transition in enumerate(transitions):
            if transition.event_class not in target_classes:
                continue

            start_index = max(0, center_index - radius)
            end_index = min(len(transitions) - 1, center_index + radius)
            neighbor_transitions = [
                _transition_record(
                    index,
                    center_index,
                    transitions[index],
                    ordered_items[index],
                    ordered_items[index + 1],
                )
                for index in range(start_index, end_index + 1)
                if index != center_index
            ]
            neighborhoods.append(
                {
                    "center_transition_index": center_index,
                    "event_class": transition.event_class,
                    "center_transition": _transition_record(
                        center_index,
                        center_index,
                        transition,
                        ordered_items[center_index],
                        ordered_items[center_index + 1],
                    ),
                    "neighbor_transitions": neighbor_transitions,
                }
            )

        roots.append(
            {
                "root_label": root["root_label"],
                "snapshot_count": len(snapshots),
                "transition_count": len(transitions),
                "neighborhood_count": len(neighborhoods),
                "transition_neighborhoods": neighborhoods,
            }
        )

    output = {
        "classifier": {
            "output_class": "transition_neighborhoods",
            "version": 1,
            "sample_only": True,
        },
        "privacy": {
            "emits_document_text": False,
            "emits_filenames": False,
            "emits_raw_paths": False,
            "emits_exact_document_timestamps": False,
            "emits_patient_or_staff_labels": False,
        },
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "roots": roots,
    }
    validate_historical_diary_output(output)
    return output


def _transition_record(
    transition_index: int,
    center_index: int,
    transition: Any,
    before_item: dict[str, Any],
    after_item: dict[str, Any],
) -> dict[str, Any]:
    return {
        "transition_index": transition_index,
        "relative_offset": transition_index - center_index,
        "event_class": transition.event_class,
        "before_counts": _neutral_counts(before_item),
        "after_counts": _neutral_counts(after_item),
        "adjacent_neutral_delta_ranges": {
            "char_count_abs_delta_range": _single_range(
                transition.char_count_abs_delta
            ),
            "paragraph_count_abs_delta_range": _single_range(
                transition.paragraph_count_abs_delta
            ),
            "non_empty_line_count_abs_delta_range": _single_range(
                transition.non_empty_line_count_abs_delta
            ),
            "time_like_token_count_abs_delta_range": _single_range(
                transition.time_like_token_count_abs_delta
            ),
            "date_like_token_count_abs_delta_range": _single_range(
                transition.date_like_token_count_abs_delta
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ordered_snapshot_json", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--radius", type=int, default=1)
    args = parser.parse_args()

    output = build_transition_neighborhoods(
        load_json(args.ordered_snapshot_json),
        radius=args.radius,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote safe transition neighborhoods: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
