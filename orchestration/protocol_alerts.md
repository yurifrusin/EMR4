# Protocol Alerts

## H-series full-trove and Claude Fable review gate

- The full local diary trove is expected to become useful later, but not as raw
  retrieval, raw fine-tuning, or provider prompt material. Treat it as a local
  PHI-bearing evidence mine that can refresh source-safe aggregate profiles and,
  only after H15 approval, de-identified synthetic semantic fixture families.
- R28 used `claude-fable-5` for the full-trove readiness consult. Trust the
  integrated packet
  `orchestration/agent_inbox/codex/plan-claude-claude-r28-fable-full-trove-readiness-review.md`
  as the durable recommendation if Fable access has lapsed.
- Fable's ordering is now the default: native Bernie/Diary action grammar first,
  deterministic synthetic replay consumer second, H22 semantic gate-review
  packet third, one-time full-trove mining only after Yuri approves H15.

## Sprint 106 Claude/Fable consulting gate

- Sprint 106 is a Claude-only consulting sprint for Bernie's reception-domain
  copilot architecture. Planning should use Claude CLI model
  `claude-fable-5` with high effort when available.
- This sprint is plan-only until Yuri explicitly approves implementation after
  reviewing the submitted Fable plan with Ariadne. Do not treat a submitted
  plan, auto-proceed prompt, or ordinary worker continuation as permission to
  edit production code.
- If `claude-fable-5` is unavailable, blocked, or rerouted, stop and report the
  exact CLI/model error to Ariadne rather than silently falling back.

Read these before acting on remembered process details.

- 2026-07-06: Default sprint-worker protocol means cross-worker lanes, not
  three native Codex subagents. At the start of each non-trivial sprint, Ariadne
  must check and record Claude and Antigravity availability before choosing the
  worker mix. The preferred mix is Claude first (Sonnet for ordinary
  implementation/review, Opus/Fable only for unusually complex architecture or
  high-leverage consulting), Antigravity/Gemini as a first-class independent
  worker (current default/Gemini Flash-class model unless escalation is needed),
  and DeepSeek Flash as the cheap high-parallelism worker lane. If Claude or
  Antigravity is quota-capped, recuperating, unavailable, or fails to submit a
  durable artifact in the sprint window, Ariadne should replace that lane with
  additional DeepSeek Flash work or complete the bounded remainder directly.
  Native Codex subagents are fallback/integration helpers, not the default
  meaning of "three lane sprint"; use them only when an external lane is
  unavailable, the work is tiny/tightly coupled, or Codex-specific tooling is
  materially better. Sprint closeout must state the actual worker mix and any
  substitutions from the preferred Claude/Antigravity/DeepSeek mix.
- 2026-07-07: Every sprint closeout must explicitly situate the sprint inside
  the larger implementation plan. State the relevant phase, programme, or
  strategy track; whether the sprint was a feature increment, guardrail
  hardening, review integration, tooling/process repair, or strategy sprint;
  what larger objective it advanced; and what the next planned step is. If
  Ariadne cannot clearly name that larger position, pause tactical
  micro-sprints and propose a strategy/planning sprint, potentially with
  Claude/Fable, before continuing.
- 2026-07-07: Avoid Ariadne-only sprint drift. Ariadne-only implementation is
  appropriate for tiny, tightly coupled guardrail increments, mechanical docs,
  or urgent hotfixes where extra worker setup would add more risk than review.
  Substantial, separable, judgment-heavy, architecture-facing, or safety-gate
  sprint blocks should include an independent worker/reviewer lane by default,
  or Ariadne must record why this sprint is intentionally single-track. This is
  especially important for Bernie Interpretation Harness work after H40-H62:
  use the H63 independent review brief before any larger runtime/provider/trove
  proposal.
- 2026-07-07: Recent sidetracked guard-cleanup sprints proved that even
  well-intended Ariadne-only work can become too single-track. Product-facing
  EMR4 development, sprint direction, safety-gate judgment, and Fable-aligned
  Bernie/Diary work should stay in a multi-agent stream by default: use Claude
  and Antigravity when available, keep DeepSeek active as an independent worker
  or reviewer, and add extra DeepSeek lanes when Claude or Antigravity are
  capped, unavailable, stale, or too slow for the sprint window. Ariadne-only
  continuation is acceptable only for tiny mechanical edits, hotfixes, or
  tightly coupled integration work, and the closeout must say why a broader
  worker mix was not used.
