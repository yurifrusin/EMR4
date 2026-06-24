# Protocol Alerts

Read these before acting on remembered process details.

- 2026-06-23: For current project state, trust refs/audit first, then
  `orchestration/sprint_closeout.md`, `orchestration/integration_log.md`,
  `orchestration/protocol_alerts.md`, and `AGENTS.md`. Historical sections in
  `orchestration/parallel_workstreams.md` help with context but must not
  override closeout/log/audit state.
- 2026-06-23: Normal polling is now fast and skips old remote `codex/*`
  disposable worker refs. Use `python scripts\agent_worktrees.py poll --fetch`
  by default. Use `--include-codex-workers` only when a current Codex subagent
  submit is expected.
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
- Plan-packet submission allowance: during a plan-gated sprint, workers may
  create, commit, and push the implementation-plan packet and minimum
  coordination-file status changes required to submit that plan to Codex's
  inbox. This allowance does not permit production code changes. Do not edit
  `app/`, diary UI, taskpane, migrations, tests, or runtime docs unless the
  task explicitly says the plan itself belongs in a documentation file.
- Antigravity artifact warning: if artifact review asks for approval during the
  plan gate, treat approval as permission to submit the implementation-plan
  packet only, not permission to implement the sprint task.
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
- Post-poll review rule: once `poll --fetch` shows the expected implementation
  review packets for the active sprint, Codex/orchestrator may proceed through
  local inspection, bounded repair, verification, and draft closeout unless a
  submission is missing, out of scope, unsafe, failing verification, or otherwise
  needs user or worker clarification. Before pushing sprint changes to `master`,
  Ariadne should run every feasible Codex-side/tool-enabled test first, including
  browser/Chrome checks for real UI affordances when relevant and available, then
  apply hotfixes for issues found. Only after that should Ariadne summarize the
  inspection result, verification run, hotfixes, and remaining manual user tests
  from `orchestration/sprint_closeout.md`. Then wait for user approval unless the
  user explicitly granted proceed-through integration for that sprint. Plan-gated
  approval still requires explicit `complete sprint task` before workers begin
  implementation.
- Closeout ping rule: Ariadne's sprint-closeout notification must include the
  Codex-side/tool-enabled reviews and tests already run, any bounded hotfixes
  made from those checks, and only the residual user review/testing that could
  not be confirmed with available tools. If no manual testing remains, say so
  explicitly and why. UI work should include browser/Chrome/Office-dialog checks
  where available before asking Yuri to test.
- WhatsApp notification rule: when local WhatsApp Cloud API credentials are
  configured, Ariadne should send a short non-PHI WhatsApp alert for sprint
  closeout, blockers, security findings needing judgment, or user decision
  points using `scripts/notify_yuri_whatsapp.py`. Do not put PHI, patient
  identifiers, secrets, raw errors, or detailed clinical/project context in
  WhatsApp; link the user back to Codex/repo docs for details. If WhatsApp is
  unavailable, keep using the in-thread closeout notification and say WhatsApp
  was not sent.
- Protocol amendment rule: prefer batching non-urgent orchestration protocol edits
  until the discussion settles. Codex should remind the user before launch if
  agreed protocol edits are still pending.
- Codex-app worker threads are disposable worker checkouts. They must use unique
  branches such as `codex/<task-name>` and submit back for review; they are not
  the durable `codex/current` mirror.
- Codex role separation: Ariadne/orchestrator Codex runs from the integration
  worktree and owns final integration. A Codex worker/subagent must use an
  explicit task branch, never `master`. Future Codex plan packets should include
  `| Role | orchestrator |` for Ariadne-owned plans or `| Role | codex-worker |`,
  `| Worker Name | ... |`, and `| Worker Branch | codex/<short-task-name> |`
  for separate Codex workers. Ariadne must not treat an orchestrator-created
  Codex plan as proof that a separate worker submitted.
- Codex records integrated submits in `orchestration/integration_log.md` and runs
  `audit` / `retire-stale` after integrations so stale disposable worktrees are
  visible instead of surprising the next session.
- After Codex integrates a submitted durable worker branch, Codex should realign
  the clean worker mirror with `python scripts\agent_worktrees.py realign --agent
  <agent> --apply` from that worker worktree. This resets the clean mirror to
  `origin/handoff/current` and force-with-lease updates the durable remote mirror
  branch, rather than rebasing and replaying the already-integrated submit commit.
- If these alerts conflict with a prior session memory, trust these alerts.
