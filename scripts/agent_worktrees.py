"""Manage EMR4's multi-agent git worktree handoff flow."""

from __future__ import annotations

import argparse
import re
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
INBOX_ROOT = REPO_ROOT / "orchestration" / "agent_inbox"


TASK_TEMPLATE = """# {task_id}

| Item | Value |
|---|---|
| To | {agent} |
| Branch | `{branch}` |
| Status | queued |
| Created | {created} |
| Start Command | `python scripts\\agent_worktrees.py handin` |
| Submit Command | `python scripts\\agent_worktrees.py submit --agent {agent} --commit-message "{commit_message}" --message "{submit_message}"` |

## Mission

{mission}

## Scope

### In Scope

{in_scope}

### Out of Scope

{out_of_scope}

## Required Steps

1. Run the start command above.
2. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
3. Work only inside the stated scope unless the user or Codex expands it.
4. Do not merge to `master`.
5. Do not move `handoff/current`.
6. Run the verification listed below.
7. Finish with the submit command above.

## Verification

{verification}

## Merge Criteria

{merge_criteria}

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Fill this in before submit:

- Files changed:
- Verification run:
- Remaining risks:
"""


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


def print_result(result: subprocess.CompletedProcess[str]) -> None:
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        sys.stderr.write(result.stderr)


def require_clean(cwd: Path = REPO_ROOT) -> None:
    status = git_stdout(["status", "--porcelain"], cwd=cwd)
    if status:
        print("Working tree has uncommitted changes:")
        print(status)
        raise SystemExit("Commit, stash, or ignore local files before continuing.")


def commit_checkpoint(message: str, cwd: Path = REPO_ROOT) -> None:
    run_git(["add", "-A"], cwd=cwd)
    status = git_stdout(["status", "--porcelain"], cwd=cwd)
    if not status:
        print("[skip] No changes to commit.")
        return

    result = run_git(["commit", "-m", message], cwd=cwd)
    print_result(result)