- 2026-07-07: Ariadne plus three is the default for general sprint work. The
  intended active sprint team is Ariadne as orchestrator/integrator plus three
  worker lanes: Claude, Antigravity, and DeepSeek. DeepSeek is not merely an
  emergency fallback; one DeepSeek lane should be used alongside Claude and
  Antigravity for ordinary multi-agent sprint work. If Claude or Antigravity is
  offline, quota-limited, stale, blocked, or otherwise unavailable in the sprint
  window, Ariadne should immediately replace that lane with an additional
  DeepSeek worker and keep moving under Yuri's standing full authority. When
  Claude or Antigravity becomes available again, restore the standard
  Claude/Antigravity/DeepSeek worker mix. Sprint closeout must state the actual
  worker mix and any DeepSeek substitutions.
- 2026-07-08: At the start of every sprint, Ariadne must explicitly announce
  whether Claude, Antigravity, and DeepSeek will be used for that sprint. If a lane will not be used, Ariadne must state the reason before proceeding. If
  Claude or Antigravity is unavailable because of usage limits, quota recovery,
  tooling failure, or silence in the sprint window, Ariadne must announce the
  unavailability and spawn an extra DeepSeek worker to cover that missing
  lane's review or implementation role unless the sprint is tiny and Ariadne
  records why a substitution would add more risk than value. Sprint closeout must repeat the actual worker mix and any substitution.
- 2026-07-08: The same sprint-start worker announcement must state how many DeepSeek worker lanes are already spawned/open, which ones are active versus completed or idle, and whether an existing lane will be reused for related follow-on work. Ariadne must close completed or unused DeepSeek lanes before
  spawning fresh ones when their outputs have been captured, so the worker pool
  does not hit its thread limit during the next sprint. Reuse an existing DeepSeek lane when the follow-on task is closely related and the lane is still
  open and coherent; spawn a fresh lane only when the old lane is closed,
  stale, overloaded, or contextually wrong for the new task.
- 2026-07-08: Sprint-start worker announcements must name the invocation mode
  for each preferred lane: Claude through the headless Claude CLI driver
  (`scripts\drive_agent_headless.py`), Antigravity through the Antigravity
  `agy.exe` CLI channel, and DeepSeek through direct Codex `deepseek-worker`
  spawning. Do not describe Claude or Antigravity as unavailable merely because
  they are not exposed as native Codex subagent tools; their CLI channels are
  the expected routine path.
- 2026-07-08: Sprint-start worker announcements must also report worker
  cleanliness before dispatch. Check Claude and Antigravity with
  `git status --short --branch` in their worktrees; if stale untracked
  artifacts from previous sprints are present, preserve/integrate any relevant
  current-sprint work, clean the stale artifacts, re-run status, and
  re-announce cleanliness before progressing. DeepSeek normally has no durable
  worktree because it is direct-spawned inside Codex; report active/completed
  lane count, unintegrated output state, and close/reuse decisions as its
  cleanliness check.
- 2026-07-07: Antigravity availability must not be inferred solely from a bare
  `antigravity --version` shell probe. If the Antigravity/Gemini UI quota view
  shows usable availability, treat Antigravity as available and use the known
  Antigravity CLI path/protocol (`agy.exe`) or GUI/tooling route for the worker
  lane. A missing PATH alias is a tooling-path issue, not quota recuperation.
- 2026-07-07: Do not leave completed, stale, or idle Codex subagent threads open
  after their sprint role is finished. Before launching extra DeepSeek or other
  native subagent lanes, close old worker agents that are no longer needed so
  the local worker pool does not hit its thread limit while useful lanes are
  waiting.
