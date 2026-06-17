"""Manage EMR4's multi-agent git worktree handoff flow."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKTREE_ROOT = REPO_ROOT.parent / "EMR4-worktrees"
AGENTS = {
    "codex": "codex/current",
    "claude": "claude/current",
    "antigravity": "antigravity/current",
}
HANDOFF_REF = "handoff/current"


def safe_path(path: Path) -> str:
    return path.resolve().as_posix()


def run_git(args: list[str], cwd: Path = REPO_ROOT, check: bool = True) -> subprocess.CompletedProcess[str]:
    cmd = ["git", "-c", f"safe.directory={safe_path(cwd)}", "-c", "core.excludesFile=", *args]
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if check and result.returncode != 0:
        sys.stderr.write(result.stdout)
        sys.stderr.write(result.stderr)
        raise SystemExit(result.returncode)
    return result


def git_stdout(args: list[str], cwd: Path = REPO_ROOT, check: bool = True) -> str:
    result = run_git(args, cwd=cwd, check=check)
    if result.stderr:
        sys.stderr.write(result.stderr)
    return result.stdout.strip()


def require_clean(cwd: Path = REPO_ROOT) -> None:
    status = git_stdout(["status", "--porcelain"], cwd=cwd)
    if status:
        print("Working tree has uncommitted changes:")
        print(status)
        raise SystemExit("Commit, stash, or ignore local files before continuing.")


def branch_exists(branch: str) -> bool:
    result = run_git(["show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], check=False)
    return result.returncode == 0


def setup(args: argparse.Namespace) -> None:
    require_clean()

    worktree_root = Path(args.worktree_root).resolve()
    worktree_root.mkdir(parents=True, exist_ok=True)

    existing = git_stdout(["worktree", "list", "--porcelain"])

    for agent, branch in AGENTS.items():
        path = worktree_root / agent
        if str(path) in existing or path.as_posix() in existing:
            print(f"[skip] {agent} worktree already exists at {path}")
            continue

        if branch_exists(branch):
            run_git(["worktree", "add", str(path), branch])
        else:
            run_git(["worktree", "add", "-b", branch, str(path), args.start_ref])
        print(f"[ok] {agent} worktree: {path} on {branch}")

    if branch_exists(HANDOFF_REF):
        print(f"[skip] {HANDOFF_REF} already exists")
    else:
        run_git(["branch", HANDOFF_REF, args.start_ref])
        print(f"[ok] created {HANDOFF_REF} from {args.start_ref}")

    print()
    print(f"Agent worktrees are ready under {worktree_root}")


def handoff(args: argparse.Namespace) -> None:
    require_clean()

    head = git_stdout(["rev-parse", "--short", "HEAD"])
    branch = git_stdout(["branch", "--show-current"])
    run_git(["branch", "-f", HANDOFF_REF, "HEAD"])

    print(f"[ok] {HANDOFF_REF} now points to {head} from {branch}")
    if args.agent:
        print(f"[ok] outgoing agent: {args.agent}")
    if args.message:
        print(f"[note] {args.message}")
    print()
    print("Next agent should run from its own worktree:")
    print(f"  python scripts\\agent_worktrees.py sync --ref {HANDOFF_REF}")


def sync(args: argparse.Namespace) -> None:
    repo = Path.cwd().resolve()
    require_clean(repo)

    before = git_stdout(["rev-parse", "--short", "HEAD"], cwd=repo)
    run_git(["merge", "--ff-only", args.ref], cwd=repo)
    after = git_stdout(["rev-parse", "--short", "HEAD"], cwd=repo)

    if before == after:
        print(f"[ok] Already up to date at {after}")
    else:
        print(f"[ok] Fast-forwarded from {before} to {after}")


def status(_: argparse.Namespace) -> None:
    print(git_stdout(["status", "--short", "--branch"]))
    print()
    print(git_stdout(["worktree", "list"]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    setup_parser = subparsers.add_parser("setup", help="Create agent worktrees and the handoff ref")
    setup_parser.add_argument("--worktree-root", default=str(DEFAULT_WORKTREE_ROOT))
    setup_parser.add_argument("--start-ref", default="master")
    setup_parser.set_defaults(func=setup)

    handoff_parser = subparsers.add_parser("handoff", help="Move handoff/current to HEAD")
    handoff_parser.add_argument("--agent", choices=sorted(AGENTS))
    handoff_parser.add_argument("--message", default="")
    handoff_parser.set_defaults(func=handoff)

    sync_parser = subparsers.add_parser("sync", help="Fast-forward current worktree to the handoff ref")
    sync_parser.add_argument("--ref", default=HANDOFF_REF)
    sync_parser.set_defaults(func=sync)

    status_parser = subparsers.add_parser("status", help="Show branch and worktree status")
    status_parser.set_defaults(func=status)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
