"""Generate or verify the provider-free T3R1 synthetic shadow refresh."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.ai.evals.bernie_shadow_silver_v2 import (  # noqa: E402
    build_t3r1_shadow_report,
    check_t3r1_shadow_report,
    write_t3r1_shadow_report,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.write:
        report = write_t3r1_shadow_report()
    else:
        errors = check_t3r1_shadow_report()
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            return 1
        report = build_t3r1_shadow_report()

    projection = report["projection"]
    plumbing = report["offline_plumbing_check"]
    print(f"DECISION: {report['decision']}")
    print(f"CASES: {projection['case_count']}")
    print(
        "OFFLINE_PLUMBING: "
        f"{plumbing['perfect_sample_count']}/{plumbing['sample_count']}"
    )
    print(f"SAFETY: {plumbing['safe_sample_count']}/{plumbing['sample_count']}")
    print(f"VARIANCE: {plumbing['variant_case_count']}")
    print(f"PROVIDER_CALLS: {str(plumbing['provider_calls_performed']).lower()}")
    print(f"PROJECTION_HASH: {projection['projection_hash']}")
    print(f"REPORT_HASH: {report['report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
