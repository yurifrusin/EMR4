# Protocol Alerts

Read these before acting on remembered process details.

- 2026-06-17: `submit` has been fixed to resolve the active worktree root. Use
  the task packet's `submit` command. Do not manually push to `master`.
- Standing orchestration rule: every protocol-followed command should be reported
  back to Codex/orchestrator, whether it succeeds or fails. For success, report
  the command, working directory, branch, and short success result. For failure
  or refusal, include the details below and then stop.
- Before running `submit`, fill in the source task packet's Completion Notes with
  files changed, verification run, and remaining risks. `submit` copies those notes
  into the Codex review packet automatically; do not leave Codex with a boilerplate
  review packet.
- Plan-gated sprint rule: for non-trivial sprint packets, workers must write an
  implementation plan before editing project code. Capture it with
  `python scripts\agent_worktrees.py plan --agent <agent> --task <task> ...`,
  show the same plan in the GUI, then stop. Do not code until the user/Codex says
  `complete sprint task`.
- Plan-gate auto-proceed warning: if an agent app offers, displays, or executes an
  "auto-proceed", "auto-approved", or similar continuation after the plan, that is
  not EMR4 approval. Stop anyway and wait for the explicit `complete sprint task`
  instruction. Report any accidental auto-proceed to Codex with the files touched
  and verification run.
- If an agent identifies a useful follow-up outside its current packet, it must
  not leave that suggestion only in the app chat. Capture it for Codex with
  `python scripts\agent_worktrees.py suggest-task --agent <agent> --title "..."`.
  A suggestion is not authorization to implement; Codex/orchestrator triages it
  into a future sprint or folds it into current scope.
- If any protocol command (`handin`, `sync`, `submit`, `realign`, `poll`, or task
  packet command) fails or refuses to run, stop and report the exact command,
  working directory, branch, `git status --short --branch`, and error output to
  Codex/orchestrator. Do not improvise a workaround.
- On push failure, `submit` will attempt to create a local Codex submit-alert packet,
  commit it, and publish it to a unique `submit-alert/...` branch. Still stop and
  report the output; Codex can then poll/reconcile the alert branch.
- Only the Codex orchestrator advances `master` and `handoff/current` in parallel
  mode unless the user explicitly says otherwise.
- GitHub Pages must deploy from canonical `master` only. Do not manually deploy
  `codex/current`, `claude/current`, or `antigravity/current` unless Codex has just
  confirmed those mirror branches are aligned to `master`. A later Pages deployment
  from a stale worker mirror can overwrite the live artifact with older taskpane or
  diary assets. Prefer the `.github/workflows/pages.yml` GitHub Actions deployment
  from `master`; set Pages source to GitHub Actions in repository settings.
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
  <agent> --apply` from that worker worktree. This resets the clean mirror to
  `origin/handoff/current` and force-with-lease updates the durable remote mirror
  branch, rather than rebasing and replaying the already-integrated submit commit.
- If these alerts conflict with a prior session memory, trust these alerts.
