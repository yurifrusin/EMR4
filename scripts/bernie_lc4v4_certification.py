#!/usr/bin/env python3
"""LC4V4 content-blind certification CLI.

Usage:
    python -m scripts.bernie_lc4v4_certification --corpus-dir <path> [--seal] [--evaluate]

This script performs content-blind certification operations without loading
any real v4 corpus content.  It validates that the empty framework satisfies
all structural, identity, and hash-chain requirements.

No provider, route, database, UI, deployment, runtime, historical diary,
memory, confirmation, release, or write-authority surface is referenced.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LC4V4 content-blind certification CLI"
    )
    parser.add_argument(
        "--corpus-dir",
        type=pathlib.Path,
        default=None,
        help="Path to the corpus directory (24 group JSON files)",
    )
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Build and validate the manifest only",
    )
    parser.add_argument(
        "--seal-only",
        action="store_true",
        help="Build and validate the seal only",
    )
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="Run aggregate evaluation (requires full corpus)",
    )
    parser.add_argument(
        "--check-report",
        type=pathlib.Path,
        default=None,
        help="Validate an existing aggregate report JSON file",
    )
    parser.add_argument(
        "--forbidden-keys",
        type=pathlib.Path,
        default=None,
        help="Check a JSON file for forbidden case-level keys",
    )

    args = parser.parse_args()

    # Late import to avoid loading certification dependencies at parse time.
    from app.services.bernie.lc4v4_certification import (
        LC4V4_CORPUS_IDENTITY,
        LC4V4_EVALUATION_ID,
        LC4V4_EVALUATOR_VERSION,
        LC4V4_GROUP_COUNT,
        LC4V4_REPEAT_COUNT,
        LC4V4_TOTAL_SCENARIOS,
        LC4V4_TOTAL_SAMPLES,
        LC4V4_TOTAL_TRAJECTORIES,
        build_manifest,
        check_aggregate_report,
        check_forbidden_aggregate_keys,
        create_seal,
        evaluate_aggregate,
        get_source_commit,
        load_verified_scenarios,
        reconstruct_manifest,
        validate_lc4v4_isolation,
        verify_seal,
    )

    # Print contract constants as identity proof
    print(f"LC4V4_CORPUS_IDENTITY: {LC4V4_CORPUS_IDENTITY}")
    print(f"LC4V4_EVALUATION_ID: {LC4V4_EVALUATION_ID}")
    print(f"LC4V4_EVALUATOR_VERSION: {LC4V4_EVALUATOR_VERSION}")
    print(f"LC4V4_GROUP_COUNT: {LC4V4_GROUP_COUNT}")
    print(f"LC4V4_REPEAT_COUNT: {LC4V4_REPEAT_COUNT}")
    print(f"LC4V4_TOTAL_SCENARIOS: {LC4V4_TOTAL_SCENARIOS}")
    print(f"LC4V4_TOTAL_TRAJECTORIES: {LC4V4_TOTAL_TRAJECTORIES}")
    print(f"LC4V4_TOTAL_SAMPLES: {LC4V4_TOTAL_SAMPLES}")
    print(f"SOURCE_COMMIT: {get_source_commit()}")

    # Isolation check
    try:
        validate_lc4v4_isolation()
        print("ISOLATION: passed")
    except RuntimeError as e:
        print(f"ISOLATION: failed - {e}", file=sys.stderr)
        sys.exit(1)

    # Forbidden-key check
    if args.forbidden_keys:
        try:
            with open(args.forbidden_keys, "r", encoding="utf-8") as f:
                data = json.load(f)
            check_forbidden_aggregate_keys(data)
            print(f"FORBIDDEN_KEYS_CHECK: passed for {args.forbidden_keys}")
        except (ValueError, json.JSONDecodeError) as e:
            print(f"FORBIDDEN_KEYS_CHECK: failed - {e}", file=sys.stderr)
            sys.exit(1)
        return

    # Report validation
    if args.check_report:
        try:
            with open(args.check_report, "r", encoding="utf-8") as f:
                report = json.load(f)
            result = check_aggregate_report(report)
            if result["valid"]:
                print(f"REPORT_VALIDATION: passed for {args.check_report}")
            else:
                print(
                    f"REPORT_VALIDATION: failed - {result['errors']}",
                    file=sys.stderr,
                )
                sys.exit(1)
        except (ValueError, json.JSONDecodeError, FileNotFoundError) as e:
            print(f"REPORT_VALIDATION: error - {e}", file=sys.stderr)
            sys.exit(1)
        return

    if not args.corpus_dir:
        print("No operation specified. Use --corpus-dir or --check-report.", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    if not args.corpus_dir.is_dir():
        print(f"Corpus directory not found: {args.corpus_dir}", file=sys.stderr)
        sys.exit(1)

    # Build manifest
    try:
        manifest = build_manifest(args.corpus_dir)
        print(f"MANIFEST: built successfully")
        print(f"  files: {len(manifest['files'])}")
        print(f"  corpus_hash: {manifest['corpus_hash']}")
        reconstructed = reconstruct_manifest(manifest)
        print(f"MANIFEST_RECONSTRUCTION: passed")
    except (ValueError, NotADirectoryError) as e:
        print(f"MANIFEST: failed - {e}", file=sys.stderr)
        sys.exit(1)

    if args.manifest_only:
        print(json.dumps(manifest, indent=2))
        return

    # Create seal
    if args.seal_only or args.evaluate:
        try:
            seal = create_seal(manifest)
            print(f"SEAL: created successfully")
            print(f"  manifest_hash: {seal['manifest_hash']}")
            print(f"  consumed: {seal['consumed']}")
            verified = verify_seal(seal, manifest)
            print(f"SEAL_VERIFICATION: passed")
        except ValueError as e:
            print(f"SEAL: failed - {e}", file=sys.stderr)
            sys.exit(1)

        if args.seal_only:
            print(json.dumps(seal, indent=2))
            return

    # Evaluate
    if args.evaluate:
        try:
            scenarios = load_verified_scenarios(args.corpus_dir)
            print(f"SCENARIOS: loaded {len(scenarios)} scenarios")
            source_commit = get_source_commit()
            report = evaluate_aggregate(
                scenarios,
                manifest_hash=manifest["corpus_hash"],
                corpus_hash=manifest["corpus_hash"],
                source_commit=source_commit,
            )
            print(f"EVALUATION: completed")
            print(f"  total_samples: {report['total_samples']}")
            print(f"  report_hash: {report['report_hash']}")
            print(json.dumps(report, indent=2))
        except (ValueError, RuntimeError) as e:
            print(f"EVALUATION: failed - {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
