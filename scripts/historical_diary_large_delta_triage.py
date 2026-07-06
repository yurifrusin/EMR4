"""Create a safe neutral triage report for large historical diary deltas."""

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
from scripts.historical_diary_output_safety import (
    load_json,
    validate_historical_diary_output,
)
from scripts.historical_diary_timeline_events import (
    EVENT_LARGE_UNEXPLAINED_DELTA,
    classify_transition,
)


DEFAULT_OUTPUT = Path(
    "local_data/historical-diary-trove/inventory/large_delta_triage_h12.json"
)


def build_large_delta_triage(payload: dict[str, Any]) -> dict[str, Any]:
    validate_historical_diary_output(payload)

    roots = []
    for root in payload.get("roots", []):
        snapshots = _snapshots_from_ordered_root(root)
        ordered_items = sorted(
            root.get("ordered_neutral_snapshots", []),
            key=lambda snapshot: int(snapshot["sequence_index"]),
        )
        triage_items = []

        for transition_index, (before_snapshot, after_snapshot) in enumerate(
            zip(snapshots, snapshots[1:])
        ):
            transition = classify_transition(before_snapshot, after_snapshot)
            if transition.event_class != EVENT_LARGE_UNEXPLAINED_DELTA:
                continue
            before_item = ordered_items[transition_index]
            after_item = ordered_items[transition_index + 1]
            triage_items.append(
                {
                    "transition_index": transition_index,
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
            )

        roots.append(
            {
                "root_label": root["root_label"],
                "snapshot_count": len(snapshots),
                "transition_count": max(len(snapshots) - 1, 0),
                "triaged_transition_count": len(triage_items),
                "large_delta_triage": triage_items,
            }
        )

    output = {
        "classifier": {
            "output_class": "large_delta_triage",
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


def _neutral_counts(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "sequence_index": int(snapshot["sequence_index"]),
        "char_count": int(snapshot["char_count"]),
        "paragraph_count": int(snapshot["paragraph_count"]),
        "non_empty_line_count": int(snapshot["non_empty_line_count"]),
        "table_count": int(snapshot["table_count"]),
        "table_cell_count": int(snapshot["table_cell_count"]),
        "time_like_token_count": int(snapshot["time_like_token_count"]),
        "date_like_token_count": int(snapshot["date_like_token_count"]),
        "table_dimension_signature": str(snapshot["table_dimension_signature"]),
        "structure_class": str(snapshot["structure_class"]),
    }


def _single_range(value: int) -> dict[str, int]:
    return {"min": value, "max": value}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ordered_snapshot_json", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    output = build_large_delta_triage(load_json(args.ordered_snapshot_json))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote safe large-delta triage: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
