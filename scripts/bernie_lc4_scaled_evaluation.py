"""LC4 development scaled evaluation — reproducible report.

Usage:
    py scripts/bernie_lc4_scaled_evaluation.py          # write report
    py scripts/bernie_lc4_scaled_evaluation.py --check  # verify in memory only
    py scripts/bernie_lc4_scaled_evaluation.py --help    # usage

Output:
    docs/bernie-lc4-development-evaluation-report.json (deterministic, write mode)
"""

from __future__ import annotations

import json
import pathlib
import sys

_HERE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_HERE))

from app.services.bernie.scaled_evaluator import (
    LC4_SCALED_REPORT_SCHEMA_VERSION,
    generate_scaled_evaluation_report,
    validate_scaled_evaluator_isolation,
)

REPORT_PATH = _HERE / "docs" / "bernie-lc4-development-evaluation-report.json"


def _compute_report() -> dict:
    """Compute the report in memory and return the dict."""
    # Validate isolation first
    validate_scaled_evaluator_isolation()

    fixture_dir = _HERE / "tests" / "fixtures" / "bernie_lc4_development"
    report = generate_scaled_evaluation_report(fixture_dir, repeats=2)
    return report


def main() -> None:
    check_mode = "--check" in sys.argv
    help_mode = "--help" in sys.argv or "-h" in sys.argv

    if help_mode:
        print(__doc__)
        return

    report = _compute_report()
    report_json = json.dumps(report, indent=2, default=str) + "\n"

    if check_mode:
        if REPORT_PATH.exists():
            existing = REPORT_PATH.read_text(encoding="utf-8")
            # Normalize line endings for comparison
            existing_normalized = existing.replace("\r\n", "\n")
            computed_normalized = report_json.replace("\r\n", "\n")
            if existing_normalized != computed_normalized:
                print("REPORT DRIFT DETECTED", file=sys.stderr)
                print(
                    "  Existing report differs from in-memory computation.",
                    file=sys.stderr,
                )
                print(
                    "  Regenerate with: "
                    "py scripts/bernie_lc4_scaled_evaluation.py",
                    file=sys.stderr,
                )
                sys.exit(1)
            print(
                "Report check passed — in-memory computation matches "
                "stored report."
            )
        else:
            print(
                f"Report file not found at {REPORT_PATH} — nothing to check.",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        REPORT_PATH.write_text(report_json, encoding="utf-8")
        print(f"Report written to {REPORT_PATH}")


if __name__ == "__main__":
    main()
