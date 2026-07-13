"""Run a bounded Gemini worker in an explicitly bound Antigravity project."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


MODELS = {
    "Gemini 3.5 Flash (Low)",
    "Gemini 3.5 Flash (Medium)",
    "Gemini 3.5 Flash (High)",
}
PROTECTED_BRANCHES = {"master", "handoff/current"}


@dataclass(frozen=True)
class WorktreeState:
    root: Path
    branch: str
    head: str
    dirty: bool


def _git(cwd: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8"
    )
    if completed.returncode != 0:
        raise ValueError(f"git {' '.join(args)} failed: {completed.stderr.strip()}")
    return completed.stdout.strip()


def inspect_worktree(cwd: Path, *, require_clean: bool) -> WorktreeState:
    resolved = cwd.resolve()
    if not resolved.is_dir():
        raise ValueError("Antigravity cwd must be an existing directory")
    root = Path(_git(resolved, "rev-parse", "--show-toplevel")).resolve()
    if root != resolved:
        raise ValueError(f"Antigravity cwd must equal the Git worktree root: {root}")
    branch = _git(resolved, "branch", "--show-current")
    if not branch or branch in PROTECTED_BRANCHES:
        raise ValueError(f"Antigravity refuses protected or detached branch: {branch!r}")
    dirty = bool(_git(resolved, "status", "--porcelain"))
    if require_clean and dirty:
        raise ValueError("Antigravity worktree must be clean before dispatch")
    return WorktreeState(
        root=root,
        branch=branch,
        head=_git(resolved, "rev-parse", "HEAD"),
        dirty=dirty,
    )


def build_command(
    *, packet: str, state: WorktreeState, model: str, os_sandbox: bool
) -> list[str]:
    if model not in MODELS:
        raise ValueError(f"unsupported Antigravity model: {model}")
    bound_packet = (
        f"BOUND WORKTREE: {state.root}\n"
        f"BOUND BRANCH: {state.branch}\n"
        "Use only this worktree. First verify the exact root and branch. "
        "Do not inspect or reuse any historical Antigravity project.\n\n"
        f"{packet}"
    )
    command = [
        "agy",
        "-p",
        bound_packet,
        "--new-project",
        "--add-dir",
        str(state.root),
        "--model",
        model,
        "--mode",
        "accept-edits",
        "--dangerously-skip-permissions",
        "--print-timeout",
        "30m",
    ]
    if os_sandbox:
        command.append("--sandbox")
    return command


def run_worker(
    *,
    packet_path: Path,
    cwd: Path,
    output_path: Path,
    model: str,
    os_sandbox: bool,
) -> dict:
    packet = packet_path.read_text(encoding="utf-8")
    if not packet.strip():
        raise ValueError("worker packet must not be empty")
    before = inspect_worktree(cwd, require_clean=True)
    completed = subprocess.run(
        build_command(packet=packet, state=before, model=model, os_sandbox=os_sandbox),
        cwd=before.root,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"Antigravity transport failed ({completed.returncode}): "
            f"{completed.stderr.strip()}"
        )
    after = inspect_worktree(before.root, require_clean=False)
    if after.root != before.root or after.branch != before.branch:
        raise RuntimeError("Antigravity changed or escaped its bound worktree/branch")
    receipt = {
        "schema_version": "ariadne.worker_receipt.v1",
        "status": "completed",
        "transport": "antigravity_new_project_bound_worktree",
        "model": model,
        "worktree": str(before.root),
        "branch": before.branch,
        "head_before": before.head,
        "head_after": after.head,
        "dirty_after": after.dirty,
        "os_sandbox": os_sandbox,
        "result": completed.stdout.strip(),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a worktree-bound Gemini worker.")
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--cwd", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", choices=sorted(MODELS), default="Gemini 3.5 Flash (Medium)")
    parser.add_argument(
        "--os-sandbox",
        action="store_true",
        help="Enable agy OS sandboxing; Windows may request elevation.",
    )
    args = parser.parse_args()
    try:
        receipt = run_worker(
            packet_path=args.packet.resolve(),
            cwd=args.cwd.resolve(),
            output_path=args.output.resolve(),
            model=args.model,
            os_sandbox=args.os_sandbox,
        )
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Antigravity transport failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps({key: receipt[key] for key in ("status", "transport", "model")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
