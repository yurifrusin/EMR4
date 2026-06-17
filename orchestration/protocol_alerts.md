# Protocol Alerts

Read these before acting on remembered process details.

- 2026-06-17: `submit` has been fixed to resolve the active worktree root. Use
  the task packet's `submit` command. Do not manually push to `master`.
- If `submit` fails, stop and report the exact command, working directory,
  branch, and error output to Codex/orchestrator. Do not improvise a workaround.
- Only the Codex orchestrator advances `master` and `handoff/current` in parallel
  mode unless the user explicitly says otherwise.
- Codex-app worker threads are disposable worker checkouts. They must use unique
  branches such as `codex/<task-name>` and submit back for review; they are not
  the durable `codex/current` mirror.
- If these alerts conflict with a prior session memory, trust these alerts.
