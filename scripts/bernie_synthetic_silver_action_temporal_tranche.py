"""Generate or verify the frozen synthetic Silver action/temporal tranche."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.bernie.synthetic_noise_action_temporal import (  # noqa: E402
    BASELINE_REPORT_PATH,
    build_tranche_report,
    write_tranche_report,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=BASELINE_REPORT_PATH)
    args = parser.parse_args()

    report = build_tranche_report()
    if args.check:
        if not args.output.exists():
            raise SystemExit(f"missing tranche report: {args.output}")
        committed = json.loads(args.output.read_text(encoding="utf-8"))
        if committed != report:
            raise SystemExit("tranche report does not regenerate exactly")
    else:
        report = write_tranche_report(args.output)

    population = report["population"]
    print(
        f"decision={report['decision']} "
        f"complete={population['complete_candidates']}/{population['candidates']} "
        f"observations={population['observations']} "
        f"variance={report['variance']['variant_candidate_count']}"
    )
    print(f"report_hash={report['report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
