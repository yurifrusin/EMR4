#!/usr/bin/env python3
"""Explicit, fail-closed LC4V2 manifest/seal/baseline CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.bernie.holdout_v2_contract import (  # noqa: E402
    AggregateReport,
    ConsumedSeal,
    Manifest,
    PreConsumptionSeal,
    build_manifest,
    consume_report,
    create_seal,
    evaluate_aggregate,
    validate_aggregate_payload,
    verify_manifest,
)


def _read(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _encoded(model) -> str:
    return json.dumps(
        model.model_dump(mode="json"),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def _write(path: Path, model, *, exclusive: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "x" if exclusive else "w"
    try:
        with path.open(mode, encoding="utf-8", newline="\n") as handle:
            handle.write(_encoded(model))
    except FileExistsError as error:
        raise ValueError(f"refusing to overwrite one-shot output: {path}") from error


def _require_write(args: argparse.Namespace) -> None:
    if not args.write:
        raise ValueError("this command requires explicit --write")


def cmd_build_manifest(args: argparse.Namespace) -> int:
    _require_write(args)
    manifest = build_manifest(args.group_dir)
    verify_manifest(manifest, args.group_dir)
    _write(args.output, manifest)
    print(f"manifest_written={args.output}")
    print(f"manifest_hash={manifest.digest()}")
    return 0


def cmd_create_seal(args: argparse.Namespace) -> int:
    _require_write(args)
    manifest = Manifest.model_validate(_read(args.manifest))
    seal = create_seal(
        manifest,
        args.group_dir,
        source_commit=args.source_commit,
    )
    _write(args.output, seal)
    print(f"seal_written={args.output}")
    print(f"manifest_hash={seal.manifest_hash}")
    return 0


def cmd_baseline_once(args: argparse.Namespace) -> int:
    _require_write(args)
    if args.report_output.exists() or args.consumed_output.exists():
        raise ValueError("one-shot output already exists; baseline will not run")
    manifest = Manifest.model_validate(_read(args.manifest))
    seal = PreConsumptionSeal.model_validate(_read(args.seal))
    report = evaluate_aggregate(
        manifest,
        seal,
        args.group_dir,
        source_commit=args.source_commit,
    )
    consumed = consume_report(seal, report)
    # Exclusive writes make a second invocation fail before it can replace
    # either authority-bearing artifact.  The report is written first and the
    # consumed seal last; a partial failure is visibly incomplete, never pass.
    _write(args.report_output, report, exclusive=True)
    _write(args.consumed_output, consumed, exclusive=True)
    print(f"report_written={args.report_output}")
    print(f"consumed_seal_written={args.consumed_output}")
    print(f"report_hash={report.report_hash}")
    return 0


def cmd_check_manifest(args: argparse.Namespace) -> int:
    manifest = Manifest.model_validate(_read(args.manifest))
    verify_manifest(manifest, args.group_dir)
    print("manifest_check=passed")
    return 0


def cmd_check_aggregate(args: argparse.Namespace) -> int:
    report = validate_aggregate_payload(_read(args.report))
    consumed = ConsumedSeal.model_validate(_read(args.consumed_seal))
    seal = PreConsumptionSeal.model_validate(_read(args.pre_seal))
    expected = consume_report(
        seal,
        report,
        consumed_at=consumed.consumed_at,
    )
    if expected != consumed:
        raise ValueError("consumed seal does not bind aggregate report")
    print("aggregate_check=passed")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    build = commands.add_parser("build-manifest")
    build.add_argument("group_dir", type=Path)
    build.add_argument("output", type=Path)
    build.add_argument("--write", action="store_true")
    build.set_defaults(handler=cmd_build_manifest)

    seal = commands.add_parser("create-seal")
    seal.add_argument("manifest", type=Path)
    seal.add_argument("group_dir", type=Path)
    seal.add_argument("source_commit")
    seal.add_argument("output", type=Path)
    seal.add_argument("--write", action="store_true")
    seal.set_defaults(handler=cmd_create_seal)

    baseline = commands.add_parser("baseline-once")
    baseline.add_argument("manifest", type=Path)
    baseline.add_argument("seal", type=Path)
    baseline.add_argument("group_dir", type=Path)
    baseline.add_argument("source_commit")
    baseline.add_argument("report_output", type=Path)
    baseline.add_argument("consumed_output", type=Path)
    baseline.add_argument("--write", action="store_true")
    baseline.set_defaults(handler=cmd_baseline_once)

    check_manifest = commands.add_parser("check-manifest")
    check_manifest.add_argument("manifest", type=Path)
    check_manifest.add_argument("group_dir", type=Path)
    check_manifest.set_defaults(handler=cmd_check_manifest)

    check_aggregate = commands.add_parser("check-aggregate")
    check_aggregate.add_argument("report", type=Path)
    check_aggregate.add_argument("pre_seal", type=Path)
    check_aggregate.add_argument("consumed_seal", type=Path)
    check_aggregate.set_defaults(handler=cmd_check_aggregate)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except (ValueError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
