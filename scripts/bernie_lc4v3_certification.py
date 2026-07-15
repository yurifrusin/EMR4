#!/usr/bin/env python
"""LC4V3 content-blind certification CLI.

Usage:
    python scripts/bernie_lc4v3_certification.py build-manifest <corpus_dir> [--write <output>]
    python scripts/bernie_lc4v3_certification.py check-manifest <corpus_dir> <manifest>
    python scripts/bernie_lc4v3_certification.py create-seal <corpus_dir> <manifest> --write <output>
    python scripts/bernie_lc4v3_certification.py baseline-once <corpus_dir> <manifest> <seal> --write <report> <consumed-seal>
    python scripts/bernie_lc4v3_certification.py check-aggregate <report>

Commands
--------
build-manifest
    Build the manifest from a corpus directory.  Mutating with --write.

create-seal
    Create a seal from a manifest file.  Mutating with --write.

baseline-once
    Run the one-shot aggregate evaluation.  Refuses if either
    authority-bearing output (report or consumed-seal) already exists.
    Writes the report exclusively and the consumed seal last.
    Mutating with --write.

check-aggregate
    Post-consumption check of the aggregate report.  Never loads or hashes
    the corpus.  Non-mutating (--write not required).

The ``--write`` flag is required for all mutating commands.
"""

from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.bernie.lc4v3_certification import (
    build_manifest,
    check_aggregate_report,
    create_seal,
    evaluate_aggregate,
    get_source_commit,
    load_verified_scenarios,
    verify_manifest_against_corpus,
    verify_seal,
)


def _load_json(path: pathlib.Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json_exclusive(data: dict, path: pathlib.Path) -> None:
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, default=str)
        f.write("\n")


def _path_exists(path: str | None) -> bool:
    if path is None:
        return False
    return pathlib.Path(path).exists()


def cmd_build_manifest(args: list[str]) -> int:
    """Handle ``build-manifest`` command."""
    if len(args) not in {1, 3} or (len(args) == 3 and args[1] != "--write"):
        print("Error: build-manifest requires <corpus_dir> [--write <output>]", file=sys.stderr)
        return 1

    corpus_dir = pathlib.Path(args[0])
    write_output = args[2] if len(args) == 3 else None

    manifest = build_manifest(corpus_dir)
    output = json.dumps(manifest, indent=2, default=str)

    if write_output:
        out_path = pathlib.Path(write_output)
        _write_json_exclusive(manifest, out_path)
        print(f"Manifest written to {out_path}")
    else:
        print(output)

    return 0


def cmd_check_manifest(args: list[str]) -> int:
    """Pre-consumption exact corpus/manifest check."""
    if len(args) != 2:
        print("Error: check-manifest requires <corpus_dir> <manifest>", file=sys.stderr)
        return 1
    manifest = _load_json(pathlib.Path(args[1]))
    verify_manifest_against_corpus(pathlib.Path(args[0]), manifest)
    print("Manifest exactly matches LC4V3 corpus")
    return 0


def cmd_create_seal(args: list[str]) -> int:
    """Handle ``create-seal`` command."""
    if len(args) != 4 or args[2] != "--write":
        print("Error: create-seal requires <corpus_dir> <manifest> --write <output>", file=sys.stderr)
        return 1

    corpus_dir = pathlib.Path(args[0])
    manifest_path = pathlib.Path(args[1])
    write_output = args[3]

    manifest = _load_json(manifest_path)
    verified = verify_manifest_against_corpus(corpus_dir, manifest)
    seal = create_seal(verified, source_commit=get_source_commit())
    out_path = pathlib.Path(write_output)
    if (
        out_path.resolve() == manifest_path.resolve()
        or out_path.resolve().is_relative_to(corpus_dir.resolve())
    ):
        print("Error: seal output must be distinct from inputs", file=sys.stderr)
        return 1
    _write_json_exclusive(seal, out_path)
    print(f"Seal written to {out_path}")
    return 0


