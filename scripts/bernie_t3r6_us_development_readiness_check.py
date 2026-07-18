"""Render or check the committed T3R6 US synthetic-development report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.ai.evals.bernie_us_synthetic_development_readiness import (
    build_readiness_report,
)


DEFAULT_EVIDENCE = ROOT / "docs" / "bernie-t3r6-us-synthetic-development-policy.json"
DEFAULT_REPORT = ROOT / "docs" / "bernie-t3r6-us-synthetic-development-report.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--as-of")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    report = build_readiness_report(evidence, as_of=args.as_of)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            print("T3R6 report is stale", file=sys.stderr)
            return 2
    else:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "policy_decision": report["policy_decision"],
                "readiness_decision": report["readiness_decision"],
                "report_hash": report["report_hash"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
