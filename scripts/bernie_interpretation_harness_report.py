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
FORBIDDEN_REPORT_FRAGMENTS = (
    "patient_id",
    "practitioner_id",
    "appointment_id",
    "payload",
    "/api/",
    "local_data",
    "h15",
    "h_series",
)
FORBIDDEN_REPORT_TEXT_FRAGMENTS = (
    "book an appointment",
    "which patient",
    "ignore the rules",
    "cancel the appointment because",
)
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

    if not fixture_dir.exists():
        raise ValueError(f"Fixture directory does not exist: {fixture_dir}")
    if not fixture_dir.is_dir():
        raise ValueError(f"Fixture path is not a directory: {fixture_dir}")

    fixture_paths = sorted(fixture_dir.glob("*.json"))
    if not fixture_paths:
        raise ValueError(f"No JSON fixtures found in: {fixture_dir}")

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
            if not isinstance(cases, list) or not cases:
                raise ValueError(f"Fixture cases must be a non-empty list: {path.name}")
            case_fixture_paths.append(path)
            fixture_case_counts[path.name] = len(cases)
            for case in cases:
                dispatch_counts[case["expected_dispatch"]] += 1
                frame_kind_counts[case["expected_frame_kind"]] += 1
        if contracts is not None:
            if not isinstance(contracts, list) or not contracts:
                raise ValueError(f"Fixture contracts must be a non-empty list: {path.name}")
            contract_count += len(contracts)
            contract_dispatches.extend(contract["dispatch"] for contract in contracts)

    if not case_fixture_paths:
        raise ValueError(f"No case fixtures found in: {fixture_dir}")
    if contract_count == 0:
        raise ValueError(f"No contract fixtures found in: {fixture_dir}")

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


def _walk_report_values(value: Any) -> tuple[str, ...]:
    if isinstance(value, dict):
        parts: list[str] = []
        for key, child in value.items():
            parts.append(str(key))
            parts.extend(_walk_report_values(child))
        return tuple(parts)
    if isinstance(value, list):
        parts = []
        for child in value:
            parts.extend(_walk_report_values(child))
        return tuple(parts)
    return (str(value),)


def assert_harness_report_safety(report: dict[str, Any]) -> None:
    """Assert a report remains aggregate-only and non-authoritative."""

    assert report.get("schema_version") == REPORT_SCHEMA_VERSION
    assert report.get("source_schema_version") == INTERPRETATION_HARNESS_SCHEMA_VERSION
    assert report.get("source") == "authored_synthetic_aggregate"
    assert isinstance(report.get("case_count"), int)
    assert isinstance(report.get("contract_count"), int)
    assert report["case_count"] > 0
    assert report["contract_count"] > 0

    boundaries = report.get("boundaries")
    assert boundaries == {
        "provider_calls": "prohibited",
        "route_calls": "prohibited",
        "database_access": "prohibited",
        "raw_trove_access": "prohibited",
        "runtime_memory": "prohibited",
    }

    omitted_fields = report.get("omitted_fields")
    assert omitted_fields == [
        "utterance",
        "patient_id",
        "practitioner_id",
        "appointment_id",
        "payload",
    ]

    dispatch_counts = report.get("dispatch_counts")
    contract_dispatches = report.get("contract_dispatches")
    assert isinstance(dispatch_counts, dict)
    assert isinstance(contract_dispatches, list)
    assert set(dispatch_counts) == set(contract_dispatches)

    searchable_parts = [
        part.casefold()
        for part in _walk_report_values(report)
        if part not in omitted_fields
    ]
    for fragment in FORBIDDEN_REPORT_FRAGMENTS:
        assert not any(fragment in part for part in searchable_parts)
    for fragment in FORBIDDEN_REPORT_TEXT_FRAGMENTS:
        assert not any(fragment in part for part in searchable_parts)


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
    assert_harness_report_safety(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
