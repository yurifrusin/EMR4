"""Manage EMR4's multi-agent git worktree handoff flow."""

from __future__ import annotations

import argparse
from datetime import datetime
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
PROTOCOL_ALERTS_PATH = REPO_ROOT / "orchestration" / "protocol_alerts.md"
INTEGRATION_LOG_PATH = REPO_ROOT / "orchestration" / "integration_log.md"
SPRINT_CLOSEOUT_PATH = REPO_ROOT / "orchestration" / "sprint_closeout.md"
DURABLE_BRANCHES = {"master", HANDOFF_REF, *AGENTS.values()}


TASK_TEMPLATE = """# {task_id}

| Item | Value |
|---|---|
| To | {agent} |
| Branch | `{branch}` |
| Status | queued |
| Created | {created} |
| Start Command | `python scripts\\agent_worktrees.py handin --agent {agent}` |
| Plan Command | `python scripts\\agent_worktrees.py plan --agent {agent} --task {task_id} --summary "Short plan summary"` |
| Submit Command | `python scripts\\agent_worktrees.py submit --agent {agent} --task {task_id} --commit-message "{commit_message}" --message "{submit_message}"` |

## Mission

{mission}

## Scope

### In Scope

{in_scope}

### Out of Scope

{out_of_scope}

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Before editing project code, write an implementation plan and stop. The plan
   must be shown in the agent GUI and captured for Codex with the plan command
   above. Do not code until the user/Codex says `complete sprint task`.
5. After plan approval, work only inside the stated scope unless the user or Codex
   expands it.
6. Do not merge to `master`.
7. Do not move `handoff/current`.
8. Run the verification listed below.
9. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
10. Finish with the submit command above.

## Implementation Plan Requirements

Before coding, the implementation plan must include:

- My Understanding
- Intended Surface / Boundary
- Out of Scope
- Files I Expect To Edit
- Implementation Steps
- Visual / Behavioural Acceptance Checks
- Risks / Ambiguities

Pay special attention to visually loaded words such as cards, slots, stacking,
panels, waiting room, diary grid, booking slot, and status. State exactly which
surface is affected and which nearby surfaces must not change.

## Hard Stop Rules

- Do not push to `master` or `handoff/current`.
- Do not manually work around a failed protocol command (`handin`, `sync`, `submit`,
  `realign`, or related orchestration commands).
- Report every protocol-followed command back to Codex/orchestrator, whether it
  succeeds or fails. For success, include the command, working directory, branch,
  and short success result.
- If any protocol command refuses to run or fails, stop and report the exact command,
  working directory, branch, `git status --short --branch`, and error output to the
  orchestrator. On push failure, `submit` will also try to publish a
  `submit-alert/...` branch for Codex to poll.
- If these instructions conflict with remembered prior protocol, trust the current
  `handin` alerts and this task packet.

## Verification

{verification}

## Merge Criteria

{merge_criteria}

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
"""


PLAN_TEMPLATE = """# plan-{agent}-{task}

| Item | Value |
|---|---|
| To | codex |
| From | {agent} |
| Branch | `{branch}` |
| Source Task | `{task}` |
| Status | pending_plan_review |
| Created | {created} |
| Source HEAD | `{head}` |

## Plan Summary

{summary}

## My Understanding

{understanding}

## Intended Surface / Boundary

{surface}

## Out Of Scope

{out_of_scope}

## Files I Expect To Edit

{files}

## Implementation Steps

{steps}

## Visual / Behavioural Acceptance Checks

{acceptance}

## Risks / Ambiguities

{risks}

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
"""


def safe_path(path: Path) -> str:
    return path.resolve().as_posix()


def md_cell(value: str | None) -> str:
    text = str(value or "").replace("\n", " ").strip()
    return text.replace("|", "\\|")


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


def local_timestamp() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %z")


def ensure_integration_log(repo_root: Path = REPO_ROOT) -> Path:
    path = repo_root / "orchestration" / "integration_log.md"
    if path.exists():
        return path
    text = """# EMR4 Integration Log

This is the operational ledger for Codex-orchestrated submits, reviews, integrations,
and worker-worktree retirement decisions. It complements the task packets under
`orchestration/agent_inbox/`.

| When | Agent | Task | Branch | Submit/Review | Integration Commit | Result | Retire/Follow-up |
|---|---|---|---|---|---|---|---|
"""
    path.write_text(text, encoding="utf-8")
    return path