def branch_exists(branch: str) -> bool:
    result = run_git(["show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], check=False)
    return result.returncode == 0


def push_handoff_refs(branch: str, remote: str) -> None:
    print(f"[push] {branch} -> {remote}/{branch}")
    print_result(run_git(["push", "-u", remote, branch]))

    print(f"[push] {HANDOFF_REF} -> {remote}/{HANDOFF_REF}")
    print_result(run_git(["push", remote, f"{HANDOFF_REF}:{HANDOFF_REF}"]))


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "task"


def inbox_dir(agent: str) -> Path:
    return INBOX_ROOT / agent


def task_files(agent: str | None = None) -> list[Path]:
    roots = [inbox_dir(agent)] if agent else [INBOX_ROOT / name for name in AGENTS]
    files: list[Path] = []
    for root in roots:
        if root.exists():
            files.extend(sorted(root.glob("*.md")))
    return files


def read_task_status(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| Status |"):
            parts = [part.strip() for part in line.split("|")]
            if len(parts) >= 4:
                return parts[2]
    return "unknown"


def update_task_status(path: Path, status_value: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.startswith("| Status |"):
            lines[idx] = f"| Status | {status_value} |"
            break
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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
    if args.commit_message:
        commit_checkpoint(args.commit_message)

    require_clean()

    head = git_stdout(["rev-parse", "--short", "HEAD"])
    branch = git_stdout(["branch", "--show-current"])
    if not branch:
        raise SystemExit("Cannot hand off from a detached HEAD. Check out an agent branch first.")

    run_git(["branch", "-f", HANDOFF_REF, "HEAD"])

    print(f"[ok] {HANDOFF_REF} now points to {head} from {branch}")
    if args.agent:
        print(f"[ok] outgoing agent: {args.agent}")
    if args.message:
        print(f"[note] {args.message}")

    if not args.no_push:
        push_handoff_refs(branch, args.remote)

    print()
    print("Next agent should run from its own worktree:")
    print(f"  python scripts\\agent_worktrees.py sync --fetch --ref {HANDOFF_REF}")


def submit(args: argparse.Namespace) -> None:
    if args.commit_message:
        commit_checkpoint(args.commit_message)

    require_clean()

    head = git_stdout(["rev-parse", "--short", "HEAD"])
    branch = git_stdout(["branch", "--show-current"])
    if not branch:
        raise SystemExit("Cannot submit from a detached HEAD. Check out an agent branch first.")
    if branch in {"master", HANDOFF_REF}:
        raise SystemExit("Parallel submit must come from an agent/workstream branch, not master or handoff/current.")

    print(f"[ok] submitting {branch} at {head}")
    if args.agent:
        print(f"[ok] submitting agent: {args.agent}")
    if args.message:
        print(f"[note] {args.message}")
    if not args.no_push:
        print(f"[push] {branch} -> {args.remote}/{branch}")
        print_result(run_git(["push", "-u", args.remote, branch]))
    print()
    print("Codex/orchestrator should review this branch before merging or moving the baton.")


def dispatch(args: argparse.Namespace) -> None:
    created = git_stdout(["rev-parse", "--short", "HEAD"])
    task_id = args.task_id or f"{args.agent}-{slugify(args.title)}"
    branch = args.branch or AGENTS[args.agent]
    commit_message = args.commit_message or args.title
    submit_message = args.submit_message or f"{task_id} ready for Codex review"

    target_dir = inbox_dir(args.agent)
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{task_id}.md"
    if path.exists() and not args.force:
        raise SystemExit(f"Task already exists: {path}. Use --force to overwrite.")

    task_text = TASK_TEMPLATE.format(
        task_id=task_id,
        agent=args.agent,
        branch=branch,
        created=created,
        commit_message=commit_message.replace('"', "'"),
        submit_message=submit_message.replace('"', "'"),
        mission=args.mission.strip(),
        in_scope=args.in_scope.strip(),
        out_of_scope=args.out_of_scope.strip(),
        verification=args.verification.strip(),
        merge_criteria=args.merge_criteria.strip(),
    )
    path.write_text(task_text, encoding="utf-8")
    print(f"[ok] dispatched {task_id} -> {path}")
    print(f"[next] {args.agent} should run: python scripts\\agent_worktrees.py brief --agent {args.agent}")


def inbox(args: argparse.Namespace) -> None:
    files = task_files(args.agent)
    if not files:
        print("[ok] inbox is empty")
        return
    for path in files:
        rel = path.relative_to(REPO_ROOT)
        print(f"{read_task_status(path):<12} {rel}")


def brief(args: argparse.Namespace) -> None:
    files = task_files(args.agent)
    if not files:
        print(f"[ok] no tasks for {args.agent}")
        return
    selected = files[0]
    if args.task:
        matches = [path for path in files if path.stem == args.task or path.name == args.task]
        if not matches:
            raise SystemExit(f"Task not found for {args.agent}: {args.task}")
        selected = matches[0]
    print(selected.read_text(encoding="utf-8"))


def claim(args: argparse.Namespace) -> None:
    files = task_files(args.agent)
    matches = [path for path in files if path.stem == args.task or path.name == args.task]
    if not matches:
        raise SystemExit(f"Task not found for {args.agent}: {args.task}")
    update_task_status(matches[0], args.status)
    print(f"[ok] {matches[0].relative_to(REPO_ROOT)} -> {args.status}")


def sync(args: argparse.Namespace) -> None:
    repo = Path.cwd().resolve()
    require_clean(repo)

    if args.fetch:
        print(f"[fetch] {args.remote}")
        print_result(run_git(["fetch", args.remote], cwd=repo))

    before = git_stdout(["rev-parse", "--short", "HEAD"], cwd=repo)
    run_git(["merge", "--ff-only", args.ref], cwd=repo)
    after = git_stdout(["rev-parse", "--short", "HEAD"], cwd=repo)

    if before == after:
        print(f"[ok] Already up to date at {after}")
    else:
        print(f"[ok] Fast-forwarded from {before} to {after}")


def handin(args: argparse.Namespace) -> None:
    args.fetch = True
    sync(args)


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

    handoff_parser = subparsers.add_parser("handoff", help="Commit/checkpoint if requested, move handoff/current, and push")
    handoff_parser.add_argument("--agent", choices=sorted(AGENTS))
    handoff_parser.add_argument("--message", default="")
    handoff_parser.add_argument("--commit-message", default="", help="Stage all non-ignored changes and commit before handoff")
    handoff_parser.add_argument("--remote", default="origin")
    handoff_parser.add_argument("--no-push", action="store_true", help="Do not push the current branch or handoff/current")
    handoff_parser.set_defaults(func=handoff)

    submit_parser = subparsers.add_parser("submit", help="Commit/checkpoint if requested and push current branch without moving the baton")
    submit_parser.add_argument("--agent", choices=sorted(AGENTS))
    submit_parser.add_argument("--message", default="")
    submit_parser.add_argument("--commit-message", default="", help="Stage all non-ignored changes and commit before submit")
    submit_parser.add_argument("--remote", default="origin")
    submit_parser.add_argument("--no-push", action="store_true", help="Do not push the current branch")
    submit_parser.set_defaults(func=submit)

    dispatch_parser = subparsers.add_parser("dispatch", help="Create an agent inbox task packet")
    dispatch_parser.add_argument("--agent", choices=sorted(AGENTS), required=True)
    dispatch_parser.add_argument("--title", required=True)
    dispatch_parser.add_argument("--mission", required=True)
    dispatch_parser.add_argument("--in-scope", required=True)
    dispatch_parser.add_argument("--out-of-scope", required=True)
    dispatch_parser.add_argument("--verification", required=True)
    dispatch_parser.add_argument("--merge-criteria", required=True)
    dispatch_parser.add_argument("--task-id", default="")
    dispatch_parser.add_argument("--branch", default="")
    dispatch_parser.add_argument("--commit-message", default="")
    dispatch_parser.add_argument("--submit-message", default="")
    dispatch_parser.add_argument("--force", action="store_true")
    dispatch_parser.set_defaults(func=dispatch)

    inbox_parser = subparsers.add_parser("inbox", help="List agent inbox task packets")
    inbox_parser.add_argument("--agent", choices=sorted(AGENTS))
    inbox_parser.set_defaults(func=inbox)

    brief_parser = subparsers.add_parser("brief", help="Print an agent task packet")
    brief_parser.add_argument("--agent", choices=sorted(AGENTS), required=True)
    brief_parser.add_argument("--task", default="")
    brief_parser.set_defaults(func=brief)

    claim_parser = subparsers.add_parser("claim", help="Update a task packet status")
    claim_parser.add_argument("--agent", choices=sorted(AGENTS), required=True)
    claim_parser.add_argument("--task", required=True)
    claim_parser.add_argument("--status", default="in_progress")
    claim_parser.set_defaults(func=claim)

    sync_parser = subparsers.add_parser("sync", help="Fast-forward current worktree to the handoff ref")
    sync_parser.add_argument("--ref", default=HANDOFF_REF)
    sync_parser.add_argument("--fetch", action="store_true", help="Fetch from the remote before merging the baton")
    sync_parser.add_argument("--remote", default="origin")
    sync_parser.set_defaults(func=sync)

    handin_parser = subparsers.add_parser("handin", help="Fetch and fast-forward current worktree to the handoff ref")
    handin_parser.add_argument("--ref", default=HANDOFF_REF)
    handin_parser.add_argument("--remote", default="origin")
    handin_parser.set_defaults(func=handin)

    status_parser = subparsers.add_parser("status", help="Show branch and worktree status")
    status_parser.set_defaults(func=status)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
