#!/usr/bin/env python3
"""LC3 Composed T2/T3 Evaluator — offline corpus consumer and report generator.

Loads all 3 LC1 Gold and 15 LC2 Silver fixtures, runs deterministic
interpretation and replay, scores every pair, and emits a deterministic
machine-readable report to ``docs/bernie-lc3-composed-evaluation-report.json``.

Usage:
    python scripts/bernie_lc3_composed_eval.py
    python scripts/bernie_lc3_composed_eval.py --lc1-dir <path> --lc2-dir <path>
    python scripts/bernie_lc3_composed_eval.py --output <path>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.bernie.composed_corpus_evaluator import (
    _default_lc1_fixture_dir,
    _default_lc2_candidate_dir,
    generate_report_json,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="LC3 Composed T2/T3 Evaluator — offline corpus consumer",
    )
    parser.add_argument(
        "--lc1-dir",
        type=Path,
        default=None,
        help="Path to LC1 Gold scenario fixture directory",
    )
    parser.add_argument(
        "--lc2-dir",
        type=Path,
        default=None,
        help="Path to LC2 Silver candidate wrapper directory",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "docs" / "bernie-lc3-composed-evaluation-report.json",
        help="Output path for the deterministic report",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    lc1_dir = args.lc1_dir if args.lc1_dir is not None else _default_lc1_fixture_dir()
    lc2_dir = args.lc2_dir if args.lc2_dir is not None else _default_lc2_candidate_dir()

    try:
        report_json = generate_report_json(
            lc1_fixture_dir=lc1_dir,
            lc2_candidate_dir=lc2_dir,
        )
    except (FileNotFoundError, NotADirectoryError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    output_path = args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report_json, encoding="utf-8")
    print(report_json, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
