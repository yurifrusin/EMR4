"""Generate or verify the unchanged-product synthetic Silver v2 baseline."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.bernie.synthetic_noise_v2_robustness import (  # noqa: E402
    build_v2_robustness_report,
    check_v2_robustness_report,
    write_v2_robustness_report,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        report = write_v2_robustness_report()
        print(f"evaluated {report['population']['candidates']} v2 candidates")
        print(f"COMPLETE: {report['population']['complete_candidates']}/192")
        print(f"SAFETY: {report['safety']['passed']}/{report['safety']['total']}")
        print(f"VARIANCE: {report['variance']['variant_candidate_count']}")
        print(f"REPORT_HASH: {report['report_hash']}")
        return 0
    errors = check_v2_robustness_report()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    report = build_v2_robustness_report()
    print(f"validated v2 robustness baseline {report['report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