- 2026-07-07: Sprint closeout is not complete until the integrated work is
  committed, pushed, and the integration worktree is clean. A closeout may be
  recorded as `local-only`, `pending commit`, or `pending push` only when there
  is an explicit blocker or Yuri has asked to defer publication; otherwise each
  sprint/batch closeout must run and record `git status --short --branch`, the
  verification commands, `git commit`, `git push origin master`, and the final
  clean status. Do not describe a sprint as `integrated`, `closed`, or
  `continuing` in `orchestration/sprint_closeout.md`,
  `orchestration/integration_log.md`, AGENTS.md, or push notifications if the
  corresponding code/docs remain only in the local working tree.
- 2026-07-05: Sprint worker mix now starts with a Claude availability/quota
  check so Ariadne remembers to use Claude when it is healthy. If Claude is
  quota-capped, unavailable, recuperating, or fails to submit a usable plan in
  the current sprint window, Ariadne should automatically replace the Claude
  lane with a DeepSeek Flash worker rather than waiting for Yuri. Ariadne may
  also spawn as many additional DeepSeek Flash workers as the sprint
  requirements safely justify. Every DeepSeek worker must use a separate
  branch, clear file/review boundary, distinct role (for example implementation
  vs adversarial review), plan gate, submit path, and Ariadne-run verification
  before integration. Use DeepSeek Pro only when reasoning depth, not diff
  hygiene, is the limiting factor. This is the default replacement protocol for
  a recuperating Claude lane, not an exceptional escalation.
- 2026-07-05: Graphify is approved as an opt-in Ariadne navigation aid, not an
  always-on memory layer. Use it autonomously when the question starts from a
  known symbol, function, route, class, or UI handler and the goal is impact or
  orientation. Refresh with `scripts\refresh_code_graph.ps1` when code changed
  since the last graph build. Prefer `explain` and `affected`; avoid broad
  natural-language `query` unless narrowed by concrete context. Treat graph
  output as a map to source/tests, not as authoritative truth. Do not enable
  Graphify MCP, hooks, or post-commit auto-indexing without a later tooling
  sprint proving refresh/reload and worker-worktree safety.
- 2026-07-04: Updated sprint worker mix. Claude is allowed to perform real
  implementation work on `claude/current` when quota is healthy; it is not
  limited to planning. Antigravity/Gemini is not limited to UX work: use it for
  independent backend/domain-policy critique, test design, fixture/harness
  work, architecture dissent, and small bounded implementation lanes when it
  has clear file ownership and a tangible repo artifact. Avoid spending
  Fable/high-cost Claude modes except for architecture consulting or unusually
  hard review. When OpenAI/Codex usage is scarce, keep Ariadne as
  orchestrator/integrator and offload bounded real work to Claude, Antigravity,
  and DeepSeek. When OpenAI usage is healthy, Ariadne may also spawn native
  Codex subagents alongside Claude, Antigravity, and DeepSeek.
- 2026-07-04: DeepSeek Flash via `codex-deepseek-bridge` is approved for
  bounded implementation experiments when Ariadne remains orchestrator and
  integrator. Use dedicated worker branches and tight file/review boundaries.
  Prompts must explicitly forbid deleting existing tests unless requested,
  require UTF-8 without BOM, top-level import hygiene, no `.tmp`/`.bak`
  leftovers, `git diff --stat` plus `git status --short --branch` before
  handback, and exact tests/results. Ariadne must review the diff and run
  verification before merging. Prefer Flash for small/backend-internal
  refactors; try Pro only if reasoning quality, not diff hygiene, becomes the
  limiting factor. Multiple DeepSeek workers may run at once in whatever number
  the sprint requirements justify, provided each has a separate branch,
  non-overlapping ownership or review boundary, and independent verification
  plan.
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
- 2026-06-30, amended 2026-07-06: Substantial Bernie / agentic-reception work
  defaults to the external-worker plan-gated loop: Claude,
  Antigravity/Gemini, and DeepSeek Flash each submit bounded plans/reviews or
  implementation artifacts first when available; Ariadne reviews, accepts or
  requests resubmission, and only then releases implementation with
  `complete sprint task`. Depart from this only for narrow hotfixes, tooling
  failures, quota/recuperation, or explicitly documented scope/risk reasons.
  If Claude or Antigravity is unavailable, replace that lane with another
  DeepSeek Flash worker before reaching for a native Codex subagent. Keep
  visible receptionist UX calm and helpful; safety belongs primarily in typed
  API contracts, confirmation endpoints, RBAC, and audit trails rather than
  alarming staff-facing copy.