def append_integration_log(
    agent: str,
    task: str,
    branch: str,
    review: str,
    integration_commit: str,
    result: str,
    follow_up: str,
    repo_root: Path = REPO_ROOT,
) -> Path:
    path = ensure_integration_log(repo_root)
    row = (
        f"| {md_cell(local_timestamp())} | {md_cell(agent)} | {md_cell(task)} | "
        f"`{md_cell(branch)}` | {md_cell(review)} | `{md_cell(integration_commit)}` | "
        f"{md_cell(result)} | {md_cell(follow_up)} |\n"
    )
    with path.open("a", encoding="utf-8") as handle:
        handle.write(row)
    return path


def integration_log_records(repo_root: Path = REPO_ROOT) -> list[dict[str, str]]:
    path = repo_root / "orchestration" / "integration_log.md"
    if not path.exists():
        return []
    records: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or line.startswith("|---") or line.startswith("| When |"):
            continue
        parts = [part.strip().strip("`") for part in line.strip("|").split("|")]
        if len(parts) < 8:
            continue
        records.append(
            {
                "when": parts[0],
                "agent": parts[1],
                "task": parts[2],
                "branch": parts[3],
                "review": parts[4],
                "commit": parts[5],
                "result": parts[6],
                "follow_up": parts[7],
            }
        )
    return records


def integrated_branches(repo_root: Path = REPO_ROOT) -> set[str]:
    branches: set[str] = set()
    for record in integration_log_records(repo_root):
        if "integrated" in record["result"].lower() and record["branch"]:
            branches.add(record["branch"])
    return branches


def branch_is_ancestor(branch: str, target: str = "master", cwd: Path = REPO_ROOT) -> bool:
    return run_git(["merge-base", "--is-ancestor", branch, target], cwd=cwd, check=False).returncode == 0


def parse_worktrees(repo_root: Path = REPO_ROOT) -> list[dict[str, str]]:
    text = git_stdout(["worktree", "list", "--porcelain"], cwd=repo_root)
    worktrees: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            if current:
                worktrees.append(current)
                current = {}
            continue
        if line.startswith("worktree "):
            current["path"] = line.removeprefix("worktree ")
        elif line.startswith("HEAD "):
            current["head"] = line.removeprefix("HEAD ")
        elif line.startswith("branch "):
            current["branch"] = line.removeprefix("branch refs/heads/")
        elif line == "detached":
            current["branch"] = "(detached)"
    if current:
        worktrees.append(current)
    return worktrees


def worktree_dirty(path: Path) -> bool:
    return bool(git_stdout(["status", "--porcelain"], cwd=path, check=False))


def is_disposable_worktree(item: dict[str, str]) -> bool:
    branch = item.get("branch", "")
    path = item.get("path", "")
    if branch in DURABLE_BRANCHES:
        return False
    return branch.startswith("codex/") or "/.codex/worktrees/" in path.replace("\\", "/")


def stale_worktree_candidates(repo_root: Path = REPO_ROOT) -> list[dict[str, str]]:
    integrated = integrated_branches(repo_root)
    candidates: list[dict[str, str]] = []
    for item in parse_worktrees(repo_root):
        branch = item.get("branch", "")
        if not branch or not is_disposable_worktree(item):
            continue
        path = Path(item["path"])
        dirty = worktree_dirty(path)
        merged = branch_is_ancestor(branch, "master", cwd=repo_root)
        logged_integrated = branch in integrated
        if not (merged or logged_integrated or dirty):
            continue
        item = dict(item)
        item["dirty"] = "yes" if dirty else "no"
        item["merged"] = "yes" if merged else "no"
        item["logged_integrated"] = "yes" if logged_integrated else "no"
        if dirty:
            item["recommendation"] = "review dirty worktree before retiring"
        elif merged or logged_integrated:
            item["recommendation"] = "safe to remove worktree; preserve branch unless separately pruned"
        else:
            item["recommendation"] = "inspect"
        candidates.append(item)
    return candidates


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


def repo_root_for_cwd(cwd: Path | None = None) -> Path:
    """Return the git root for the active working directory."""
    root_cwd = (cwd or Path.cwd()).resolve()
    result = run_git(["rev-parse", "--show-toplevel"], cwd=root_cwd, check=False)
    if result.returncode != 0:
        return REPO_ROOT
    return Path(result.stdout.strip()).resolve()


def inbox_root(repo_root: Path = REPO_ROOT) -> Path:
    return repo_root / "orchestration" / "agent_inbox"


