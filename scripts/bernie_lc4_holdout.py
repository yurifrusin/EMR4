"""Author, consume once, or verify the protected LC4 holdout."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.lc4_holdout_support import (  # noqa: E402
    author_holdout_fixture,
    evaluate_once,
    verify_sealed_artifacts,
)


FIXTURE_DIR = ROOT / "tests" / "fixtures" / "bernie_lc4_holdout"
SEAL_RECEIPT = ROOT / "docs" / "bernie-lc4-holdout-seal-receipt.json"
REPORT_PATH = ROOT / "docs" / "bernie-lc4-holdout-aggregate-report.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--author-and-seal", action="store_true")
    mode.add_argument("--evaluate-once", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.author_and_seal:
        author_holdout_fixture(FIXTURE_DIR, SEAL_RECEIPT)
        print("LC4 holdout authored and sealed; baseline remains unconsumed.")
    elif args.evaluate_once:
        report = evaluate_once(FIXTURE_DIR, SEAL_RECEIPT, REPORT_PATH)
        print(
            "LC4 holdout baseline consumed once: "
            f"{report['aggregate']['passed']}/{report['aggregate']['total']} passed."
        )
    else:
        verify_sealed_artifacts(FIXTURE_DIR, SEAL_RECEIPT, REPORT_PATH)
        print("LC4 sealed holdout artifacts verified without re-evaluation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
