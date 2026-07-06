"""Summarise Bernie interpretation harness fixtures without provider calls."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.services.bernie.interpretation_harness import (
    INTERPRETATION_HARNESS_SCHEMA_VERSION,
)

REPORT_SCHEMA_VERSION = "bernie.interpretation_harness_report.v1"
DEFAULT_FIXTURE_DIR = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "bernie_interpretation_harness"
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_harness_report(fixture_dir: Path = DEFAULT_FIXTURE_DIR) -> dict[str, Any]:
    """Build a safe aggregate report over authored synthetic harness fixtures."""

    fixture_paths = sorted(fixture_dir.glob("*.json"))
    case_fixture_paths: list[Path] = []
    contract_count = 0
    dispatch_counts: Counter[str] = Counter()
    frame_kind_counts: Counter[str] = Counter()
    fixture_case_counts: dict[str, int] = {}
    contract_dispatches: list[str] = []

    for path in fixture_paths:
        payload = _load_json(path)
        if payload.get("schema_version") != INTERPRETATION_HARNESS_SCHEMA_VERSION:
            raise ValueError(f"Unexpected fixture schema_version in {path.name}")
        if payload.get("source") != "authored_synthetic":
            raise ValueError(f"Unexpected fixture source in {path.name}")

        cases = payload.get("cases")
        contracts = payload.get("contracts")
        if cases is not None:
            case_fixture_paths.append(path)
            fixture_case_counts[path.name] = len(cases)
            for case in cases:
                dispatch_counts[case["expected_dispatch"]] += 1
                frame_kind_counts[case["expected_frame_kind"]] += 1
        if contracts is not None:
            contract_count += len(contracts)
            contract_dispatches.extend(contract["dispatch"] for contract in contracts)

    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "source_schema_version": INTERPRETATION_HARNESS_SCHEMA_VERSION,
        "source": "authored_synthetic_aggregate",
        "case_fixture_count": len(case_fixture_paths),
        "case_count": sum(fixture_case_counts.values()),
        "contract_count": contract_count,
        "dispatch_counts": dict(sorted(dispatch_counts.items())),
        "frame_kind_counts": dict(sorted(frame_kind_counts.items())),
        "fixture_case_counts": dict(sorted(fixture_case_counts.items())),
        "contract_dispatches": sorted(contract_dispatches),
        "omitted_fields": [
            "utterance",
            "patient_id",
            "practitioner_id",
            "appointment_id",
            "payload",
        ],
        "boundaries": {
            "provider_calls": "prohibited",
            "route_calls": "prohibited",
            "database_access": "prohibited",
            "raw_trove_access": "prohibited",
            "runtime_memory": "prohibited",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Emit a safe aggregate Bernie interpretation harness report."
    )
    parser.add_argument(
        "--fixture-dir",
        type=Path,
        default=DEFAULT_FIXTURE_DIR,
        help="Directory containing Bernie interpretation harness fixtures.",
    )
    args = parser.parse_args()
    report = build_harness_report(args.fixture_dir)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