def inbox_dir(agent: str, repo_root: Path = REPO_ROOT) -> Path:
    return inbox_root(repo_root) / agent


def task_files(agent: str | None = None, repo_root: Path = REPO_ROOT) -> list[Path]:
    roots = [inbox_dir(agent, repo_root)] if agent else [inbox_root(repo_root) / name for name in AGENTS]
    files: list[Path] = []
    for root in roots:
        if root.exists():
            files.extend(sorted(root.glob("*.md")))
    return files


def read_task_status(path: Path) -> str:
    return read_status_from_text(path.read_text(encoding="utf-8"))


def read_status_from_text(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("| Status |"):
            parts = [part.strip() for part in line.split("|")]
            if len(parts) >= 4:
                return parts[2]
    return "unknown"


def is_actionable_status(status_value: str) -> bool:
    return status_value in {
        "queued",
        "pending_review",
        "pending_plan_review",
        "in_progress",
        "blocked",
        "suggested",
    }


def update_task_status(path: Path, status_value: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.startswith("| Status |"):
            lines[idx] = f"| Status | {status_value} |"
            break
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def agent_from_branch(cwd: Path = REPO_ROOT) -> str | None:
    branch = git_stdout(["branch", "--show-current"], cwd=cwd, check=False)
    for agent, agent_branch in AGENTS.items():
        if branch == agent_branch:
            return agent
    if branch == "master":
        return "codex"
    return None


def next_task_for(agent: str) -> Path | None:
    files = task_files(agent)
    for status_value in ("in_progress", "queued"):
        for path in files:
            if read_task_status(path) == status_value:
                return path
    return files[0] if files else None


def print_agent_brief(agent: str) -> None:
    print()
    print(f"[inbox] {agent}")
    files = task_files(agent)
    if not files:
        print("[ok] no tasks")
        return
    for path in files:
        print(f"{read_task_status(path):<12} {path.relative_to(REPO_ROOT)}")
    selected = next_task_for(agent)
    if selected:
        print()
        print(f"[brief] {selected.relative_to(REPO_ROOT)}")
        print(selected.read_text(encoding="utf-8"))


def print_protocol_alerts(repo_root: Path = REPO_ROOT) -> None:
    alerts_path = repo_root / "orchestration" / "protocol_alerts.md"
    if not alerts_path.exists():
        return
    text = alerts_path.read_text(encoding="utf-8").strip()
    if not text:
        return
    print()
    print("[protocol alerts]")
    print(text)


def append_completion_note(path: Path, summary: str) -> None:
    if not summary:
        return
    text = path.read_text(encoding="utf-8").rstrip()
    text += f"\n\nSubmitted summary:\n\n{summary.strip()}\n"
    path.write_text(text, encoding="utf-8")


def section_text(markdown: str, heading: str) -> str:
    pattern = re.compile(
        rf"^## {re.escape(heading)}\s*$([\s\S]*?)(?=^## |\Z)",
        re.MULTILINE,
    )
    match = pattern.search(markdown)
    return match.group(1).strip() if match else ""


def task_completion_notes(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    notes = section_text(text, "Completion Notes")
    placeholder_lines = {
        "Fill this in before submit:",
        "- Files changed:",
        "- Verification run:",
        "- Remaining risks:",
    }
    meaningful = [
        line for line in notes.splitlines()
        if line.strip() and line.strip() not in placeholder_lines
    ]
    return notes if meaningful else ""


def create_codex_review_packet(
    agent: str,
    task_id: str,
    branch: str,
    message: str,
    completion_notes: str = "",
    repo_root: Path = REPO_ROOT,
) -> Path:
    review_dir = inbox_dir("codex", repo_root)
    review_dir.mkdir(parents=True, exist_ok=True)
    review_id = f"review-{agent}-{task_id}"
    path = review_dir / f"{review_id}.md"
    text = f"""# {review_id}

| Item | Value |
|---|---|
| To | codex |
| From | {agent} |
| Branch | `{branch}` |
| Source Task | `{task_id}` |
| Status | queued |

## Review Request

{message or "Worker branch submitted for Codex review."}

## Worker Completion Notes

{completion_notes or "_No completion notes were supplied in the source task packet. Reviewer should inspect the branch and may ask the worker for a concise summary before integration._"}

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/{agent}/{task_id}.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
"""
    path.write_text(text, encoding="utf-8")
    return path


def create_codex_submit_alert_packet(
    agent: str | None,
    task_id: str | None,
    branch: str,
    head: str,
    command: str,
    result: subprocess.CompletedProcess[str],
    repo_root: Path,
) -> Path:
    alert_dir = inbox_dir("codex", repo_root)
    alert_dir.mkdir(parents=True, exist_ok=True)
    alert_id = f"submit-alert-{slugify(agent or 'unknown')}-{slugify(task_id or branch)}-{head}"
    path = alert_dir / f"{alert_id}.md"
    text = f"""# {alert_id}

| Item | Value |
|---|---|
| To | codex |
| From | {agent or "unknown"} |
| Branch | `{branch}` |
| Source Task | `{task_id or ""}` |
| Status | blocked |

## Submit Failure

The worker reached submit but the push failed. The worker must stop; Codex/orchestrator
should reconcile the branch.

## Details

- Working directory: `{repo_root}`
- Branch: `{branch}`
- Head: `{head}`
- Command: `{command}`
- Return code: `{result.returncode}`

## Stdout

```text
{(result.stdout or "").strip()}
```

## Stderr

```text
{(result.stderr or "").strip()}
```

## Required Review Steps

1. Fetch this alert branch.
2. Inspect the worker branch and this failure packet.
3. Reconcile with the remote branch from the Codex/orchestrator side.
4. Do not ask the worker to manually pull/rebase unless Codex explicitly chooses that path.
"""
    path.write_text(text, encoding="utf-8")
    return path


def publish_submit_alert(
    agent: str | None,
    task_id: str | None,
    branch: str,
    head: str,
    command: str,
    result: subprocess.CompletedProcess[str],
    remote: str,
    repo: Path,
) -> None:
    alert_path = create_codex_submit_alert_packet(agent, task_id, branch, head, command, result, repo)
    print(f"[blocked] wrote Codex submit alert: {alert_path.relative_to(repo)}")
    print_result(run_git(["add", str(alert_path.relative_to(repo))], cwd=repo, check=False))
    commit_result = run_git(
        ["commit", "-m", f"Report {agent or 'agent'} submit failure"],
        cwd=repo,
        check=False,
    )
    print_result(commit_result)
    if commit_result.returncode != 0:
        print("[blocked] could not commit submit alert; report the alert path and push failure manually.")
        return

    alert_head = git_stdout(["rev-parse", "--short", "HEAD"], cwd=repo, check=False) or head
    alert_branch = f"submit-alert/{slugify(agent or 'unknown')}/{slugify(task_id or branch)}/{alert_head}"
    print(f"[push] alert -> {remote}/{alert_branch}")
    alert_push = run_git(["push", remote, f"HEAD:{alert_branch}"], cwd=repo, check=False)
    print_result(alert_push)
    if alert_push.returncode == 0:
        print(f"[blocked] submit alert published on {alert_branch}")
    else:
        print("[blocked] failed to publish submit alert branch; report the output above manually.")


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
    repo = repo_root_for_cwd()
    branch = git_stdout(["branch", "--show-current"], cwd=repo)
    if not branch:
        raise SystemExit("Cannot submit from a detached HEAD. Check out an agent branch first.")
    if branch in {"master", HANDOFF_REF}:
        raise SystemExit("Parallel submit must come from an agent/workstream branch, not master or handoff/current.")

    if args.task and args.agent:
        matches = [
            path for path in task_files(args.agent, repo)
            if path.stem == args.task or path.name == args.task
        ]
        if not matches:
            raise SystemExit(f"Task not found for {args.agent}: {args.task}")
        update_task_status(matches[0], "submitted")
        append_completion_note(matches[0], args.summary)
        completion_notes = task_completion_notes(matches[0])
        review_path = create_codex_review_packet(
            args.agent,
            matches[0].stem,
            branch,
            args.message,
            completion_notes,
            repo,
        )
        print(f"[ok] wrote Codex review packet: {review_path.relative_to(repo)}")

    if args.commit_message:
        commit_checkpoint(args.commit_message, cwd=repo)

    require_clean(repo)

    head = git_stdout(["rev-parse", "--short", "HEAD"], cwd=repo)
    print(f"[ok] submitting {branch} at {head}")
    if args.agent:
        print(f"[ok] submitting agent: {args.agent}")
    if args.message:
        print(f"[note] {args.message}")
    if not args.no_push:
        print(f"[push] {branch} -> {args.remote}/{branch}")
        push_cmd = ["push", "-u", args.remote, branch]
        push_result = run_git(push_cmd, cwd=repo, check=False)
        print_result(push_result)
        if push_result.returncode != 0:
            publish_submit_alert(
                args.agent,
                args.task,
                branch,
                head,
                "git " + " ".join(push_cmd),
                push_result,
                args.remote,
                repo,
            )
            raise SystemExit(push_result.returncode)
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


def suggest_task(args: argparse.Namespace) -> None:
    repo = repo_root_for_cwd(Path.cwd().resolve())
    created = local_timestamp()
    head = git_stdout(["rev-parse", "--short", "HEAD"], cwd=repo)
    branch = git_stdout(["branch", "--show-current"], cwd=repo, check=False) or "(detached)"
    task_id = args.task_id or f"suggestion-{args.agent}-{slugify(args.title)}"

    target_dir = inbox_dir("codex", repo)
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{task_id}.md"
    if path.exists() and not args.force:
        raise SystemExit(f"Suggestion already exists: {path}. Use --force to overwrite.")

    suggestion_text = f"""# {task_id}

| Item | Value |
|---|---|
| To | codex |
| From | {args.agent} |
| Branch | `{branch}` |
| Status | suggested |
| Created | {created} |
| Source HEAD | `{head}` |

## Suggested Task

{args.title.strip()}

## Rationale / Evidence

{args.rationale.strip() or "Not supplied."}

## Proposed Scope

{args.scope.strip() or "Not supplied."}

## Suggested Verification

{args.verification.strip() or "Not supplied."}

## Notes / Risks

{args.notes.strip() or "Not supplied."}

## Codex Triage Notes

_Codex/orchestrator to fill in: accepted, deferred, merged into an active sprint, or rejected._
"""
    path.write_text(suggestion_text, encoding="utf-8")
    print(f"[ok] wrote Codex suggested-task packet: {path.relative_to(repo)}")
    print("[next] Submit or push this packet through the normal protocol so Codex can poll it.")
    print("[note] A suggestion is not authorization to implement; Codex/orchestrator must triage it.")


def submit_plan(args: argparse.Namespace) -> None:
    repo = repo_root_for_cwd(Path.cwd().resolve())
    created = local_timestamp()
    head = git_stdout(["rev-parse", "--short", "HEAD"], cwd=repo)
    branch = git_stdout(["branch", "--show-current"], cwd=repo, check=False) or "(detached)"
    task_id = args.task
    plan_id = args.plan_id or f"plan-{args.agent}-{task_id}"

    source_task = inbox_dir(args.agent, repo) / f"{task_id}.md"
    if not source_task.exists():
        raise SystemExit(f"Source task not found: {source_task.relative_to(repo)}")

    target_dir = inbox_dir("codex", repo)
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{plan_id}.md"
    if path.exists() and not args.force:
        raise SystemExit(f"Plan already exists: {path.relative_to(repo)}. Use --force to overwrite.")

    plan_text = PLAN_TEMPLATE.format(
        agent=args.agent,
        task=task_id,
        branch=branch,
        created=created,
        head=head,
        summary=args.summary.strip() or "Not supplied.",
        understanding=args.understanding.strip() or "Not supplied.",
        surface=args.surface.strip() or "Not supplied.",
        out_of_scope=args.out_of_scope.strip() or "Not supplied.",
        files=args.files.strip() or "Not supplied.",
        steps=args.steps.strip() or "Not supplied.",
        acceptance=args.acceptance.strip() or "Not supplied.",
        risks=args.risks.strip() or "Not supplied.",
    )
    path.write_text(plan_text, encoding="utf-8")
    update_task_status(source_task, "pending_plan_review")
    print(f"[ok] wrote Codex implementation-plan packet: {path.relative_to(repo)}")
    print(f"[ok] {source_task.relative_to(repo)} -> pending_plan_review")
    print("[next] Stop coding. Show the same plan in the GUI and wait for 'complete sprint task'.")


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
    selected = next_task_for(args.agent) or files[0]
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


def realign(args: argparse.Namespace) -> None:
    repo = Path.cwd().resolve()
    require_clean(repo)

    expected_branch = AGENTS[args.agent]
    branch = git_stdout(["branch", "--show-current"], cwd=repo)
    if branch != expected_branch:
        raise SystemExit(
            f"Refusing to realign {branch or '(detached HEAD)'} as {args.agent}; "
            f"expected branch {expected_branch}."
        )

    print(f"[fetch] {args.remote}")
    print_result(run_git(["fetch", args.remote], cwd=repo))

    target = f"{args.remote}/{args.ref}"
    before = git_stdout(["rev-parse", "--short", "HEAD"], cwd=repo)
    target_head = git_stdout(["rev-parse", "--short", target], cwd=repo)

    if not args.apply:
        print(f"[dry-run] would reset clean {expected_branch} from {before} to {target_head} ({target})")
        if not args.no_push:
            print(f"[dry-run] would push {expected_branch} -> {args.remote}/{expected_branch} with --force-with-lease")
        print("Re-run with --apply after Codex has integrated the submitted task.")
        return

    print_result(run_git(["reset", "--hard", target], cwd=repo))
    after = git_stdout(["rev-parse", "--short", "HEAD"], cwd=repo)
    print(f"[ok] realigned clean {expected_branch} from {before} to {after} ({target})")
    if not args.no_push:
        print(f"[push] {expected_branch} -> {args.remote}/{expected_branch} (--force-with-lease)")
        print_result(run_git(["push", "--force-with-lease", args.remote, f"HEAD:{expected_branch}"], cwd=repo))


def handin(args: argparse.Namespace) -> None:
    args.fetch = True
    sync(args)
    if args.no_brief:
        return
    print_protocol_alerts(repo_root_for_cwd(Path.cwd().resolve()))
    agent = args.agent or agent_from_branch(Path.cwd().resolve())
    if agent:
        print_agent_brief(agent)
    else:
        print("[hint] Could not infer agent from current branch. Use --agent claude, --agent antigravity, or --agent codex.")


def status(_: argparse.Namespace) -> None:
    print(git_stdout(["status", "--short", "--branch"]))
    print()
    print(git_stdout(["worktree", "list"]))


def print_task_summary(repo_root: Path = REPO_ROOT) -> None:
    files = task_files(repo_root=repo_root)
    if not files:
        print("[tasks] none")
        return
    print("[tasks]")
    for path in files:
        print(f"{read_task_status(path):<12} {path.relative_to(repo_root)}")


def print_integration_log_tail(limit: int = 8, repo_root: Path = REPO_ROOT) -> None:
    records = integration_log_records(repo_root)
    if not records:
        print("[integration log] no records yet")
        return
    print(f"[integration log] last {min(limit, len(records))}")
    for record in records[-limit:]:
        print(
            f"{record['when']}  {record['agent']:<11} {record['task']:<45} "
            f"{record['commit']:<8} {record['result']}"
        )


def print_stale_worktrees(repo_root: Path = REPO_ROOT) -> list[dict[str, str]]:
    candidates = stale_worktree_candidates(repo_root)
    if not candidates:
        print("[stale worktrees] none")
        return []
    print("[stale worktrees]")
    for item in candidates:
        print(
            f"{item.get('branch', ''):<28} dirty={item['dirty']:<3} "
            f"merged={item['merged']:<3} logged={item['logged_integrated']:<3} "
            f"{item.get('path', '')}"
        )
        print(f"  -> {item['recommendation']}")
    return candidates


def audit(args: argparse.Namespace) -> None:
    if args.fetch:
        print(f"[fetch] {args.remote}")
        print_result(run_git(["fetch", args.remote]))

    print("[refs]")
    for ref in ["master", HANDOFF_REF, *AGENTS.values()]:
        result = run_git(["rev-parse", "--short", ref], check=False)
        value = result.stdout.strip() if result.returncode == 0 else "missing"
        print(f"{ref:<22} {value}")

    print()
    print("[worktrees]")
    for item in parse_worktrees():
        path = Path(item.get("path", ""))
        dirty = "dirty" if path.exists() and worktree_dirty(path) else "clean"
        branch = item.get("branch", "(unknown)")
        head = item.get("head", "")[:8]
        print(f"{branch:<28} {head:<8} {dirty:<5} {item.get('path', '')}")

    print()
    print_task_summary()
    print()
    print_integration_log_tail(args.limit)
    print()
    print_stale_worktrees()


def record_integration(args: argparse.Namespace) -> None:
    commit_ref = args.integration_commit or "HEAD"
    resolved = git_stdout(["rev-parse", "--short", commit_ref], check=False)
    commit = resolved or commit_ref
    path = append_integration_log(
        agent=args.agent,
        task=args.task,
        branch=args.branch,
        review=args.review,
        integration_commit=commit,
        result=args.result,
        follow_up=args.follow_up,
    )
    print(f"[ok] wrote {path.relative_to(REPO_ROOT)}")


def retire_stale(args: argparse.Namespace) -> None:
    candidates = stale_worktree_candidates()
    if not candidates:
        print("[ok] no stale disposable worktrees found")
        return

    removable = [item for item in candidates if item["dirty"] == "no"]
    blocked = [item for item in candidates if item["dirty"] == "yes"]

    if blocked:
        print("[blocked: dirty worktrees]")
        for item in blocked:
            print(f"{item.get('branch', ''):<28} {item.get('path', '')}")

    if not removable:
        print("[ok] no clean stale disposable worktrees to retire")
        return

    action = "remove" if args.apply else "would remove"
    print(f"[{action}]")
    for item in removable:
        print(f"{item.get('branch', ''):<28} {item.get('path', '')}")
        if args.apply:
            print_result(run_git(["worktree", "remove", item["path"]]))

    if not args.apply:
        print()
        print("Dry run only. Re-run with --apply to remove the clean stale worktree directories.")


def closeout(_: argparse.Namespace) -> None:
    if not SPRINT_CLOSEOUT_PATH.exists():
        print("[missing] orchestration/sprint_closeout.md")
        return
    print(SPRINT_CLOSEOUT_PATH.read_text(encoding="utf-8"))


def poll(args: argparse.Namespace) -> None:
    if args.fetch:
        print(f"[fetch] {args.remote}")
        print_result(run_git(["fetch", args.remote]))

    found = False
    branch_checks = [
        (agent, branch)
        for agent, branch in AGENTS.items()
        if agent != "codex"
    ]

    codex_worker_refs = git_stdout(
        [
            "for-each-ref",
            f"refs/remotes/{args.remote}/codex",
            "--format=%(refname:short)",
        ],
        check=False,
    )
    for remote_branch in codex_worker_refs.splitlines():
        branch = remote_branch.removeprefix(f"{args.remote}/")
        if branch and branch != AGENTS["codex"]:
            branch_checks.append(("codex", branch))

    alert_refs = git_stdout(
        [
            "for-each-ref",
            f"refs/remotes/{args.remote}/submit-alert",
            "--format=%(refname:short)",
        ],
        check=False,
    )
    for remote_branch in alert_refs.splitlines():
        branch = remote_branch.removeprefix(f"{args.remote}/")
        if branch:
            branch_checks.append(("alert", branch))

    seen_refs: set[str] = set()
    for agent, branch in branch_checks:
        remote_ref = f"{args.remote}/{branch}"
        if remote_ref in seen_refs:
            continue
        seen_refs.add(remote_ref)
        if run_git(["rev-parse", "--verify", remote_ref], check=False).returncode != 0:
            continue

        log = git_stdout(["log", "--oneline", f"master..{remote_ref}"], check=False)
        review_files = git_stdout(
            ["ls-tree", "-r", "--name-only", remote_ref, "orchestration/agent_inbox/codex"],
            check=False,
        )
        actionable_reviews: list[tuple[str, str]] = []
        for file_path in review_files.splitlines():
            if not file_path.endswith(".md"):
                continue
            packet = git_stdout(["show", f"{remote_ref}:{file_path}"], check=False)
            from_matches = agent == "alert" or f"| From | {agent} |" in packet
            if is_actionable_status(read_status_from_text(packet)) and from_matches:
                actionable_reviews.append((file_path, packet))

        if log or actionable_reviews:
            found = True
            label = "submit alert" if agent == "alert" else "submitted"
            print(f"\n[{label}] {agent} branch {remote_ref}")
            if log:
                print(log)
            for file_path, packet in actionable_reviews:
                print(f"\n[review packet] {remote_ref}:{file_path}")
                print(packet)

    codex_files = [path for path in task_files("codex") if is_actionable_status(read_task_status(path))]
    if codex_files:
        found = True
        print("\n[codex local inbox]")
        for path in codex_files:
            print(f"{read_task_status(path):<12} {path.relative_to(REPO_ROOT)}")

    if not found:
        print("[ok] no submitted worker branches or Codex inbox packets found")

    candidates = stale_worktree_candidates()
    if candidates:
        print()
        print("[note] stale disposable worktrees detected; run:")
        print("  python scripts\\agent_worktrees.py audit")
        print("  python scripts\\agent_worktrees.py retire-stale")


def build_parser() -> argparse.ArgumentParser:
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
    submit_parser.add_argument("--task", default="", help="Source inbox task id; marks task submitted and writes a Codex review packet")
    submit_parser.add_argument("--message", default="")
    submit_parser.add_argument("--summary", default="", help="Completion summary appended to the source task packet")
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

    suggest_parser = subparsers.add_parser("suggest-task", help="Write a Codex inbox packet for a worker-suggested follow-up")
    suggest_parser.add_argument("--agent", choices=sorted(AGENTS), required=True)
    suggest_parser.add_argument("--title", required=True)
    suggest_parser.add_argument("--rationale", default="")
    suggest_parser.add_argument("--scope", default="")
    suggest_parser.add_argument("--verification", default="")
    suggest_parser.add_argument("--notes", default="")
    suggest_parser.add_argument("--task-id", default="")
    suggest_parser.add_argument("--force", action="store_true")
    suggest_parser.set_defaults(func=suggest_task)

    plan_parser = subparsers.add_parser("plan", help="Write a Codex inbox implementation plan before coding a task")
    plan_parser.add_argument("--agent", choices=sorted(AGENTS), required=True)
    plan_parser.add_argument("--task", required=True)
    plan_parser.add_argument("--summary", default="")
    plan_parser.add_argument("--understanding", default="")
    plan_parser.add_argument("--surface", default="")
    plan_parser.add_argument("--out-of-scope", default="")
    plan_parser.add_argument("--files", default="")
    plan_parser.add_argument("--steps", default="")
    plan_parser.add_argument("--acceptance", default="")
    plan_parser.add_argument("--risks", default="")
    plan_parser.add_argument("--plan-id", default="")
    plan_parser.add_argument("--force", action="store_true")
    plan_parser.set_defaults(func=submit_plan)

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

    realign_parser = subparsers.add_parser(
        "realign",
        help="After Codex integration, reset a clean durable agent worktree to the remote handoff ref",
    )
    realign_parser.add_argument("--agent", choices=sorted(AGENTS), required=True)
    realign_parser.add_argument("--ref", default=HANDOFF_REF)
    realign_parser.add_argument("--remote", default="origin")
    realign_parser.add_argument("--apply", action="store_true", help="Actually reset the clean worktree")
    realign_parser.add_argument("--no-push", action="store_true", help="Do not update the remote durable mirror branch")
    realign_parser.set_defaults(func=realign)

    handin_parser = subparsers.add_parser("handin", help="Fetch and fast-forward current worktree to the handoff ref")
    handin_parser.add_argument("--ref", default=HANDOFF_REF)
    handin_parser.add_argument("--remote", default="origin")
    handin_parser.add_argument("--agent", choices=sorted(AGENTS))
    handin_parser.add_argument("--no-brief", action="store_true", help="Only sync; do not print the inferred agent inbox task")
    handin_parser.set_defaults(func=handin)

    poll_parser = subparsers.add_parser("poll", help="Fetch and report submitted worker branches / Codex review packets")
    poll_parser.add_argument("--remote", default="origin")
    poll_parser.add_argument("--fetch", action="store_true")
    poll_parser.set_defaults(func=poll)

    audit_parser = subparsers.add_parser("audit", help="Show orchestration refs, tasks, integration log, and stale worker worktrees")
    audit_parser.add_argument("--remote", default="origin")
    audit_parser.add_argument("--fetch", action="store_true")
    audit_parser.add_argument("--limit", type=int, default=8, help="Number of integration-log rows to show")
    audit_parser.set_defaults(func=audit)

    record_parser = subparsers.add_parser("record-integration", help="Append a reviewed submit/integration to the integration ledger")
    record_parser.add_argument("--agent", choices=sorted(AGENTS), required=True)
    record_parser.add_argument("--task", required=True)
    record_parser.add_argument("--branch", required=True)
    record_parser.add_argument("--review", default="")
    record_parser.add_argument("--integration-commit", default="")
    record_parser.add_argument("--result", default="integrated")
    record_parser.add_argument("--follow-up", default="")
    record_parser.set_defaults(func=record_integration)

    retire_parser = subparsers.add_parser("retire-stale", help="Dry-run removal of clean stale disposable worker worktrees")
    retire_parser.add_argument("--apply", action="store_true", help="Actually remove clean stale disposable worktree directories")
    retire_parser.set_defaults(func=retire_stale)

    closeout_parser = subparsers.add_parser("closeout", help="Print the latest user review checklist and next recommendation")
    closeout_parser.set_defaults(func=closeout)

    status_parser = subparsers.add_parser("status", help="Show branch and worktree status")
    status_parser.set_defaults(func=status)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
