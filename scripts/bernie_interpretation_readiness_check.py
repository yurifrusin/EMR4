"""Combined safe readiness check for the Bernie interpretation harness."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.bernie_interpretation_harness_report import (
    DEFAULT_FIXTURE_DIR,
    assert_harness_report_safety,
    build_harness_report,
)
from scripts.bernie_interpretation_runtime_gate_check import (
    DEFAULT_GATE_PATH,
    build_runtime_gate_status,
)

READINESS_SCHEMA_VERSION = "bernie.interpretation_readiness_check.v1"


def build_readiness_status(
    fixture_dir: Path = DEFAULT_FIXTURE_DIR,
    gate_path: Path = DEFAULT_GATE_PATH,
) -> dict[str, object]:
    report = build_harness_report(fixture_dir)
    assert_harness_report_safety(report)
    gate_status = build_runtime_gate_status(gate_path)

    return {
        "schema_version": READINESS_SCHEMA_VERSION,
        "harness_report_schema_version": report["schema_version"],
        "runtime_gate_status_schema_version": gate_status["schema_version"],
        "case_count": report["case_count"],
        "contract_count": report["contract_count"],
        "dispatch_count": len(report["dispatch_counts"]),
        "frame_kind_count": len(report["frame_kind_counts"]),
        "runtime_gate_decision": gate_status["decision"],
        "runtime_gate_pause_required": gate_status["pause_required"],
        "sprint_engine_state": "continuing",
        "runtime_or_provider_wiring_ready": False,
        "raw_trove_access_ready": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run safe aggregate Bernie interpretation readiness checks."
    )
    parser.add_argument(
        "--fixture-dir",
        type=Path,
        default=DEFAULT_FIXTURE_DIR,
        help="Directory containing Bernie interpretation harness fixtures.",
    )
    parser.add_argument(
        "--gate",
        type=Path,
        default=DEFAULT_GATE_PATH,
        help="Path to the runtime gate JSON file.",
    )
    args = parser.parse_args()
    status = build_readiness_status(args.fixture_dir, args.gate)
    print(json.dumps(status, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
