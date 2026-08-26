"""CLI for the immutable-source operational G1A gatekeeper."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from orchestration_harness.pinned_programme_gatekeeper import (
    evaluate_pinned_programme_operation,
    execute_exact_index_commit,
    execute_exact_sha_push,
    write_operation_receipt,
)
from orchestration_harness.programme_admission import strict_json_object


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate a target repository from the exact clean transition-pinned source."
    )
    subparsers = parser.add_subparsers(dest="operation", required=True)
    evaluate = subparsers.add_parser("evaluate")
    evaluate.add_argument("--target-repo", required=True, type=Path)
    evaluate.add_argument("--task-manifest", required=True, type=Path)
    evaluate.add_argument(
        "--entrypoint",
        required=True,
        choices=("task_branch_commit", "task_branch_push"),
    )
    evaluate.add_argument(
        "--phase", required=True, choices=("development", "pre-push", "post-push")
    )
    evaluate.add_argument("--format", choices=("human", "json"), default="human")
    commit = subparsers.add_parser("commit")
    commit.add_argument("--target-repo", required=True, type=Path)
    commit.add_argument("--task-manifest", required=True, type=Path)
    commit.add_argument("--message", required=True)
    commit.add_argument("--receipt", required=True, type=Path)
    commit.add_argument("--format", choices=("human", "json"), default="human")
    push = subparsers.add_parser("push")
    push.add_argument("--target-repo", required=True, type=Path)
    push.add_argument("--task-manifest", required=True, type=Path)
    push.add_argument("--receipt", required=True, type=Path)
    push.add_argument("--format", choices=("human", "json"), default="human")
    args = parser.parse_args()

    gatekeeper_root = Path(__file__).resolve().parents[1]
    manifest = strict_json_object(args.task_manifest.resolve())
    if args.operation == "commit":
        payload = execute_exact_index_commit(
            gatekeeper_root=gatekeeper_root,
            target_repo_root=args.target_repo,
            manifest=manifest,
            message=args.message,
        )
        write_operation_receipt(args.receipt, payload)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    if args.operation == "push":
        payload = execute_exact_sha_push(
            gatekeeper_root=gatekeeper_root,
            target_repo_root=args.target_repo,
            manifest=manifest,
        )
        write_operation_receipt(args.receipt, payload)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    decision = evaluate_pinned_programme_operation(
        gatekeeper_root=gatekeeper_root,
        target_repo_root=args.target_repo,
        manifest=manifest,
        entrypoint=args.entrypoint,
        phase=args.phase,
    )
    payload = asdict(decision)
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            "pinned programme gatekeeper: "
            + ("ADMITTED" if decision.admitted else "BLOCKED")
        )
        for reason in decision.reason_codes:
            print(f"- {reason}")
    return 0 if decision.admitted else 2


if __name__ == "__main__":
    raise SystemExit(main())
