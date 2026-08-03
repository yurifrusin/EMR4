"""Validate an exact verifier worktree before a pre-verifier receipt is issued."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.ariadne_antigravity import WorktreeState, inspect_worktree


SCHEMA_VERSION = "ariadne.verifier-worktree-preflight.v1"
DEFAULT_BRANCH_PREFIX = "codex/review-"


def build_preflight(
    *,
    cwd: Path,
    expected_head: str,
    branch_prefix: str = DEFAULT_BRANCH_PREFIX,
) -> dict[str, object]:
    state: WorktreeState = inspect_worktree(cwd, require_clean=True)
    if state.head != expected_head:
        raise ValueError(
            f"verifier worktree HEAD mismatch: {state.head}!={expected_head}"
        )
    if not state.branch.startswith(branch_prefix):
        raise ValueError(
            "verifier branch must use the non-protected review prefix: "
            f"{state.branch!r}"
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "passed",
        "worktree": state.root.as_posix(),
        "branch": state.branch,
        "head": state.head,
        "expected_head": expected_head,
        "clean": not state.dirty,
        "branch_prefix": branch_prefix,
        "provider_or_model_calls": 0,
        "authority_boundary": "local_read_only_pre_dispatch_check",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cwd", type=Path, required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--branch-prefix", default=DEFAULT_BRANCH_PREFIX)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        evidence = build_preflight(
            cwd=args.cwd,
            expected_head=args.expected_head,
            branch_prefix=args.branch_prefix,
        )
    except (OSError, ValueError) as error:
        print(json.dumps({"status": "revision_required", "reason": str(error)}))
        return 2
    rendered = json.dumps(evidence, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
