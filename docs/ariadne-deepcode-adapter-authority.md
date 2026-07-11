# Ariadne Deep Code Adapter Authority Boundary

> Durable worker artifact for the Deep Code PTY adapter protocol.
> Lane D2 — authority scope documentation.

## Reachability vs Authority

Deep Code is reachable through multiple paths:

- **Interactive TUI**: `deepcode -p <packet>` at a real terminal. This is the
  standard production path. Deep Code responds to tool approvals, file edits,
  and conversational interaction in real time.
- **Non-TTY / headless**: Deep Code deliberately refuses to operate without a
  real TTY. A non-TTY refusal is **adapter unavailability**, not DeepSeek model
  unavailability. Adapters and harnesses must distinguish these two states.
- **PTY adapter bridge**: A programmatic terminal wrapper that spawns Deep Code
  in a pseudo-terminal. The bridge provides bounded process lifecycle control
  (start, poll, stop) but no general bidirectional conversation channel.

**Being reachable does not grant authority.** Deep Code's interactive
capabilities — tool use, file editing, network access — are constrained by the
worker scope and the adapter protocol, not by Deep Code's own ability to
perform them.

## Real-TTY and Non-TTY Handling

| Mode | Behaviour | Worker Result |
|---|---|---|
| Real interactive TTY | Full conversational + tool-permission flow | Durable packet artifact |
| Non-TTY / piped input | Refuses to start; prints TTY-required error | Adapter-unavailability evidence |
| PTY adapter (simulated TTY) | Bounded lifecycle: spawn, wait, kill | PTY events + durable artifact |

The PTY adapter never answers a permission prompt. If Deep Code encounters a
permission prompt (e.g. a write-outside-cwd approval), the prompt suspends the
process until the adapter times out or kills it. Permission prompts **fail
closed**: the operation is not performed, and the worker session ends with an
incomplete artifact. This is a safety feature, not a bug.

## CWD-Wide Write Permission and Allowed Tools

Deep Code's local configuration permits `write-in-cwd` across the entire
process working directory. This permission is necessary so the mailbox bridge
can write its ignored outbox event file without requiring explicit tool
approval each time. Manual (interactive TUI) sessions may also use the legacy
`notify` hook, but **automated sessions use PTY-adapter completion events**
instead — the notify hook cannot reliably execute `.cmd` scripts on Windows.

The following tools are **pre-allowed** (no permission prompt required):

- `read-in-cwd` — reading files inside the disposable worktree
- `write-in-cwd` — writing files inside the disposable worktree
- `query-git-log` — reading Git history (non-mutating)

The following tools are **denied** (the PTY adapter never approves):

- `read-out-cwd` — reading outside the disposable worktree
- `write-out-cwd` — writing outside the disposable worktree
- `delete-in-cwd` — deleting files inside the worktree
- `delete-out-cwd` — deleting files outside the worktree
- `mutate-git-log` — any Git mutation (commit, merge, rebase, push, tag)
- `network` — any network access
- MCP — Model Context Protocol access

**The containment mechanism is the disposable packet-scoped worktree.**
Worker sessions run in ephemeral checkouts created per-packet. CWD-wide write
permission covers only that disposable checkout. Semantic packet ownership is
**not CLI-enforced**; instead, disposable worktrees provide filesystem
containment, and the orchestrator enforces ownership through diff review
during the integration gate.

## Completion: Artifact + Event + Receipt

A Deep Code worker lane completes when all three of these are present:

1. **Authority-bearing durable artifact** — a review packet, plan, or code
   change set at the expected inbox path. This is the **only** result that
   carries authority for orchestrator acceptance.
2. **PTY event** — an adapter-side lifecycle signal (spawned, wrote input,
   produced output, timed out, killed). This is tracking metadata, not
   content verification.
3. **Mailbox receipt** — a record that a mailbox event was written. The
   receipt proves the event file was created; its content is adapter-ignored.

Terminal output is **not authoritative**. Reasons:

1. Terminal output may be truncated, garbled, or misinterpreted by the adapter.
2. Deep Code's TUI renders progress in place; the captured output may miss
   intermediate states.
3. PTY events and receipts are adapter-side evidence only.

**Only the durable artifact is authority-bearing.** The orchestrator must
always read and verify the artifact itself.

## Forced Cleanup Constraint

Forced cleanup (killing the PTY process and retiring the disposable worktree)
is accepted **only after** both of these conditions are met:

1. A valid durable artifact exists (begins with `DECISION: pass` or
   `DECISION: revision_required` for review artifacts, or contains a
   verifiable completion marker).
2. The Deep Code turn has reported a completed state.

There is no exception: forced cleanup is permitted only when both conditions
are satisfied. If either condition is absent, the orchestrator must investigate
before cleanup.

## Protected-Orchestrator-Only Integration

Deep Code workers **never** hold integration authority:

- Workers do not commit, push, merge, or advance `handoff/current`.
- Workers do not modify integration branches (`master`, `handoff/current`,
  `codex/current`, `claude/current`, `antigravity/current`).
- Workers do not deploy, run migrations, change secrets, or modify CI/CD
  configurations.
- Workers do not alter `AGENTS.md`, `CLAUDE.md`, `orchestration/` protocol
  files, or `implementation_plan.md` without explicit orchestrator direction.
- Workers submit durable artifacts to the orchestrator's inbox. The
  orchestrator (Codex as Ariadne) reviews, verifies, integrates, commits, and
  pushes.

Semantic packet ownership is enforced at the orchestrator level, not by the
CLI. Disposable packet-scoped worktrees provide filesystem containment, and
the orchestrator's diff review during the acceptance gate enforces that
workers touched only their assigned scope.

## Summary of Authority Constraints

| Aspect | Constraint |
|---|---|
| Write scope | Disposable packet-scoped worktree only |
| Pre-allowed tools | `read-in-cwd`, `write-in-cwd`, `query-git-log` |
| Denied tools | `read-out-cwd`, `write-out-cwd`, `delete-in-cwd`, `delete-out-cwd`, `mutate-git-log`, `network`, MCP |
| Permission prompts | Fail closed (adapter never approves) |
| Integration authority | None (orchestrator-only) |
| Authority-bearing result | Durable artifact only (not terminal output, events, or receipts) |
| Completion requirements | Artifact (authority) + PTY event (tracking) + receipt (evidence) |
| Ownership enforcement | Orchestrator diff review; worktree provides filesystem containment |
| Forced cleanup condition | Valid artifact exists AND turn reports completion |
| Automated session signalling | PTY-adapter events (not legacy notify hook) |
