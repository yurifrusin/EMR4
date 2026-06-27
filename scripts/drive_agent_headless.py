#!/usr/bin/env python3
"""
drive_agent_headless.py — orchestrator-callable headless driver for worker agents.

DRAFT (orchestration side-track, 2026-06-25): authored by the Claude worker at
Yuri's request, as part of migrating multi-agent orchestration OFF Computer-Use
GUI prompting and ONTO cheap text/CLI invocation. This is a PROPOSAL for
Codex/Ariadne to review and own. Before wiring it into the live loop, Ariadne
should ratify:
  * the permission posture (DEFAULT_ALLOWED_TOOLS / --bypass below),
  * where per-sprint session ids are minted and stored,
  * logging, error handling, and retry policy.

It is intentionally a STANDALONE script (not a subcommand of agent_worktrees.py)
so it carries ZERO blast radius on the live protocol commands
(handin / submit / poll / realign). Codex may fold it into agent_worktrees.py
later if that is preferred.

What it does
------------
Runs a single non-interactive `claude -p` turn inside a worker's git worktree and
prints the raw result JSON to stdout for the orchestrator to parse. No
screenshots, no perception loop — the whole exchange is text. This is the cheap
replacement for "Ariadne drives Computer Use to type a prompt into the GUI and
screenshots the result back".

The plan-gate maps cleanly onto process boundaries:
  * Step 1 (plan):  drive ... --session-id <uuid> \
                        --prompt "handin, write the implementation plan, submit the
                                  plan packet, then stop"
  * Step 2 (implement, ONLY after the user/Codex approves):
                    drive ... --phase implement \
                        --prompt "handin, then complete sprint task"
The "stop and wait" is enforced by the orchestrator simply not issuing step 2
until the plan is approved — the process exit IS the stop.

Cost note: a cold session auto-loads CLAUDE.md (@-includes the large AGENTS.md),
~27k tokens of cache-creation per cold start — bounded and acceptable. Do NOT use
--bare to trim it: --bare disables OAuth/keychain reading and forces
ANTHROPIC_API_KEY, so it 401s under subscription/setup-token auth.

Model / effort policy
---------------------
Use --phase to apply the plan-gate split (the model choice is the main lever;
effort is second-order):
  * --phase plan      -> Opus / medium effort   (high-leverage reasoning)
  * --phase implement -> Sonnet / medium effort (executes an already-approved plan)
Explicit --model / --effort override the phase defaults. Because the two phases
use DIFFERENT models, run a FRESH session per phase (do NOT --resume across the
gate): step 2 re-runs handin to reload the packet and implements against the
approved plan already persisted in the inbox/git. --resume remains useful for
multi-turn work WITHIN a single phase/model.

Usage
-----
  python scripts/drive_agent_headless.py --cwd <worktree> --prompt "..." \
         --phase {plan|implement} [--session-id UUID | --resume UUID] [--max-budget-usd N]
  add --dry-run to print the exact `claude` argv WITHOUT executing (auditable,
  and runnable from any environment because it never calls the API).

Safety posture: this script is for Claude worker branches only. By default it
refuses to run outside `claude/*` branches, refuses dirty starting trees, and
refuses bypassPermissions. Use the override flags only for explicit, reviewed
orchestration/debugging cases.

Exit code: 0 if the turn completed with is_error == false, 1 otherwise.

Environment requirement: invoke this from a CLEAN shell — NOT nested inside
another Claude Code tool call. A nested Claude Code session exports per-session
auth/routing overrides (e.g. a custom ANTHROPIC_BASE_URL) that a child `claude -p`
inherits and that cause a spurious 401. Ariadne's normal shell is clean, so this
only matters for local hand-testing.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import uuid as _uuid
from pathlib import Path

# ── Permission posture — RATIFY BEFORE PRODUCTION USE ────────────────────────
# A headless worker must never block on a permission prompt (nobody answers it).
# We allowlist exactly what a sprint worker needs — git / python / pytest /
# alembic and the protocol script (Bash), plus the file tools — and auto-accept
# edits. Chrome / Computer-Use tools are deliberately NOT enabled. This is broad
# Bash on a dev worktree with dummy data; Codex/Ariadne should confirm that is an
# acceptable trade for unattended operation, or tighten to granular Bash(...) rules.
DEFAULT_ALLOWED_TOOLS = ["Bash", "Edit", "Write", "Read", "Grep", "Glob"]

# ── Per-phase model + reasoning-effort policy — RATIFY ───────────────────────
# The plan-gate seam: planning is high-leverage reasoning (Opus); implementation
# executes a detailed, already-approved plan (Sonnet). The model split is the main
# lever; effort is second-order. Explicit --model / --effort override these.
PHASE_DEFAULTS = {
    "plan":      {"model": "opus",   "effort": "medium"},
    "implement": {"model": "sonnet", "effort": "medium"},
}

ALLOWED_BRANCH_PREFIXES = ("claude/",)


def find_claude_bin() -> str | None:
    """Find Claude Code even when Codex Desktop launches with a curated PATH."""
    found = shutil.which("claude")
    if found:
        return found

    path_entries: list[str] = []
    if os.name == "nt":
        try:
            ps = (
                "[Environment]::GetEnvironmentVariable('Path','User') + ';' + "
                "[Environment]::GetEnvironmentVariable('Path','Machine')"
            )
            completed = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if completed.returncode == 0:
                path_entries.extend(completed.stdout.strip().split(";"))
        except Exception:
            pass

        local_appdata = os.environ.get("LOCALAPPDATA")
        if local_appdata:
            packages = Path(local_appdata) / "Packages"
            if packages.exists():
                path_entries.extend(
                    str(path.parent)
                    for path in packages.glob(
                        "Claude_*/*/Roaming/Claude/claude-code/*/claude.exe"
                    )
                )

    for entry in path_entries:
        if not entry:
            continue
        candidate = Path(entry.strip().strip('"')) / ("claude.exe" if os.name == "nt" else "claude")
        if candidate.is_file():
            return str(candidate)
    return None


def run_git(cwd: Path, *git_args: str) -> subprocess.CompletedProcess[str]:
    """Run a git command in cwd and capture text output."""
    return subprocess.run(
        ["git", *git_args],
        cwd=str(cwd),
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )


def validate_worker_worktree(cwd: Path, args: argparse.Namespace) -> int:
    """Refuse risky worktrees before allowing an unattended CLI worker turn."""
    inside = run_git(cwd, "rev-parse", "--is-inside-work-tree")
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        print(json.dumps({"error": f"--cwd is not a git worktree: {cwd}"}), file=sys.stderr)
        return 2

    branch_proc = run_git(cwd, "rev-parse", "--abbrev-ref", "HEAD")
    branch = branch_proc.stdout.strip()
    if branch_proc.returncode != 0 or not branch:
        print(json.dumps({"error": "could not determine current git branch"}), file=sys.stderr)
        return 2

    if not args.allow_non_worker_branch and not branch.startswith(ALLOWED_BRANCH_PREFIXES):
        print(
            json.dumps({
                "error": "refusing to run outside a Claude worker branch",
                "branch": branch,
                "hint": "use --allow-non-worker-branch only for explicit debugging",
            }),
            file=sys.stderr,
        )
        return 2

    status = run_git(cwd, "status", "--short")
    if status.returncode != 0:
        print(json.dumps({"error": "git status failed", "stderr": status.stderr.strip()}), file=sys.stderr)
        return 2
    if status.stdout.strip() and not args.allow_dirty_start:
        print(
            json.dumps({
                "error": "refusing to start from a dirty worker tree",
                "status": status.stdout,
                "hint": "submit/clean current work first, or use --allow-dirty-start for explicit recovery",
            }),
            file=sys.stderr,
        )
        return 2

    return 0


def build_claude_argv(claude_bin: str, args: argparse.Namespace, prompt: str) -> list[str]:
    """Construct the exact argv for the headless `claude` invocation."""
    argv: list[str] = [claude_bin, "-p", prompt, "--output-format", "json"]

    # Session continuity: --resume to continue, else --session-id to pin a known id.
    if args.resume:
        argv += ["--resume", args.resume]
    elif args.session_id:
        argv += ["--session-id", args.session_id]

    if args.model:
        argv += ["--model", args.model]
    if args.effort:
        argv += ["--effort", args.effort]
    if args.max_budget_usd is not None:
        argv += ["--max-budget-usd", str(args.max_budget_usd)]
    if args.bare:
        argv += ["--bare"]

    # Permissions LAST so the variadic --allowedTools list terminates at end-of-argv.
    if args.bypass:
        argv += ["--permission-mode", "bypassPermissions"]
    else:
        argv += ["--permission-mode", "acceptEdits", "--allowedTools", *DEFAULT_ALLOWED_TOOLS]

    return argv


def main() -> int:
    p = argparse.ArgumentParser(description="Headless driver for a worker agent's worktree.")
    p.add_argument("--cwd", required=True,
                   help="Absolute path to the worker's git worktree (run dir).")
    grp = p.add_mutually_exclusive_group()
    grp.add_argument("--prompt", help="Prompt text for this turn.")
    grp.add_argument("--prompt-file", help="Read the prompt from this file (UTF-8).")
    p.add_argument("--session-id", help="Pin a known session UUID (use on the first turn).")
    p.add_argument("--resume", help="Resume an existing session by UUID (later turns).")
    p.add_argument("--phase", choices=["plan", "implement"],
                   help="Apply the plan-gate policy: plan=opus/medium, implement=sonnet/medium. "
                        "Explicit --model/--effort override.")
    p.add_argument("--model", help="Model alias, e.g. 'sonnet' or 'opus'. Overrides the --phase default.")
    p.add_argument("--effort", choices=["low", "medium", "high", "xhigh", "max"],
                   help="Reasoning effort. Overrides the --phase default.")
    p.add_argument("--max-budget-usd", type=float, default=None,
                   help="Hard per-invocation spend cap (printed mode only).")
    p.add_argument("--bare", action="store_true",
                   help="Skip CLAUDE.md auto-discovery etc. for a near-zero-context pulse. "
                        "Not recommended for EMR4 subscription/setup-token auth.")
    p.add_argument("--bypass", action="store_true",
                   help="Use bypassPermissions instead of the scoped allowlist (riskier).")
    p.add_argument("--allow-bypass", action="store_true",
                   help="Permit --bypass. Requires explicit orchestration approval.")
    p.add_argument("--allow-non-worker-branch", action="store_true",
                   help="Permit running outside claude/* branches for explicit debugging.")
    p.add_argument("--allow-dirty-start", action="store_true",
                   help="Permit starting from a dirty worktree for explicit recovery.")
    p.add_argument("--mint-session", action="store_true",
                   help="If no --session-id/--resume given, mint and pin a fresh UUID; print it to stderr.")
    p.add_argument("--dry-run", action="store_true",
                   help="Print the claude argv as JSON and exit without executing.")
    args = p.parse_args()

    # Resolve per-phase model/effort defaults (explicit flags always win).
    if args.phase:
        defaults = PHASE_DEFAULTS[args.phase]
        if not args.model:
            args.model = defaults["model"]
        if not args.effort:
            args.effort = defaults["effort"]

    # Resolve the prompt.
    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text(encoding="utf-8")
    elif args.prompt is not None:
        prompt = args.prompt
    else:
        print(json.dumps({"error": "one of --prompt or --prompt-file is required"}), file=sys.stderr)
        return 2

    # Optionally mint a deterministic session id so the caller can resume later.
    if args.mint_session and not args.resume and not args.session_id:
        args.session_id = str(_uuid.uuid4())
        print(f"[minted-session-id] {args.session_id}", file=sys.stderr)

    if args.resume and args.phase in {"plan", "implement"}:
        print(
            json.dumps({
                "error": "--resume is not allowed with plan-gate phases",
                "hint": "use a fresh session for each plan/implement phase; resume only within a same-model phase",
            }),
            file=sys.stderr,
        )
        return 2

    if args.bypass and not args.allow_bypass:
        print(
            json.dumps({
                "error": "--bypass requires --allow-bypass",
                "hint": "default EMR4 posture is acceptEdits with DEFAULT_ALLOWED_TOOLS",
            }),
            file=sys.stderr,
        )
        return 2

    cwd = Path(args.cwd)
    if not cwd.is_dir():
        print(json.dumps({"error": f"--cwd is not a directory: {cwd}"}), file=sys.stderr)
        return 2

    worktree_check = validate_worker_worktree(cwd, args)
    if worktree_check != 0:
        return worktree_check

    claude_bin = find_claude_bin()
    if not claude_bin and not args.dry_run:
        print(json.dumps({"error": "claude CLI not found on PATH"}), file=sys.stderr)
        return 2

    argv = build_claude_argv(claude_bin or "claude", args, prompt)

    if args.dry_run:
        print(json.dumps({"dry_run": True, "cwd": str(cwd), "argv": argv}, indent=2))
        return 0

    # stdin from DEVNULL avoids the "no stdin data received in 3s" wait.
    proc = subprocess.run(
        argv, cwd=str(cwd), stdin=subprocess.DEVNULL,
        capture_output=True, text=True,
    )

    # Pass the result JSON through verbatim for the orchestrator to parse.
    sys.stdout.write(proc.stdout)
    if proc.stderr.strip():
        sys.stderr.write(proc.stderr)

    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        print(json.dumps({"error": "claude did not emit valid JSON", "returncode": proc.returncode}),
              file=sys.stderr)
        return 1

    return 0 if result.get("is_error") is False else 1


if __name__ == "__main__":
    raise SystemExit(main())