- 2026-07-01: Bernie release gates are recorded in
  `orchestration/bernie_release_gates.md`. A basic Bernie booking happy path,
  including the Margaret Thompson / Dr Shera ordinary receptionist prompt, is a
  blocking release gate for Bernie booking work, not optional residual user
  review. Do not call route-intercepted, fake-provider, mocked-provider, or
  `?smoke=true` Playwright checks "live"; a true live-provider check must reach
  the configured provider path and include evidence such as
  `live_provider: true`. If a reported screenshot/visual failure remains
  reproducible, Sprint 97-style Bernie work cannot close as verified.
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
  GUI automation. Antigravity should normally be prompted from a fresh
  project-scoped CLI session:
  `C:\Users\sarashera\AppData\Local\agy\bin\agy.exe --add-dir C:\Users\sarashera\EMR4-worktrees\antigravity --print "<prompt>"`.
  Do not rely on stale `--conversation` IDs after app/CLI restarts unless the
  conversation ID has just been verified. If stdout is blank, inspect the
  Antigravity transcript/log and then trust poll/git, not chat text, as proof of
  submission. 2026-06-28 local probe confirmed the upstream Windows stdout
  capture issue described in
  `https://github.com/google-antigravity/antigravity-cli/issues/115`: `agy`
  may return no useful captured transcript from a non-TTY Codex shell, while
  still performing requested filesystem writes. For routine EMR4 automation,
  prompts to Antigravity must request a tangible repo artifact such as a plan
  packet, review packet, task-packet completion notes, or an explicit temporary
  proof file in the Antigravity worktree. Codex should verify success with
  `git status`, `poll --fetch`, and file inspection. Do not treat blank stdout
  alone as failure when the expected artifact was created, and do not treat
  stdout text alone as success without a committed/pushed packet. Keep
  `C:\Users\sarashera\.gemini\antigravity-cli\settings.json` as UTF-8 without
  BOM; a BOM makes the CLI ignore settings and fall back to defaults.
  For non-trivial Antigravity plan or implementation prompts, pass an explicit
  `--print-timeout 15m`; Codex's shell timeout does not extend Antigravity's
  internal print-mode timeout. Before calling a silent Antigravity return a
  crash, check `tasklist /FI "IMAGENAME eq agy.exe"`,
  `git -C C:\Users\sarashera\EMR4-worktrees\antigravity status
  --short`, and the latest
  `C:\Users\sarashera\.gemini\antigravity-cli\log\cli-*.log`. A clean worktree,
  no `agy.exe`, and a log line such as `Print mode: timed out` means the CLI
  timed out while streaming rather than crashing.
  Claude should be prompted with `scripts\drive_agent_headless.py` from a clean
  shell and the Claude worker worktree, using `--phase plan` for plan-gated
  handin and `--phase implement` only after plan approval. Yuri does not need to
  explicitly invoke these routine worker prompts. If a CLI is unavailable,
  Ariadne should fall back to Computer Use where appropriate, then ask Yuri for
  only the smallest manual prompt still needed.