def cmd_baseline_once(args: list[str]) -> int:
    """Handle ``baseline-once`` command.

    Refuses if either authority-bearing output already exists.
    Writes report exclusively, then writes consumed seal last.
    """
    if len(args) != 6 or args[3] != "--write":
        print(
            "Error: usage: baseline-once <corpus_dir> <manifest> <seal> "
            "[--write <report> <consumed-seal>]",
            file=sys.stderr,
        )
        return 1

    corpus_dir = pathlib.Path(args[0])
    manifest_path = pathlib.Path(args[1])
    seal_path = pathlib.Path(args[2])
    report_output = args[4]
    consumed_seal_output = args[5]

    report_path = pathlib.Path(report_output)
    consumed_path = pathlib.Path(consumed_seal_output)
    resolved = {
        report_path.resolve(), consumed_path.resolve(), manifest_path.resolve(), seal_path.resolve()
    }
    if len(resolved) != 4:
        print("Error: manifest, seal, report, and consumed-seal paths must be distinct", file=sys.stderr)
        return 1
    corpus_root = corpus_dir.resolve()
    if report_path.resolve().is_relative_to(corpus_root) or consumed_path.resolve().is_relative_to(corpus_root):
        print("Error: authority-bearing outputs must remain outside the corpus", file=sys.stderr)
        return 1

    # Refuse if either output already exists
    if _path_exists(report_output):
        print(
            f"Error: report output already exists: {report_output}",
            file=sys.stderr,
        )
        return 1
    if _path_exists(consumed_seal_output):
        print(
            f"Error: consumed-seal output already exists: {consumed_seal_output}",
            file=sys.stderr,
        )
        return 1
    manifest = _load_json(manifest_path)
    seal = _load_json(seal_path)
    verified_manifest = verify_manifest_against_corpus(corpus_dir, manifest)
    source_commit = get_source_commit()
    verified_seal = verify_seal(
        seal, verified_manifest, expected_source_commit=source_commit,
    )
    scenarios = load_verified_scenarios(corpus_dir)

    # Run aggregate evaluation exclusively
    report = evaluate_aggregate(
        scenarios,
        manifest_hash=verified_seal["manifest_hash"],
        corpus_hash=verified_seal["corpus_hash"],
        source_commit=source_commit,
    )

    # Write report first (exclusively)
    _write_json_exclusive(report, report_path)
    print(f"Report written to {report_path}")

    # Mark seal consumed and write it last
    consumed_seal = dict(seal)
    consumed_seal["consumed"] = True
    consumed_seal["report_hash"] = report["report_hash"]
    _write_json_exclusive(consumed_seal, consumed_path)
    print(f"Consumed seal written to {consumed_path}")

    return 0


def cmd_check_aggregate(args: list[str]) -> int:
    """Handle ``check-aggregate`` command.

    Post-consumption verification of the aggregate report.
    Never loads or hashes the protected corpus.
    """
    if len(args) != 1:
        print("Error: check-aggregate requires exactly <report>", file=sys.stderr)
        return 1

    report_path = pathlib.Path(args[0])
    report = _load_json(report_path)

    result = check_aggregate_report(report)

    if result["valid"]:
        print("Aggregate report valid")
    else:
        print("Aggregate report INVALID:")
        for error in result["errors"]:
            print(f"  - {error}")

    print(f"Report hash: {report.get('report_hash', 'N/A')}")
    print(f"Total samples: {report.get('total_samples', 'N/A')}")
    print(f"Schema version: {report.get('schema_version', 'N/A')}")
    print(f"Evaluation ID: {report.get('evaluation_id', 'N/A')}")

    return 0 if result["valid"] else 1


def main() -> int:
    """Dispatch CLI commands."""
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 1

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "build-manifest":
        return cmd_build_manifest(args)
    elif command == "check-manifest":
        return cmd_check_manifest(args)
    elif command == "create-seal":
        return cmd_create_seal(args)
    elif command == "baseline-once":
        return cmd_baseline_once(args)
    elif command == "check-aggregate":
        return cmd_check_aggregate(args)
    elif command in ("--help", "-h"):
        print(__doc__)
        return 0
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
