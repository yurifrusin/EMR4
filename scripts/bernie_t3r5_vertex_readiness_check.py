"""Render the committed T3R5 no-call Vertex readiness evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.ai.evals.bernie_vertex_au_readiness import build_readiness_report


DEFAULT_EVIDENCE = ROOT / "docs" / "bernie-t3r5-vertex-au-feasibility.json"
DEFAULT_REPORT = ROOT / "docs" / "bernie-t3r5-vertex-au-readiness-report.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    report = build_readiness_report(evidence)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            print("T3R5 readiness report is stale", file=sys.stderr)
            return 2
    else:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(json.dumps({"decision": report["decision"], "report_hash": report["report_hash"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
