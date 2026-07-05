"""Compare two safe historical diary neutral event summaries."""

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
    "local_data/historical-diary-trove/inventory/event_summary_compare_h10.json"
)


def compare_event_summaries(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    validate_historical_diary_output(baseline)
    validate_historical_diary_output(candidate)

    baseline_roots = {root["root_label"]: root for root in baseline.get("roots", [])}
    candidate_roots = {root["root_label"]: root for root in candidate.get("roots", [])}
    shared_labels = sorted(set(baseline_roots).intersection(candidate_roots))

    roots = []
    for label in shared_labels:
        baseline_root = baseline_roots[label]
        candidate_root = candidate_roots[label]
        roots.append(
            {
                "root_label": label,
                "snapshot_count_delta": int(candidate_root["snapshot_count"])
                - int(baseline_root["snapshot_count"]),
                "transition_count_delta": int(candidate_root["transition_count"])
                - int(baseline_root["transition_count"]),
                "comparison": _compare_distributions(
                    baseline_root.get("event_class_distribution", []),
                    candidate_root.get("event_class_distribution", []),
                ),
            }
        )

    output = {
        "classifier": {
            "output_class": "summary_comparison",
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
            "output_class": "summary_comparison",
            "root_match_count": len(shared_labels),
        },
        "roots": roots,
    }
    validate_historical_diary_output(output)
    return output


def _compare_distributions(baseline: list[dict[str, Any]], candidate: list[dict[str, Any]]) -> list[dict[str, Any]]:
    baseline_counts = {item["value"]: int(item["count"]) for item in baseline}
    candidate_counts = {item["value"]: int(item["count"]) for item in candidate}
    values = sorted(set(baseline_counts).union(candidate_counts))
    return [
        {
            "value": value,
            "count": candidate_counts.get(value, 0) - baseline_counts.get(value, 0),
        }
        for value in values
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline_json", type=Path)
    parser.add_argument("candidate_json", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    output = compare_event_summaries(load_json(args.baseline_json), load_json(args.candidate_json))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote safe event summary comparison: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
