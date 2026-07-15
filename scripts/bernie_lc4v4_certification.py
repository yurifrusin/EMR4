#!/usr/bin/env python3
"""Fail-closed LC4V4 manifest, seal, one-shot, and aggregate CLI."""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

from app.services.bernie.lc4v4_certification import (
    build_manifest,
    check_aggregate_report,
    create_seal,
    reconstruct_manifest,
    run_baseline_once,
    verify_manifest_against_corpus,
    write_json_exclusive,
)


def _read_object(path: pathlib.Path, label: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    build = commands.add_parser("build-manifest")
    build.add_argument("corpus", type=pathlib.Path)
    build.add_argument("quality_receipt", type=pathlib.Path)
    build.add_argument("--write", type=pathlib.Path, required=True)

    check = commands.add_parser("check-manifest")
    check.add_argument("corpus", type=pathlib.Path)
    check.add_argument("quality_receipt", type=pathlib.Path)
    check.add_argument("manifest", type=pathlib.Path)

    seal = commands.add_parser("create-seal")
    seal.add_argument("corpus", type=pathlib.Path)
    seal.add_argument("quality_receipt", type=pathlib.Path)
    seal.add_argument("manifest", type=pathlib.Path)
    seal.add_argument("--write", type=pathlib.Path, required=True)

    baseline = commands.add_parser("baseline-once")
    baseline.add_argument("corpus", type=pathlib.Path)
    baseline.add_argument("quality_receipt", type=pathlib.Path)
    baseline.add_argument("manifest", type=pathlib.Path)
    baseline.add_argument("seal", type=pathlib.Path)
    baseline.add_argument("--write", type=pathlib.Path, required=True)
    baseline.add_argument("consumed_seal", type=pathlib.Path)

    aggregate = commands.add_parser("check-aggregate")
    aggregate.add_argument("report", type=pathlib.Path)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.command == "check-aggregate":
        report = _read_object(args.report, "aggregate report")
        result = check_aggregate_report(report)
        if not result["valid"]:
            raise ValueError(f"aggregate report invalid: {result['errors']}")
        print("Aggregate report valid")
        print(f"Report hash: {report['report_hash']}")
        return 0

    quality = _read_object(args.quality_receipt, "authoring quality receipt")
    if args.command == "build-manifest":
        manifest = build_manifest(args.corpus, quality)
        write_json_exclusive(args.write, manifest)
        print(f"Manifest written to {args.write}")
        return 0

    manifest = _read_object(args.manifest, "manifest")
    reconstruct_manifest(manifest)
    verify_manifest_against_corpus(args.corpus, manifest, quality)
    if args.command == "check-manifest":
        print("Manifest exactly matches LC4V4 corpus and quality receipt")
        return 0
    if args.command == "create-seal":
        seal = create_seal(manifest)
        write_json_exclusive(args.write, seal)
        print(f"Seal written to {args.write}")
        return 0
    seal = _read_object(args.seal, "seal")
    run_baseline_once(
        args.corpus,
        manifest,
        quality,
        seal,
        report_path=args.write,
        consumed_seal_path=args.consumed_seal,
    )
    print(f"Report written to {args.write}")
    print(f"Consumed seal written to {args.consumed_seal}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
