#!/usr/bin/env python3
"""LC4V2 content-blind framework CLI.

Explicit non-mutating commands (``--write`` required to create files):

    build-manifest   Build a manifest from a group fixture directory.
    create-seal      Create a pre-consumption seal from a manifest.
    evaluate-once    Run a content-blind aggregate evaluation.
    consume          Consume an aggregate report (one-shot).
    check            Verify manifest integrity against a group directory.

Usage:
    python scripts/bernie_holdout_v2.py build-manifest <group-dir> [--output FILE] [--write]
    python scripts/bernie_holdout_v2.py create-seal <manifest> <source-commit> [--output FILE] [--write]
    python scripts/bernie_holdout_v2.py evaluate-once <manifest> <seal> <group-dir> [--output FILE] [--write]
    python scripts/bernie_holdout_v2.py consume <seal> <report> <source-commit> [--output FILE] [--write]
    python scripts/bernie_holdout_v2.py check <manifest> <group-dir> [--expected-groups 24] [...]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.bernie.holdout_v2_contract import (
    CANONICAL_ENCODING,
    DEFAULT_GROUP_COUNT,
    DEFAULT_MULTI_TURN_COUNT,
    DEFAULT_VARIANT_COUNT,
    AggregateReport,
    ConsumedSeal,
    Manifest,
    PreConsumptionSeal,
    build_manifest,
    consume_report,
    create_seal,
    run_aggregate_evaluation,
    verify_manifest,
)


def _read_json(path: Path):
    with open(path, "r", encoding=CANONICAL_ENCODING) as fh:
        return json.load(fh)


def _write_json(data, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False),
        encoding=CANONICAL_ENCODING,
    )


# ---------------------------------------------------------------------------
#  Command:  build-manifest
# ---------------------------------------------------------------------------

def cmd_build_manifest(args: argparse.Namespace) -> int:
    group_dir = args.group_dir.resolve()
    if not group_dir.is_dir():
        print(f"ERROR: not a directory: {group_dir}", file=sys.stderr)
        return 1

    try:
        manifest = build_manifest(group_dir)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    data = manifest.model_dump(mode="json")
    if args.write:
        _write_json(data, args.output)
    print(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


# ---------------------------------------------------------------------------
#  Command:  create-seal
# ---------------------------------------------------------------------------

def cmd_create_seal(args: argparse.Namespace) -> int:
    try:
        manifest_data = _read_json(args.manifest)
        manifest = Manifest.model_validate(manifest_data)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: invalid manifest: {exc}", file=sys.stderr)
        return 1

    try:
        seal = create_seal(
            manifest,
            source_commit=args.source_commit,
        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    data = seal.model_dump(mode="json")
    if args.write:
        _write_json(data, args.output)
    print(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


# ---------------------------------------------------------------------------
#  Command:  evaluate-once
# ---------------------------------------------------------------------------

def cmd_evaluate_once(args: argparse.Namespace) -> int:
    try:
        manifest_data = _read_json(args.manifest)
        manifest = Manifest.model_validate(manifest_data)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: invalid manifest: {exc}", file=sys.stderr)
        return 1

    try:
        seal_data = _read_json(args.seal)
        seal = PreConsumptionSeal.model_validate(seal_data)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: invalid seal: {exc}", file=sys.stderr)
        return 1

    group_dir = args.group_dir.resolve()
    if not group_dir.is_dir():
        print(f"ERROR: not a directory: {group_dir}", file=sys.stderr)
        return 1

    try:
        report = run_aggregate_evaluation(manifest, seal, group_dir)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    data = report.model_dump(mode="json")
    if args.write:
        _write_json(data, args.output)
    print(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


# ---------------------------------------------------------------------------
#  Command:  consume
# ---------------------------------------------------------------------------

def cmd_consume(args: argparse.Namespace) -> int:
    try:
        seal_data = _read_json(args.seal)
        seal = PreConsumptionSeal.model_validate(seal_data)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: invalid seal: {exc}", file=sys.stderr)
        return 1

    try:
        report_data = _read_json(args.report)
        report = AggregateReport.model_validate(report_data)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: invalid report: {exc}", file=sys.stderr)
        return 1

    try:
        consumed = consume_report(seal, report, source_commit=args.source_commit)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    data = consumed.model_dump(mode="json")
    if args.write:
        _write_json(data, args.output)
    print(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


# ---------------------------------------------------------------------------
#  Command:  check
# ---------------------------------------------------------------------------

def cmd_check(args: argparse.Namespace) -> int:
    try:
        manifest_data = _read_json(args.manifest)
        manifest = Manifest.model_validate(manifest_data)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: invalid manifest: {exc}", file=sys.stderr)
        return 1

    group_dir = args.group_dir.resolve()
    if not group_dir.is_dir():
        print(f"ERROR: not a directory: {group_dir}", file=sys.stderr)
        return 1

    try:
        verify_manifest(
            manifest,
            group_dir,
            expected_group_count=args.expected_groups,
            expected_variant_count=args.expected_variants,
            expected_multi_turn_count=args.expected_multi_turn,
        )
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print("PASS: manifest verified successfully")
    return 0


# ---------------------------------------------------------------------------
#  Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="LC4V2 content-blind framework CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # build-manifest
    p = sub.add_parser("build-manifest", help="Build manifest from group dir")
    p.add_argument("group_dir", type=Path, help="Path to group fixture directory")
    p.add_argument("--output", type=Path, default=Path("lc4v2-manifest.json"),
                   help="Output path (default: lc4v2-manifest.json)")
    p.add_argument("--write", action="store_true",
                   help="Write output to file (default: print only)")
    p.set_defaults(func=cmd_build_manifest)

    # create-seal
    p = sub.add_parser("create-seal", help="Create pre-consumption seal")
    p.add_argument("manifest", type=Path, help="Path to manifest JSON")
    p.add_argument("source_commit", type=str, help="Exact source commit hash")
    p.add_argument("--output", type=Path, default=Path("lc4v2-seal.json"),
                   help="Output path (default: lc4v2-seal.json)")
    p.add_argument("--write", action="store_true",
                   help="Write output to file (default: print only)")
    p.set_defaults(func=cmd_create_seal)

    # evaluate-once
    p = sub.add_parser("evaluate-once", help="Run aggregate evaluation")
    p.add_argument("manifest", type=Path, help="Path to manifest JSON")
    p.add_argument("seal", type=Path, help="Path to pre-consumption seal JSON")
    p.add_argument("group_dir", type=Path, help="Path to group fixture directory")
    p.add_argument("--output", type=Path, default=Path("lc4v2-report.json"),
                   help="Output path (default: lc4v2-report.json)")
    p.add_argument("--write", action="store_true",
                   help="Write output to file (default: print only)")
    p.set_defaults(func=cmd_evaluate_once)

    # consume
    p = sub.add_parser("consume", help="Consume aggregate report (one-shot)")
    p.add_argument("seal", type=Path, help="Path to pre-consumption seal JSON")
    p.add_argument("report", type=Path, help="Path to aggregate report JSON")
    p.add_argument("source_commit", type=str, help="Exact source commit hash")
    p.add_argument("--output", type=Path, default=Path("lc4v2-consumed-seal.json"),
                   help="Output path (default: lc4v2-consumed-seal.json)")
    p.add_argument("--write", action="store_true",
                   help="Write output to file (default: print only)")
    p.set_defaults(func=cmd_consume)

    # check
    p = sub.add_parser("check", help="Verify manifest against group directory")
    p.add_argument("manifest", type=Path, help="Path to manifest JSON")
    p.add_argument("group_dir", type=Path, help="Path to group fixture directory")
    p.add_argument("--expected-groups", type=int, default=DEFAULT_GROUP_COUNT,
                   help=f"Expected group count (default: {DEFAULT_GROUP_COUNT})")
    p.add_argument("--expected-variants", type=int, default=DEFAULT_VARIANT_COUNT,
                   help=f"Expected variant count (default: {DEFAULT_VARIANT_COUNT})")
    p.add_argument("--expected-multi-turn", type=int, default=DEFAULT_MULTI_TURN_COUNT,
                   help=f"Expected multi-turn count (default: {DEFAULT_MULTI_TURN_COUNT})")
    p.set_defaults(func=cmd_check)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
