"""Build a safe cross-pilot trend table from neutral event summaries."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.historical_diary_output_safety import (
    load_json,
    validate_historical_diary_output,
)


DEFAULT_OUTPUT = Path(
    "local_data/historical-diary-trove/inventory/cross_pilot_event_trends_h17.json"
)
NOTABLE_EVENT_CLASSES = ("large_unexplained_delta", "time_grid_delta")


def build_cross_pilot_event_trends(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    roots_by_label: dict[str, dict[str, Any]] = {}

    for summary in summaries:
        validate_historical_diary_output(summary)
        for root in summary.get("roots", []):
            label = root["root_label"]
            if label in roots_by_label:
                raise ValueError(f"duplicate root_label in event summaries: {label}")
            roots_by_label[label] = root

    roots = [_summarize_root(root) for _, root in sorted(roots_by_label.items())]
    output = {
        "classifier": {
            "output_class": "cross_pilot_event_trends",
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
        "summary_comparison": {
            "version": 1,
            "sample_only": True,
            "output_class": "cross_pilot_event_trends",
            "root_count": len(roots),
            "total_sampled_count": sum(int(root["snapshot_count"]) for root in roots),
        },
        "roots": roots,
    }
    validate_historical_diary_output(output)
    return output


def _summarize_root(root: dict[str, Any]) -> dict[str, Any]:
    event_counts = {
        item["value"]: int(item["count"])
        for item in root.get("event_class_distribution", [])
    }
    return {
        "root_label": root["root_label"],
        "snapshot_count": int(root["snapshot_count"]),
        "transition_count": int(root["transition_count"]),
        "event_class_distribution": [
            {"value": value, "count": event_counts[value]}
            for value in sorted(event_counts)
        ],
        "large_delta_triage": [
            {"event_class": event_class, "count": event_counts.get(event_class, 0)}
            for event_class in NOTABLE_EVENT_CLASSES
        ],
        "adjacent_neutral_delta_ranges": root.get("adjacent_neutral_delta_ranges", {}),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("event_summary_json", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    output = build_cross_pilot_event_trends(
        [load_json(event_summary_json) for event_summary_json in args.event_summary_json]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote safe cross-pilot event trends: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
