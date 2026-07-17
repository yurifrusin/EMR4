"""Write or verify the admitted synthetic Silver robustness baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.bernie.synthetic_noise_robustness import (  # noqa: E402
    DEFAULT_REPORT_PATH,
    build_baseline_report,
    write_baseline_report,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()

    if args.write:
        report = write_baseline_report(args.output)
        print(f"wrote {args.output}")
    else:
        if not args.output.is_file():
            print(f"missing report: {args.output}", file=sys.stderr)
            return 1
        committed = json.loads(args.output.read_text(encoding="utf-8"))
        report = build_baseline_report()
        if committed != report:
            print("committed baseline report does not regenerate", file=sys.stderr)
            return 1

    population = report["population"]
    print(
        f"decision={report['decision']} "
        f"complete={population['complete_candidates']}/{population['candidates']} "
        f"observations={population['observations']} "
        f"variance={report['variance']['variant_candidate_count']}"
    )
    print(f"report_hash={report['report_hash']}")
    return 0 if report["decision"] == "baseline_complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
