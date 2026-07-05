"""Build a safe synthetic event summary from historical diary aggregate output.

This dry run intentionally consumes only committed-safe aggregate JSON, such as
the ignored H6 timeline delta payload. It does not read raw diary documents and
does not reconstruct true chronological edits from grouped aggregate signatures.
"""

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
from scripts.historical_diary_timeline_events import (
    NeutralSnapshot,
    summarize_timeline_events,
)


DEFAULT_OUTPUT = Path(
    "local_data/historical-diary-trove/inventory/event_summary_h8.json"
)


def summarize_aggregate_timeline(payload: dict[str, Any]) -> dict[str, Any]:
    validate_historical_diary_output(payload)

    summaries = [
        summarize_timeline_events(
            str(root["root_label"]),
            _snapshots_from_neutral_signature_distribution(root),
        )["roots"][0]
        for root in payload.get("roots", [])
    ]

    output = {
        "classifier": {
            "output_class": "aggregate_neutral_timeline_events",
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
        "event_model": {
            "version": 1,
            "sample_only": True,
            "output_class": "aggregate_neutral_timeline_events",
        },
        "roots": summaries,
    }
    validate_historical_diary_output(output)
    return output


def _snapshots_from_neutral_signature_distribution(root: dict[str, Any]) -> list[NeutralSnapshot]:
    snapshots: list[NeutralSnapshot] = []
    structure_class = _mode_value(root.get("structure_class_distribution"), "unknown_structure")
    char_count = _range_min(root.get("char_count_range"))

    for item in root.get("neutral_signature_distribution", []):
        signature = _parse_neutral_signature(str(item["value"]))
        snapshot = NeutralSnapshot(
            char_count=char_count,
            paragraph_count=int(signature["paragraphs"]),
            non_empty_line_count=int(signature["lines"]),
            table_count=int(signature["tables"]),
            table_cell_count=int(signature["cells"]),
            time_like_token_count=int(signature["times"]),
            date_like_token_count=int(signature["dates"]),
            table_dimension_signature=signature["dims"],
            structure_class=structure_class,
        )
        snapshots.extend([snapshot] * int(item["count"]))

    return snapshots


def _parse_neutral_signature(signature: str) -> dict[str, str]:
    parts: dict[str, str] = {}
    for segment in signature.split(";"):
        key, separator, value = segment.partition("=")
        if not separator:
            raise ValueError(f"invalid neutral signature segment: {segment!r}")
        parts[key] = value

    required = {"tables", "cells", "paragraphs", "lines", "times", "dates", "dims"}
    missing = required.difference(parts)
    if missing:
        raise ValueError(f"neutral signature missing fields: {sorted(missing)}")
    return parts


def _mode_value(distribution: Any, default: str) -> str:
    if not isinstance(distribution, list) or not distribution:
        return default
    return str(max(distribution, key=lambda item: int(item.get("count", 0)))["value"])


def _range_min(range_payload: Any) -> int:
    if not isinstance(range_payload, dict):
        return 0
    return int(range_payload.get("min", 0))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_json", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    output = summarize_aggregate_timeline(load_json(args.input_json))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote safe aggregate event summary: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
