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
- 2026-06-24: Use `orchestration/phase_programmes.md` as the planning layer
  between implementation phases and tactical sprints. Prefer coherent
  outcome-sized sprints inside a programme over reactive micro-sprints.
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
- External-agent control rule: after `HANDIN READY`, Ariadne should use the
  lowest-cost text channel available for external workers before considering
  GUI automation. Antigravity should be prompted with:
  `C:\Users\YuriFrusin\AppData\Local\agy\bin\agy.exe --conversation e959487d-4cc5-4528-bc81-8b637702d006 --print "<prompt>"`.
  Claude should be prompted with `scripts\drive_agent_headless.py` from a clean
  shell and the Claude worker worktree, using `--phase plan` for plan-gated
  handin and `--phase implement` only after plan approval. Yuri does not need to
  explicitly invoke these routine worker prompts. If a CLI is unavailable,
  Ariadne should fall back to Computer Use where appropriate, then ask Yuri for
  only the smallest manual prompt still needed.
- Claude headless plan-gate rule: do not `--resume` across a plan gate. The plan
  and implementation turns use different default models (`plan` = Opus/medium,
  `implement` = Sonnet/medium), so use a fresh session per phase. Re-run
  `handin` in the implementation prompt so Claude reloads the persisted task
  packet and approved plan from git. `--resume` is only for multi-turn recovery
  inside the same phase/model.
- Claude headless permission rule: use the driver default posture of
  `acceptEdits` plus the scoped allowed tools (`Bash`, `Edit`, `Write`, `Read`,
  `Grep`, `Glob`) on Claude worker branches only. Do not use
  `bypassPermissions` or run from `master`/the integration worktree unless Yuri
  explicitly approves a debugging exception. Poll/git remains the authoritative
  verification channel; do not treat a CLI success JSON as proof of submission.
- Claude headless auth rule: run the driver from Ariadne's clean shell, not from
  inside a nested Claude Code tool call, because nested Claude sessions can
  inherit auth/routing overrides and 401. Do not use `--bare` for EMR4 routine
  prompts; it is incompatible with the current subscription/setup-token auth
  path.
- Computer Use restart rule: after a Windows/Codex restart, Computer Use may be
  available through the skill's JS bootstrap path even when no standalone
  desktop-control tool appears in tool discovery. Ariadne should read/use the
  current `computer-use` skill, bootstrap via the Node REPL, and verify
  `sky.list_apps()` before reporting Computer Use unavailable. Old plugin-cache
  paths can become stale after Codex updates.
- Submission visibility rule: if Claude/Antigravity says a plan or review was
  submitted but `poll --fetch` does not show it, inspect the worker worktree for
  uncommitted `orchestration/agent_inbox/codex/...` packets and task status
  edits. Local-only packets are not submitted. Nudge the worker to use the
  packet/protocol `submit --task ...` path so the files are committed and pushed
  to the durable worker branch; do not approve implementation from GUI text
  alone.
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
  apply hotfixes for issues found. If a residual user test appears blocked by
  tooling rather than truly human judgment, Ariadne should research local and
  online options, then install/configure safe tools as needed to complete the
  test independently. Ariadne may log into EMR4 with dummy dev user/dev admin
  credentials for non-PHI dev verification. Flag Yuri only for material cost,
  security/privacy risk, external-console action, or manual intervention such as
  restarting Codex. Only after that should Ariadne summarize the
  inspection result, verification run, hotfixes, and remaining manual user tests
  from `orchestration/sprint_closeout.md`. Then wait for user approval unless the
  user explicitly granted proceed-through integration for that sprint. Plan-gated
  approval still requires explicit `complete sprint task` before workers begin
  implementation.
- Cost-conscious UI review rule: conserve model/tool credits during sprint
  verification. Use the cheapest reliable signal first: backend/API tests,
  static frontend checks, reusable parameterized review primitives
  (`assert_text_in`, `assert_count`, `assert_api_field`, `assert_version`),
  direct Playwright/CDP/JavaScript assertions against known URLs/selectors, and
  scoped accessibility/DOM summaries before any screenshot-heavy or step-by-step
  Computer Use browsing. Avoid full DOM dumps, broad screenshots, and repeated
  visual polling loops. The goal is to remove the model from deterministic
  execution loops: explore once, crystallize into a stored script/harness, then
  run that harness with compact structured output on future sprints. Escalate to
  real Chrome/Computer Use interaction only for behaviours that need real
  browser input or Office/dialog state, and use cropped/small visual checks when
  structural assertions cannot prove the result. Do not add a local model such
  as Gemma to the sprint loop unless measured residual interactive/visual review
  cost remains high after scriptable checks have been harvested.
- Closeout ping rule: Ariadne's sprint-closeout notification must include the
  Codex-side/tool-enabled reviews and tests already run, any bounded hotfixes
  made from those checks, and only the residual user review/testing that could
  not be confirmed with available tools. If no manual testing remains, say so
  explicitly and why. UI work should include browser/Chrome/Office-dialog checks
  where available before asking Yuri to test.
- Forward-progress rule: if a sprint closes cleanly and Ariadne's review leaves
  no Yuri-only manual tests, approvals, risk calls, or priority decisions, Ariadne
  should continue into the next recommended sprint from the current programme
  rather than waiting idly. Dispatch the next sprint, announce `HANDIN READY`,
  and use external-agent CLIs for Claude/Antigravity prompts when available,
  falling back to Computer Use only when text channels are unavailable or a GUI
  interaction is genuinely required. Stop and notify Yuri only when human input
  is genuinely needed.
- Residual user-test detail rule: when any closeout leaves manual checks for
  Yuri, Ariadne must provide concrete, step-by-step user review instructions,
  not just a terse checklist. Include setup/preconditions, exact UI path,
  goal of the check, expected result, suspicious/failure signs, what can be
  skipped, and what evidence or screenshots to report back. These steps should
  cover only checks Ariadne could not run herself after researching and applying
  appropriate tooling.
- Notification rule: when local notification credentials are configured,
  Ariadne should send a short non-PHI alert for sprint closeout, blockers,
  security findings needing judgment, or user decision points using
  `scripts/notify_yuri.py`. Prefer `NOTIFY_PROVIDER=pushover` when available;
  WhatsApp remains a fallback path. Do not put PHI, patient identifiers,
  secrets, raw errors, or detailed clinical/project context in push messages;
  link Yuri back to Codex/repo docs for details. If notification delivery is
  unavailable, keep using the in-thread closeout notification and say the push
  alert was not sent.
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
