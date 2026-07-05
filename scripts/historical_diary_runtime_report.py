"""Create a safe runtime report for a historical diary neutral probe."""

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
    "local_data/historical-diary-trove/inventory/runtime_report_h11.json"
)


def build_runtime_report(payload: dict[str, Any], elapsed_seconds: float, output_byte_count: int) -> dict[str, Any]:
    validate_historical_diary_output(payload)
    roots = payload.get("roots", [])

    output = {
        "classifier": {
            "output_class": "runtime_report",
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
        "runtime_report": {
            "version": 1,
            "sample_only": True,
            "output_class": "runtime_report",
            "elapsed_seconds": round(float(elapsed_seconds), 3),
            "output_byte_count": int(output_byte_count),
            "root_count": len(roots),
            "total_sampled_count": sum(int(root.get("sampled_count", 0)) for root in roots),
            "total_opened_count": sum(int(root.get("opened_count", 0)) for root in roots),
            "total_error_count": sum(int(root.get("error_count", 0)) for root in roots),
        },
        "roots": [
            {
                "root_label": root["root_label"],
                "dense_candidate_count": int(root.get("dense_candidate_count", 0)),
                "sampled_count": int(root.get("sampled_count", 0)),
                "opened_count": int(root.get("opened_count", 0)),
                "error_count": int(root.get("error_count", 0)),
            }
            for root in roots
        ],
    }
    validate_historical_diary_output(output)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("probe_json", type=Path)
    parser.add_argument("--elapsed-seconds", type=float, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    output = build_runtime_report(
        load_json(args.probe_json),
        elapsed_seconds=args.elapsed_seconds,
        output_byte_count=args.probe_json.stat().st_size,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote safe runtime report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
