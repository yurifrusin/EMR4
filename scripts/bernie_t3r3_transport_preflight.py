"""Generate or verify the no-call Bernie T3R3 transport preflight report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.ai.evals.bernie_shadow_transport_preflight import (  # noqa: E402
    build_transport_preflight_report,
    check_transport_preflight_report,
    write_transport_preflight_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.write:
        report = write_transport_preflight_report()
    else:
        errors = check_transport_preflight_report()
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            return 1
        report = build_transport_preflight_report()

    print(
        json.dumps(
            {
                "decision": report["decision"],
                "lane_count": report["approval_binding"]["lane_count"],
                "maximum_scheduled_samples": report["approval_binding"]["maximum_scheduled_samples"],
                "adapter_contract_ready_lanes": report["aggregate"]["adapter_contract_ready_lanes"],
                "execution_ready_lanes": report["aggregate"]["execution_ready_lanes"],
                "provider_calls_performed": report["aggregate"]["provider_calls_performed"],
                "report_hash": report["report_hash"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