- Parallel implementation release rule: once all plan packets for a sprint have
  been reviewed and accepted, Ariadne should release independent Claude,
  Antigravity, and DeepSeek Flash implementation/review tasks in parallel using
  their lowest-cost text channels. A native Codex worker may supplement or
  replace one of those lanes only when the external lane is unavailable,
  recuperating, too slow for the bounded sprint window, or when Codex-specific
  tooling is the right fit. Serial release is reserved for unusual conditions:
  unproven/broken worker CLI channels, overlapping mutable file surfaces,
  security-sensitive manual approval points, or active recovery from a protocol
  violation. If Ariadne serializes a release or substitutes Codex for an
  external lane, record why.
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
- Worker-count rule: use the right number of agents for the risk and separable
  surfaces, not "always three agents". Ariadne may keep a narrow sprint
  single-track, add one specialist reviewer, or spawn extra Claude,
  Antigravity, or Codex workers when independent ownership boundaries make the
  extra review/parallelism worth it.
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
- UI review harness rule: run the deterministic `review/` harness before
  interactive browser review when diary smoke coverage is relevant:
  `pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q`.
  The CI workflow `.github/workflows/ui-review.yml` runs the same checks on
  diary/review changes. Add new stable checks here rather than repeating
  screenshot-driven inspections when a structural assertion can prove the end
  state.
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
  link Yuri back to Codex/repo docs for details. Every sprint-closeout push
  notification must state whether the sprint engine is continuing or paused. If
  continuing, name the next sprint/workstream briefly. If paused, include the
  concrete pause reason, for example awaiting Yuri approval, manual clinical
  review, external credential/console action, failing verification, worker
  protocol failure, or an unresolved safety/product decision. If notification
  delivery is unavailable, keep using the in-thread closeout notification and
  say the push alert was not sent.
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
- Codex worker polling refinement: for active Codex app subagents, Ariadne
  should not routinely use broad `poll --fetch --include-codex-workers`.
  Prefer the direct subagent channel/status, the recorded worker id/branch, and
  exact branch/packet inspection (`git fetch origin codex/<task>` plus the
  expected plan/review packet). Reserve `--include-codex-workers` for recovery
  cases where the worker branch is unknown, the direct subagent link is lost, or
  a historical remote Codex worker submission must be discovered. Broad Codex
  worker polling is intentionally slower/noisier because old `codex/*` refs may
  remain on the remote.
- Antigravity CLI model policy: normal Antigravity UI sprint work should use
  the current default Gemini 3.5 Flash / Medium reasoning posture unless plan or
  implementation quality indicates escalation is needed; Medium is the expected
  cost/quality sweet spot for narrow sprint packets. If Claude is quota-blocked
  or a task needs Claude-style reasoning, Ariadne may try Antigravity CLI
  `--model` overrides with GUI-available Claude models after a no-edit probe
  confirms the exact CLI model identifier. Prefer Claude Sonnet 4.6 for
  implementation/recovery work and Claude Opus 4.6 for high-leverage planning,
  architecture, or repeated failure recovery. Treat GPT-OSS 120B as
  experimental until it has passed low-risk EMR4 tasks. Do not hardcode
  unverified `settings.json` reasoning/model keys; prefer per-run CLI overrides
  or verified settings values.
- Codex records integrated submits in `orchestration/integration_log.md` and runs
  `audit` / `retire-stale` after integrations so stale disposable worktrees are
  visible instead of surprising the next session.
- After Codex integrates a submitted durable worker branch, Codex should realign
  the clean worker mirror with `python scripts\agent_worktrees.py realign --agent
  <agent> --apply` from that worker worktree. This resets the clean mirror to
  `origin/handoff/current` and force-with-lease updates the durable remote mirror
  branch, rather than rebasing and replaying the already-integrated submit commit.
- If these alerts conflict with a prior session memory, trust these alerts.
- Bernie Interpretation Harness readiness gate: before any worker or Ariadne
  sprint proposes runtime route wiring, provider prompt/dry-run wiring,
  memory/RAG/GraphRAG use, H15/H-series runtime imports, or
  historical diary material access from the provider-free interpretation harness, run
  `.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py`.
  Current expected values are `runtime_or_provider_wiring_ready=false`,
  `raw_trove_access_ready=false`, and `runtime_gate_decision=blocked`. If the
  command fails or those values change, pause the sprint engine for explicit
  review instead of continuing automatically.
  Before any provider-boundary, provider integration, provider prompt, or
  provider dry-run recommendation, also run
  `.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py`.
  Current expected provider-boundary values are `default_provider=disabled`,
  `runtime_or_provider_wiring_ready=false`, `live_provider_enabled=false`,
  `provider_calls_performed=false`, `route_behavior_changed=false`,
  `database_access_performed=false`, `memory_or_rag_access_performed=false`,
  and `historical_diary_material_access_performed=false`.
