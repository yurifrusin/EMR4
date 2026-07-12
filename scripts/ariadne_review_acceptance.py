"""CLI for the deterministic review-acceptance gate.

Exit codes
----------
0 — accepted
1 — rejected
2 — input or internal error

Usage
-----
    python scripts/ariadne_review_acceptance.py \
        --artifact path/to/artifact.md \
        --artifact-kind decision|completion \
        --receipt path/to/receipt.json \
        --worktree path/to/review/worktree \
        --expected-branch claude/current \
        --candidate-commit <sha> \
        --pytest-collect-output path/to/collect.txt \
        --review-mode executable|static_evidence \
        [--worker-reported-count N]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Bootstrap repository root onto sys.path so direct invocation works
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from orchestration_harness.review_acceptance import accept_review_artifact


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic review-acceptance gate for Deep Code worker artifacts."
    )

    parser.add_argument(
        "--artifact",
        type=Path,
        required=True,
        help="Path to the worker's submitted review artifact.",
    )
    parser.add_argument(
        "--artifact-kind",
        type=str,
        required=True,
        choices=["decision", "completion"],
        help="Kind of artifact: decision (DECISION: pass|revision_required) "
        "or completion (STATUS: complete).",
    )
    parser.add_argument(
        "--receipt",
        type=Path,
        required=True,
        help="Path to the adapter receipt JSON file.",
    )
    parser.add_argument(
        "--worktree",
        type=Path,
        required=True,
        help="Path to the review worktree (cwd for git commands).",
    )
    parser.add_argument(
        "--expected-branch",
        type=str,
        required=True,
        help="Exact branch name expected (e.g. 'claude/current').",
    )
    parser.add_argument(
        "--candidate-commit",
        type=str,
        required=True,
        help="Commit SHA that should be an ancestor of HEAD.",
    )
    parser.add_argument(
        "--pytest-collect-output",
        type=Path,
        required=True,
        help="Path to a file containing captured pytest --collect-only -q output.",
    )
    parser.add_argument(
        "--review-mode",
        type=str,
        required=True,
        choices=["executable", "static_evidence"],
        help="Review mode: executable or static_evidence.",
    )
    parser.add_argument(
        "--worker-reported-count",
        type=int,
        default=None,
        help="Optional N passed claim from the worker.",
    )

    args = parser.parse_args()

    # --pytest-collect-output is always treated as a file path (never executed)
    # argparse with type=Path ensures it is a Path object, not a command string.
    collect_path = args.pytest_collect_output

    try:
        result = accept_review_artifact(
            artifact_path=args.artifact,
            artifact_kind=args.artifact_kind,  # type: ignore[arg-type]
            receipt_path=args.receipt,
            review_worktree=args.worktree,
            expected_branch=args.expected_branch,
            candidate_commit=args.candidate_commit,
            pytest_collect_path=collect_path,
            review_mode=args.review_mode,  # type: ignore[arg-type]
            worker_reported_count=args.worker_reported_count,
        )
    except (ValueError, OSError) as exc:
        print(
            f'{{"error": "unexpected error: {exc}"}}',
            file=sys.stderr,
        )
        return 2

    print(result.to_json())

    if result.accepted:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
