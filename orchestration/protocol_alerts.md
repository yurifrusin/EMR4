# Protocol Alerts

Read these before acting on remembered process details.

- 2026-06-17: `submit` has been fixed to resolve the active worktree root. Use
  the task packet's `submit` command. Do not manually push to `master`.
- Standing orchestration rule: every protocol-followed command should be reported
  back to Codex/orchestrator, whether it succeeds or fails. For success, report
  the command, working directory, branch, and short success result. For failure
  or refusal, include the details below and then stop.
- If any protocol command (`handin`, `sync`, `submit`, `realign`, `poll`, or task
  packet command) fails or refuses to run, stop and report the exact command,
  working directory, branch, `git status --short --branch`, and error output to
  Codex/orchestrator. Do not improvise a workaround.
- On push failure, `submit` will attempt to create a local Codex submit-alert packet,
  commit it, and publish it to a unique `submit-alert/...` branch. Still stop and
  report the output; Codex can then poll/reconcile the alert branch.
- Only the Codex orchestrator advances `master` and `handoff/current` in parallel
  mode unless the user explicitly says otherwise.
- Sprint launch rule: Codex/orchestrator must announce `HANDIN READY` before the
  user prompts external worker agents to run `handin`.
- Sprint integration rule: Codex/orchestrator must not push sprint work through
  to `master` until all active sprint agents, including any Codex subagent worker,
  have submitted or been explicitly stood down.
- Protocol amendment rule: prefer batching non-urgent orchestration protocol edits
  until the discussion settles. Codex should remind the user before launch if
  agreed protocol edits are still pending.
- Codex-app worker threads are disposable worker checkouts. They must use unique
  branches such as `codex/<task-name>` and submit back for review; they are not
  the durable `codex/current` mirror.
- Codex records integrated submits in `orchestration/integration_log.md` and runs
  `audit` / `retire-stale` after integrations so stale disposable worktrees are
  visible instead of surprising the next session.
- After Codex integrates a submitted durable worker branch, Codex should realign
  the clean worker mirror with `python scripts\agent_worktrees.py realign --agent
  <agent> --apply` from that worker worktree, rather than rebasing and replaying
  the already-integrated submit commit.
- If these alerts conflict with a prior session memory, trust these alerts.
