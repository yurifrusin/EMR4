# EMR4 Parallel Workstreams

This is the live board for Codex-orchestrated parallel work. `AGENTS.md` remains the
single source of truth for durable project state; this file tracks active branch work.
For the layer between long phases and tactical sprints, use
`orchestration/phase_programmes.md`.

## Operating Rules

- Every agent starts with `python scripts\agent_worktrees.py handin`.
  This now performs the full intake ritual: sync, infer agent, list inbox, and
  print protocol alerts plus the next task packet.
- Protocol changes must be written to `orchestration/protocol_alerts.md`.
  Worker agents should trust those alerts over remembered prior-session details.
- Parallel workers finish with `python scripts\agent_worktrees.py submit ...`.
  Packet submit commands include `--task`, which creates a Codex review packet
  in the worker branch.
- If `submit` fails, the worker must stop and report the exact command, working
  directory, branch, and error output. Do not manually push to `master` or
  `handoff/current` as a workaround.
- `codex/current` is the durable Codex mirror branch. It is not the same thing as
  a Codex-app subagent worktree. Codex subagents should use unique task branches
  such as `codex/time-model`, `codex/gemini-sdk-migration`, or
  `codex/<short-task-name>`.
- Codex-app subagent worktrees may live under `.codex/worktrees/...`; treat them
  as disposable worker checkouts. They must submit or be reviewed/integrated by
  the orchestrator before their work is considered part of the project.
- Ariadne/orchestrator Codex is distinct from Codex worker/subagents. Codex
  workers must use explicit task branches, never `master`; future Codex plan
  packets should mark `Role` as either `orchestrator` or `codex-worker`.
- Codex dispatches concrete task packets to `orchestration/agent_inbox/<agent>/`.
- Agents read their next packet with `python scripts\agent_worktrees.py brief --agent <agent>`.
- Non-trivial sprint work is plan-gated. After `handin`, workers create a Codex
  plan packet with `python scripts\agent_worktrees.py plan --agent <agent>
  --task <task> ...`, show the same plan in their GUI, then stop. Coding starts
  only after the user/Codex says `complete sprint task`.
- During the plan gate, workers may create, commit, and push implementation-plan
  packets and minimum coordination status changes to Codex's inbox. This is not
  approval to change production code. For Antigravity, artifact approval means
  "submit the plan packet only" unless the user explicitly says
  `complete sprint task`.
- Agents capture off-scope follow-up ideas with
  `python scripts\agent_worktrees.py suggest-task --agent <agent> --title "..."`
  so Codex can triage them from `orchestration/agent_inbox/codex/`.
  Suggested packets are not permission to implement the work.
- Codex polls durable worker submissions with
  `python scripts\agent_worktrees.py poll --fetch`.
- Use `python scripts\agent_worktrees.py poll --fetch --include-codex-workers`
  only when a current Codex subagent worker is expected to have submitted on a
  `codex/<task>` branch. The default fast poll skips historic remote
  `codex/*` disposable worker refs.
  The default path includes Claude/Antigravity branches, submit-alert branches,
  and local Codex inbox packets, excluding remote disposable `codex/*` branches
  and the durable `codex/current` mirror.
- Codex records every reviewed submit/integration in `orchestration/integration_log.md`
  via `python scripts\agent_worktrees.py record-integration ...`.
- After each integration, Codex runs `python scripts\agent_worktrees.py audit --fetch`
  and, when appropriate, `python scripts\agent_worktrees.py retire-stale` to expose
  disposable worker worktrees that should be removed or manually reviewed.
- `retire-stale` is dry-run by default. It removes only clean disposable worker
  worktrees when called with `--apply`; dirty worktrees are reported, never removed.
- Only Codex, acting as orchestrator, advances `master` and `handoff/current` in
  parallel mode unless the user explicitly instructs otherwise.
- Codex must announce `HANDIN READY` before the user prompts external workers to
  run `handin`.
- After `HANDIN READY`, Ariadne should use Computer Use automatically when
  available to send external-worker `handin`, corrective nudge, and
  `complete sprint task` prompts. If Computer Use is unavailable, Ariadne asks
  Yuri for only the specific manual prompt needed.
- During a sprint, Codex must not push sprint work through to `master` until all
  active sprint agents, including any Codex subagent worker, have submitted or
  been explicitly stood down.
- Prefer batching non-urgent orchestration protocol edits until discussion
  settles. Codex should remind the user before launch when agreed protocol edits
  are pending.
- Every workstream must state files in scope, files out of scope, verification, and
  merge criteria.
- Agents should record concerns or disagreement in the "Dissent / Risks" field.
- Prefer grouping tactical sprints under a coherent phase programme. Sprints
  should be sized by product outcome rather than file count: backend, frontend,
  tests, and docs can share a sprint when they serve one clear user-visible or
  operational outcome.

## Transparency Routine

Use a single evidence chain for every parallel task:

1. Dispatch packet in `orchestration/agent_inbox/<agent>/`.
2. Worker submit creates a Codex review packet.
3. Codex review marks packets `integrated`, `superseded`, or `blocked`.
4. Codex records the outcome in `orchestration/integration_log.md`.
5. Codex runs `audit --fetch` and reports:
   - submitted work waiting for review
   - integration-log delta since the last poll
   - branch/baton/mirror alignment
   - stale disposable worktrees and whether they are clean or dirty
6. Clean stale disposable worktrees may be retired with `retire-stale --apply`.
   Dirty stale worktrees require explicit review or user-approved abandonment.

When reporting progress to the user, Codex should use this shape:

- **Polled:** what submissions/review packets were found.
- **Integrated:** what was accepted, repaired, rejected, or superseded.
- **Verified:** checks run and failures/warnings.
- **Deployed:** for `docs/` changes, whether GitHub Pages serves the expected
  cache-bust/version. If stale, run `gh api --method POST
  repos/yurifrusin/EMR4/pages/builds` and re-check the live URL.
- **Aligned:** which refs were pushed/realigned.
- **Retirement:** stale disposable worktrees removed or left for review.
- **User Review:** all feasible Codex-side/tool-enabled checks already run, any
  hotfixes made from those checks, and only the residual user review/testing
  Ariadne could not confirm with available tools; use "none required" with the
  reason when no manual testing remains. If residual user checks remain, provide
  concrete steps: setup, exact UI path, expected result, suspicious/failure
  signs, skippable items, and what evidence to report back.
- **Next Direction:** Codex's recommendation for the next project slice and any
  project-level concerns raised by the integrated agent work.

After every fully integrated batch, Codex updates
`orchestration/sprint_closeout.md` with:

- what changed
- Codex-run reviews/tests, residual user review, and anything not required
- detailed step-by-step instructions for residual Yuri-only checks
- what is not required before moving on
- known follow-up
- recommended next direction

## Reasoning Budget Guidance

Use maximum reasoning for:

- architecture decisions
- security/privacy/clinical-safety decisions
- schema and migration design
- integration reviews
- debugging unclear failures

Use medium/high reasoning for:

- implementing an already-approved plan
- focused backend route work
- frontend UI implementation from a clear spec
- test writing

Use lower reasoning only for:

- mechanical version bumps
- formatting
- simple copy/docs updates
- running known commands

The default pattern should be: think hard at planning and review boundaries, execute
at medium/high once the plan is stable, then think hard again before integration.

## Sprint 25: Status/Waiting-Area Proposal Retrofit

| Item | Value |
|---|---|
| Programme | Phase 2 Programme 2B - Safe Appointment Mutation Workbench |
| Status | Integrated locally with focused backend/frontend and Chrome/CDP smoke verification passing |
| Launch Gate | Complete; Claude and Antigravity plans accepted and implementation released with `complete sprint task` |
| Integration Gate | Complete locally; push, mirror realignment, and audit pending |
| Theme | Bring receptionist-facing status, check-in, and waiting-area changes under the same proposal-first safety rail as create/edit |

### Workstream S25-A - Backend Status/Waiting-Area Proposal Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-appointment-status-waiting-area-proposal-contract.md` |
| Goal | Plan and then extend appointment proposal contracts so status and waiting-area mutations can be preflighted before any write |
| In Scope | Backend appointment proposal schemas/routes/tests; deterministic block/warning/allow responses; practice/location/resource safety; no-write proposal behavior |
| Out of Scope | Diary frontend implementation, drag/drop/resize, recurrence, taskpane/Command Centre/Gemini, Resource Administration UI, patient duplicate workflow |
| Verification | Plan packet first; after approval focused appointment status/waiting-area/proposal pytest checks, import/check_backend as needed, and proof that proposal calls do not mutate appointments |
| Status | Integrated locally |

### Workstream S25-B - Diary Status/Waiting-Area Proposal Flow

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-status-waiting-area-proposal-flow.md` |
| Goal | Plan and then route diary status/check-in/waiting-area changes through proposal preflight before mutation, matching the create/edit Confirm & Save pattern |
| In Scope | `docs/diary/diary.{html,css,js}`, status controls, waiting-room/check-in affordances, proposal handling, smoke/live-test helpers, cache-busting |
| Out of Scope | Backend routes/models/tests/migrations, taskpane/Command Centre/Gemini, drag/drop/resize, recurrence, Resource Administration, patient duplicate review, broad visual redesign |
| Verification | Plan packet first; after approval `node --check docs/diary/diary.js`, smoke-mode allowed/blocked/warning/reset/API-failure checks, and Ariadne live Chrome/CDP checks after integration |
| Status | Integrated locally |

### Workstream S25-C - Ariadne Integration and Review

| Item | Value |
|---|---|
| Owner | Codex/Ariadne |
| Role | orchestrator |
| Branch | `master` only for orchestration docs and final integration |
| Goal | Review plans together, ensure backend/UI proposal semantics match, run all feasible tool-enabled tests including live browser checks, and leave only genuine Yuri-only checks if any |
| In Scope | Plan review, polling, integration sequencing, bounded repairs, closeout/user-test summary, next-sprint recommendation |
| Out of Scope | Acting as proof of a separate Codex worker submission or bypassing worker plan gates |
| Verification | `poll --fetch`, plan/review inspection, focused backend/frontend checks, Chrome/CDP/live diary smoke where relevant, `git diff --check` |
| Status | Integrated locally |

## Sprint 24: Appointment Edit Proposal Flow

| Item | Value |
|---|---|
| Programme | Phase 2 Programme 2B - Safe Appointment Mutation Workbench |
| Status | Integrated, pushed, mirrored, audited, and Ariadne live Chrome/CDP smoke passed |
| Launch Gate | Complete; plans accepted and implementation released with `complete sprint task` |
| Integration Gate | Complete |
| Theme | Route receptionist-facing appointment edit/reschedule through the formal non-mutating proposal layer before writing changes |

### Workstream S24-A - Backend Edit Proposal Contract Hardening

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-appointment-edit-proposal-contract-hardening.md` |
| Goal | Plan and then harden the backend `POST /appointments/proposals/update/{appointment_id}` contract only where needed for safe diary edit/reschedule preflight |
| In Scope | `app/routers/appointments.py`, `app/schemas/appointments.py`, focused update-proposal and adjacent appointment update tests, contract notes if needed |
| Out of Scope | Diary frontend implementation, taskpane/Command Centre, patient demographics, resource admin, migrations unless the plan proves a schema issue, Bernie runtime |
| Verification | Plan packet first; after approval `scripts/check_backend.ps1`, `tests/test_appointment_update_proposal.py`, adjacent booking/break tests if touched, `git diff --check` |
| Status | Integrated locally |

### Workstream S24-B - Diary Edit Proposal UI Flow

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-edit-proposal-flow.md` |
| Goal | Plan and then make appointment edit/reschedule saves call the update proposal endpoint before the actual `PUT`, mirroring the existing create-proposal Confirm & Save flow |
| In Scope | `docs/diary/diary.{html,css,js}`, edit modal proposal call, safe/warning/blocked copy, Confirm & Save state reset, smoke-mode simulation, cache-bust |
| Out of Scope | Backend route/schema changes, create-proposal behaviour except shared helper reuse, taskpane/Command Centre, Waiting Room panel layout, Resource Administration, drag/drop/resize, Bernie runtime |
| Verification | Plan packet first; after approval `node --check docs/diary/diary.js`, `npm run validate-all`, smoke/browser notes for edit safe/warning/blocked flows where feasible, `git diff --check` |
| Status | Integrated locally |

### Workstream S24-C - Ariadne Integration and Review

| Item | Value |
|---|---|
| Owner | Codex/Ariadne |
| Role | orchestrator |
| Branch | `master` only for orchestration docs after worker plans are accepted or during closeout |
| Goal | Review proposal-contract and UI plans together, verify create/edit proposal compatibility, run feasible backend/frontend/browser checks, and produce detailed Yuri-only residual review steps if any |
| In Scope | Plan review, integration sequencing, bounded repairs, closeout/user-test summary, next-sprint recommendation |
| Out of Scope | Acting as proof of a separate Codex worker submission or bypassing worker plan gates |
| Verification | `poll --fetch`, plan/review inspection, backend/frontend checks, browser/Chrome checks if available, `git diff --check` |
| Status | Ariadne-owned |

## Sprint 23: Room Default Waiting-Area Invariant

| Item | Value |
|---|---|
| Status | Integrated locally with focused verification passing |
| Launch Gate | Complete; packets submitted by Claude and Antigravity; no Codex worker expected |
| Integration Gate | Complete; push, mirror realignment, audit, and live Pages v84 review pending |
| Theme | Ensure every active room has a valid default waiting area so reception/admin state stays coherent after room or waiting-area changes |

### Workstream S23-A - Backend Default Waiting-Area Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-room-default-waiting-area-contract.md` |
| Goal | Plan and then enforce a safe backend invariant that every active room has a valid active default waiting area where possible |
| In Scope | Room/WaitingArea backend models, schemas, resource-admin routes/services, seed/dev-data repair, migrations only if required, focused pytest coverage |
| Out of Scope | Diary frontend UI, taskpane/Command Centre, appointment booking/status semantics beyond preserving existing consumers, broad roster redesign |
| Verification | Plan packet first; after approval focused resource-admin/default-waiting-area pytest coverage, backend Tier-1 check, full pytest if shared fixtures are touched, `git diff --check` |
| Status | Integrated |

### Workstream S23-B - Resource Admin Default Waiting-Area UI

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-room-default-waiting-area-ui.md` |
| Goal | Plan and then make room default waiting areas visible/editable in Resource Administration without regressing existing room/waiting-area flows |
| In Scope | `docs/diary/diary.{html,css,js}`, source/deployed asset sync and cache-bust if needed, default/fallback UI messaging, smoke/browser checks |
| Out of Scope | Backend contract changes, migrations, taskpane/Command Centre, appointment booking/status UI, roster admin redesign, drag/drop/resize |
| Verification | Plan packet first; after approval JS syntax, `npm run validate-all`, local/deployed asset version checks, smoke/live browser checks, `git diff --check` |
| Status | Integrated |

### Workstream S23-C - Ariadne Integration and Review Harness

| Item | Value |
|---|---|
| Owner | Codex/Ariadne |
| Role | orchestrator |
| Branch | `master` only for orchestration docs after worker plans are accepted or during closeout |
| Goal | Review both plans for invariant/UI compatibility, then run all feasible backend/frontend/browser checks before asking Yuri for any residual user review |
| In Scope | Plan review, integration sequencing, bounded repairs, closeout/user-test summary, and next-sprint recommendation |
| Out of Scope | Acting as proof of a separate Codex worker submission or bypassing worker plan gates |
| Verification | `poll --fetch`, plan/review inspection, backend/frontend checks, browser/Chrome checks if runtime UI changes land, `git diff --check` |
| Status | Integrated locally; closeout/push/audit pending |

## Sprint 22: Development Tooling Optimisation

| Item | Value |
|---|---|
| Status | Integrated locally with verification passing |
| Launch Gate | Complete |
| Integration Gate | Complete; push, mirror realignment, and audit pending |
| Theme | Improve EMR4's AI-assisted development feedback loops before the next product-growth sprint |

### Workstream S22-A - Backend Dev Loop Tooling

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-backend-dev-loop-tooling.md` |
| Goal | Plan and then improve backend development feedback loops so Ariadne and workers can run fast, reliable checks before residual user review |
| In Scope | Backend/dev-environment tooling, pytest/static-check ergonomics, startup verification, backend check-tier documentation, small scripts/config that reduce false starts |
| Out of Scope | Product behaviour, diary/taskpane UI, migrations, schema changes, WhatsApp production send behaviour, security alert dismissal, broad dependency upgrades |
| Verification | Plan packet first; after approval app import/startup check, proposed focused checks, `run_dev` or equivalent non-destructive probe where feasible, `git diff --check` |
| Status | Integrated |

### Workstream S22-B - Frontend Browser Dev Tooling

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-frontend-browser-dev-tooling.md` |
| Goal | Plan and then improve diary/taskpane frontend and browser-feedback loops so UI affordance regressions are caught by tools before Yuri is asked to test |
| In Scope | Diary/taskpane smoke commands, browser/check scripts, local/deployed asset version checks, npm script ergonomics, Antigravity/Gemini-assisted UI QA notes |
| Out of Scope | Product UI behaviour changes, visual redesign, backend API contracts, migrations, patient/clinical flows, production WhatsApp sending, forced broad dependency upgrades |
| Verification | Plan packet first; after approval JS/build/validate or smoke commands, local/deployed asset URL checks where feasible, `git diff --check`, browser/visual observations |
| Status | Integrated |

### Workstream S22-C - Ariadne Architecture and Tooling Harness

| Item | Value |
|---|---|
| Owner | Ariadne/orchestrator Codex |
| Role | orchestrator |
| Branch | `master` only for orchestration docs after worker plans are accepted or during closeout |
| Goal | Review Sprint 22 plans against the software-fundamentals architecture frame: shared design language, fast feedback loops, TDD-sized increments, deep-module boundaries, and residual user-test discipline |
| In Scope | Plan review, integration checklist, closeout wording, and next-sprint architecture/tooling recommendations |
| Out of Scope | Acting as proof of a separate Codex worker submission, production feature implementation, or bypassing worker plan gates |
| Verification | `poll --fetch`, plan/review inspection, feasible local/browser checks before closeout, `git diff --check` for orchestration updates |
| Status | Integrated |

## Sprint 20: Security Baseline

| Item | Value |
|---|---|
| Status | Integrated locally after plan-gated review |
| Launch Gate | Complete |
| Integration Gate | Complete; observe GitHub Actions after push |
| Theme | Add a small repeatable security baseline before deeper product work |

### Workstream S20-A - Python Security Baseline

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-python-security-baseline.md` |
| Goal | Add fast backend/Python dependency and static-analysis security checks |
| In Scope | Python security workflow/tooling notes, likely `pip-audit` and Bandit, deterministic commands Ariadne can rerun, plus Claude Code tool/plugin recommendations |
| Out of Scope | Runtime app behavior, migrations, diary/taskpane UI, Node/Office audit |
| Verification | New local security commands where feasible; YAML validation/diff checks; exact command output in completion notes |
| Status | Integrated |

### Workstream S20-B - Node Office Security Baseline

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-node-security-baseline.md` |
| Goal | Add repeatable Office add-in dependency audit and validation checks |
| In Scope | Node/Office audit workflow or metadata, `EMR4 Sidebar` package audit reproducibility, concise local command notes, plus Antigravity/Gemini tool/plugin recommendations |
| Out of Scope | Runtime frontend behavior, diary/taskpane asset changes, backend/Python security checks |
| Verification | `npm audit`/Office validation where feasible; `git diff --check`; exact command output in completion notes |
| Status | Integrated |

### Workstream S20-C - Security Review Harness

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/security-review-harness` |
| Task Packet | `orchestration/agent_inbox/codex/codex-security-review-harness.md` |
| Goal | Configure CodeQL/Dependabot coordination and create Ariadne's Sprint 20 security review checklist |
| In Scope | CodeQL/Dependabot config, `orchestration/security_baseline_review.md`, Codex Security review path, installed Codex tool/skill inventory |
| Out of Scope | Production code, migrations, runtime frontend/backend behavior, duplicating Claude/Antigravity workflows |
| Verification | `git diff --check`, YAML validation where feasible, documented Codex Security scan/review path |
| Status | Integrated |

## Sprint 21: Security Alert Triage and Focused Remediation

| Item | Value |
|---|---|
| Status | Integrated locally with verification passing |
| Launch Gate | Complete |
| Integration Gate | Complete; Codex worker stood down after repeated local tooling blockers and Ariadne completed the triage harness |
| Theme | Turn Sprint 20 security signals into bounded fixes and an Ariadne-facing alert triage harness |

### Workstream S21-A - Consultation CodeQL Fixes

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-consultation-codeql-fixes.md` |
| Goal | Address high/medium CodeQL findings in `app/routers/consultation.py` without changing successful API behaviour |
| In Scope | Path cleanup validation, sensitive-content logging reduction, bounded error responses, focused tests if adjacent |
| Out of Scope | UI, diary/taskpane assets, migrations, RBAC redesign, Gemini prompt redesign |
| Verification | Focused py_compile/pytest/Bandit commands recorded in Completion Notes |
| Status | Integrated |

### Workstream S21-B - Node Security Workflow Triage

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-node-security-workflow-triage.md` |
| Goal | Improve Node/Office security workflow signal quality while preserving a clean production audit gate |
| In Scope | `.github/workflows/node-security.yml`, `EMR4 Sidebar/package*.json` only if the plan proves a safe metadata/update change |
| Out of Scope | Runtime diary/taskpane UI, backend, forced major build-tool upgrades |
| Verification | `npm run validate`, `npm audit --omit=dev`, and non-blocking full `npm audit` where feasible |
| Status | Integrated |

### Workstream S21-C - Security Alert Triage Harness

| Item | Value |
|---|---|
| Owner | Codex worker/security-manager |
| Branch | `codex/security-alert-triage` |
| Task Packet | `orchestration/agent_inbox/codex/codex-security-alert-triage-harness.md` |
| Goal | Inventory GitHub security alerts with `gh`, classify fix-now/defer/noise, and preserve a redacted Ariadne review harness |
| In Scope | `orchestration/security_alert_triage.md`, read-only `gh` security queries, links to existing security baseline notes |
| Out of Scope | Production code changes, alert dismissal, cloud/key rotation, master/handoff integration |
| Verification | `gh auth status`, CodeQL/secret/Dependabot/workflow queries, secret-safe report review |
| Status | Superseded by Ariadne-owned `orchestration/security_alert_triage.md` |

### Deferred Product Follow-Up

- Future resource-admin work should ensure every active room always has a
  default waiting area. A sensible default is the active waiting area with
  display order `0` when no room-specific default has been selected.

## Sprint 19: Resource Admin Foundations

| Item | Value |
|---|---|
| Sprint Goal | Add the first safe admin path for physical rooms and waiting areas so reception/admin can maintain Phase 2 diary resources without confusing locations, rooms, diary views, waiting areas, appointment status, or patient identity |
| Dispatch Mode | Plan-gated parallel sprint |
| Start State | `master`, `handoff/current`, and durable worker mirrors aligned at `d78659a` after Sprint 18 closeout |
| User Review Dependency | None before planning; implementation plans must be reviewed before coding |
| Integration Rule | Do not push Sprint 19 work to `master` until Claude, Antigravity, and any Codex worker have submitted or been explicitly stood down |
| Status | Integrated; pending push/deploy and user review |

### Workstream A - Backend Room and Waiting-Area Admin Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-diary-resource-admin-contract.md` |
| Goal | Plan, then after approval implement the smallest role-gated backend admin contract for rooms and waiting areas |
| In Scope | `app/schemas/diary.py`, `app/routers/diary.py`, focused `tests/test_diary_resource_admin.py`; `GET /diary/rooms`; create/update/archive for `Room` and `WaitingArea`; Admin/PracticeOwner RBAC; practice and location scoping; archive semantics; room `default_waiting_area_id` validation |
| Out of Scope | Diary frontend, roster writes, diary template editing, appointment mutation semantics, migrations unless the approved plan proves one is needed, full practice admin UI, patient merge, Bernie runtime, audit-log platform |
| Verification | Plan packet first; after approval backend py_compile plus focused resource-admin tests and adjacent `test_location_scoped_diary.py`, `test_diary_roster.py`, and `test_waiting_area_contract.py` coverage |
| Plan Gate | Required before coding |
| Merge Criteria | Admin writes cannot leak cross-practice data; inactive/archive preserves historical references; room defaults cannot point at cross-location/cross-practice waiting areas; existing diary read endpoints keep working |
| Dissent / Risks | Display-order uniqueness and archive behaviour may expose existing dev-data assumptions; do not introduce non-person bookable resources in this slice |
| Status | Integrated |

### Workstream B - Diary Resource Admin First Slice

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-resource-admin-ui.md` |
| Goal | Plan, then after approval add a restrained diary-admin surface for rooms and waiting areas using the Workstream A API contract |
| In Scope | `docs/diary/diary.html`, `docs/diary/diary.css`, `docs/diary/diary.js`; active-location context; list/create/edit/archive controls for rooms and waiting areas; default waiting-area selection for rooms; clear success/failure feedback; cache bust if assets change |
| Out of Scope | Backend changes, roster editor, diary template editor, appointment create/edit/status logic, main diary appointment geometry, Waiting Room card layout, taskpane, Command Centre, duplicate merge, Bernie runtime |
| Verification | Plan packet first; after approval `node --check docs\diary\diary.js`, `git diff --check`, and manual visual notes for one-location and multi-location resource admin flows |
| Plan Gate | Required before coding |
| Merge Criteria | One-location diary remains uncluttered; multi-location context remains explicit; admin controls do not mutate appointments or waiting-room attendance state; API errors are visible and recoverable |
| Dissent / Risks | This depends on Workstream A's final route/payload shape; if backend scope changes, UI should stop at a plan or adapter shell rather than guessing |
| Status | Integrated |

### Workstream C - Resource Admin Review Harness

| Item | Value |
|---|---|
| Owner | Codex worker or orchestrator |
| Branch | Unique `codex/<short-task-name>` worker branch, or direct orchestrator docs if no worker is launched |
| Task Packet | `orchestration/agent_inbox/codex/codex-resource-admin-review-harness.md` |
| Goal | Prepare the integration and user-review harness for resource admin without duplicating backend or frontend implementation scopes |
| In Scope | Orchestration review docs, API spot-check snippets, user review checklist, closeout scaffolding, and vocabulary guardrails tying back to `orchestration/resource_admin_bernie_tool_design.md` |
| Out of Scope | Production backend/frontend code, migrations, taskpane, Command Centre, appointment mutations, patient merge, autonomous Bernie runtime |
| Verification | Plan packet first if launched as a worker; after approval `git diff --check` and snippet sanity review against the final submitted backend API |
| Plan Gate | Required before coding if launched as worker |
| Merge Criteria | Review harness names the exact surfaces to test and not test; keeps room/resource/waiting-area/location language separate; preserves agent dissent/risks from submitted plans |
| Dissent / Risks | If Codex keeps this direct, no external worker handin is needed for Workstream C; if launched as a subagent, use normal submit and include it in the integration gate |
| Status | Integrated |

## Sprint 18: Patient-Admin Safety and Duplicate Visibility

| Item | Value |
|---|---|
| Sprint Goal | Make duplicate patient records visible and safer to reason about, while tightening the taskpane patient search/save feedback that led to confusion during review |
| Dispatch Mode | Plan-gated parallel sprint |
| Start State | `master`, `handoff/current`, and durable worker mirrors aligned at Sprint 17 closeout |
| User Review Dependency | None before planning; implementation plans must be reviewed before coding |
| Integration Rule | Do not push sprint work to `master` until Claude, Antigravity, and the Codex worker have submitted or been explicitly stood down |
| Status | Integrated, deployed, and user-reviewed; see `orchestration/sprint_closeout.md` |

### Workstream A — Backend Duplicate Review Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-patient-duplicate-review-api.md` |
| Goal | Plan, then after approval implement a read-only backend duplicate-patient review contract |
| In Scope | Patient duplicate review schemas/router/tests; same-name+DOB groups; Medicare+IRN and IHI strong-identifier groups; reference counts where practical; practice isolation |
| Out of Scope | Frontend UI, patient merge/delete mutation, manual DB deletion, production data migrations |
| Verification | Plan packet first; after approval focused pytest for duplicate review API and relevant patient tests |
| Plan Gate | Required before coding |
| Status | Integrated |

### Workstream B — Taskpane Patient Search and Alert Clarity

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-taskpane-patient-search-and-alerts.md` |
| Goal | Plan, then after approval improve full-name patient search and make patient-details save failures obvious without scrolling |
| In Scope | Taskpane HTML/JS/CSS only; cache bust; patient search and patient-details save feedback |
| Out of Scope | Backend changes, diary changes, Command Centre redesign, patient merge/delete implementation |
| Verification | Plan packet first; after approval JS syntax check plus manual taskpane verification notes |
| Plan Gate | Required before coding |
| Status | Integrated |

### Workstream C — Dev Duplicate Audit Helper

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | unique `codex/<short-task-name>` worker branch |
| Task Packet | `orchestration/agent_inbox/codex/codex-dev-data-duplicate-audit-tool.md` |
| Goal | Plan, then after approval add a read-only developer helper for inspecting duplicate patients and references |
| In Scope | `scripts/` helper or equivalent command path; dummy-guide update; read-only output by default |
| Out of Scope | Automatic deletion, patient merge mutation, production admin UI, app runtime behaviour changes |
| Verification | Plan packet first; after approval run helper against dev DB if available and confirm safe failure without DB settings |
| Plan Gate | Required before coding |
| Status | Integrated |

## Sprint 17: Command/Proposal Workflow Retrofit

| Item | Value |
|---|---|
| Status | Dispatched; plan gate pending |
| Launch Gate | HANDIN READY after dispatch commit/push/audit |
| Implementation Gate | Pending worker plans and Codex approval |
| Theme | Retrofit high-risk receptionist workflows onto the formal command/proposal layer before adding Bernie runtime |

### Workstream AX - Appointment Update Proposal Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-appointment-update-proposal-contract.md` |
| Goal | Plan, then after approval implement backend proposal contract(s) for editing, rescheduling, cancelling, and/or status-changing an existing appointment without mutating until staff confirmation |
| In Scope | Appointment schemas/router/tests; non-mutating proposal endpoint(s); typed command payloads; conflict, break, provisional-identity, terminal/cancellation, and waiting-area/status warnings if touched |
| Out of Scope | Diary frontend, taskpane, Command Centre, Bernie runtime, migrations unless necessary, patient demographics, room/location admin, drag/drop/resize, SMS/reminder confirmation, billing/finalisation |
| Verification | Plan packet first; after approval backend py_compile, focused pytest, adjacent booking/status/break tests, `git diff --check` |
| Plan Gate | Required before coding |
| Status | Dispatched |

### Workstream AY - Diary Create Proposal Flow

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-create-proposal-flow.md` |
| Goal | Plan, then after approval make the diary booking modal call `POST /api/v1/appointments/proposals/create` before writing a new booking |
| In Scope | `docs/diary/diary.{html,css,js}`; cache-bust if diary assets change; booking-create modal proposal, block, warning, and confirmation flow only |
| Out of Scope | Backend route/schema changes, taskpane, Command Centre, Waiting Room panel layout, main diary appointment geometry, location selector redesign, patient demographics, Bernie runtime, drag/drop/resize |
| Verification | Plan packet first; after approval `node --check docs\diary\diary.js`, `git diff --check`, visual/manual notes for safe create, conflict block, break warning, and provisional warning if supported |
| Plan Gate | Required before coding |
| Status | Dispatched |

### Workstream AZ - Command Proposal Review Harness

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/command-proposal-review-harness` |
| Task Packet | `orchestration/agent_inbox/codex/codex-command-proposal-review-harness.md` |
| Goal | Plan, then after approval create the review harness and developer-facing API snippets for the formal command/proposal layer |
| In Scope | Orchestration docs, sprint closeout/review harness updates, developer guide snippets where useful, PowerShell/API examples for proposal safe/warning/blocked paths |
| Out of Scope | Production backend/frontend changes, migrations, diary UI, taskpane, Command Centre, Bernie runtime, modifying Claude/Antigravity packets after dispatch |
| Verification | Plan packet first; after approval `git diff --check` plus executable snippet/schema verification if practical |
| Plan Gate | Required before coding |
| Status | Dispatched |

## Sprint 16: Location-Aware Diary Foundations

| Item | Value |
|---|---|
| Status | Integrated |
| Launch Gate | Complete |
| Implementation Gate | Complete |
| Theme | Make the diary/resource model explicitly location-aware while separating physical sites from diary screen/page views |

### Workstream AU - Location-Scoped Diary Backend Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-location-scoped-diary-contract.md` |
| Goal | Plan, then after approval implement, the smallest backend changes needed so diary templates, rooms, waiting areas, rosters, and appointments do not assume one physical location per practice |
| In Scope | Backend models/schemas/routers/tests around `PracticeLocation`, `Room`, `WaitingArea`, `DiaryTemplate`, `DiaryRoster`, `Appointment.location_id`, seed/test data, migrations only if needed |
| Out of Scope | Diary frontend, taskpane, Command Centre, full practice/location admin UI, drag/drop/resize, online booking portal, Bernie runtime |
| Verification | Plan packet first; after approval, focused location/diary/appointment pytest, backend py_compile, migration check if changed, `git diff --check` |
| Plan Gate | Required before coding |
| Status | Integrated |

### Workstream AV - Diary Location Selector and View Boundary

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-location-selector-view-boundary.md` |
| Goal | Plan, then after approval implement, a restrained diary UI path for choosing/indicating the active physical location and preserving the distinction from diary page/column-group views |
| In Scope | `docs/diary/diary.{html,css,js}` and cache-bust; frontend consumption of existing/new location-aware diary APIs if available; no broad redesign |
| Out of Scope | Backend schema/routes/tests, taskpane, Command Centre, drag/drop/resize, full admin UI, Bernie runtime, appointment-card geometry changes |
| Verification | Plan packet first; after approval, `node --check docs\diary\diary.js`, `git diff --check`, live/smoke visual notes for one-location fallback and multi-location affordance |
| Plan Gate | Required before coding |
| Status | Integrated |

### Workstream AW - Location and Diary View Design Harness

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/location-diary-view-design-harness` |
| Task Packet | `orchestration/agent_inbox/codex/codex-location-diary-view-design-harness.md` |
| Goal | Plan, then after approval prepare the design guardrails, user-review checklist, and future Bernie tool vocabulary for practice vs location vs room/resource vs waiting area vs diary page/view group |
| In Scope | Orchestration docs, implementation-plan notes, review harness, API/user-test snippets if useful |
| Out of Scope | Production backend/frontend implementation, migrations, taskpane/Command Centre, autonomous Bernie runtime, drag/drop/resize |
| Verification | Plan packet first; after approval, `git diff --check` |
| Plan Gate | Required before coding |
| Status | Integrated |

## Sprint 15: Plan-Gated Waiting Room Check-In Operations

| Item | Value |
|---|---|
| Status | Integrated |
| Launch Gate | Complete |
| Implementation Gate | Complete |
| Theme | Make Waiting Room check-in operational while preserving room/resource/waiting-area terminology and avoiding diary-grid churn |

### Workstream AR - Waiting Area Check-In Defaults

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-waiting-area-checkin-defaults.md` |
| Goal | Plan, then after approval implement, backend defaults/clearing semantics for waiting-area assignment during check-in/status transitions |
| In Scope | Appointment status/update semantics, waiting-area assignment/defaulting/clearing tests, practice scoping, inactive/cross-practice guards, terminal status policy |
| Out of Scope | Diary frontend, taskpane, room/admin UI, Bernie runtime, SMS/email/voice reminder confirmation, billing/finalisation locking, drag/drop/resize |
| Verification | Plan packet first; after approval, focused pytest, backend py_compile, `git diff --check` |
| Plan Gate | Required before coding |
| Status | Integrated |

### Workstream AS - Diary Check-In Waiting-Area UI

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-checkin-waiting-area-ui.md` |
| Goal | Plan, then after approval implement, Waiting Room side-panel check-in with visible/default waiting-area assignment and denser Expected Today display |
| In Scope | `docs/diary/diary.{html,css,js}` and diary cache-bust; Waiting Room side-panel only |
| Out of Scope | Backend routes/models/tests/migrations, taskpane, Command Centre, booking modal semantics beyond existing status/check-in API, main diary grid appointment positioning, drag/drop/resize, Bernie runtime |
| Verification | Plan packet first; after approval, `node --check docs\diary\diary.js`, `git diff --check`, visual acceptance notes |
| Plan Gate | Required before coding |
| Status | Integrated |

### Workstream AT - Waiting Room Review Harness

| Item | Value |
|---|---|
| Owner | Codex |
| Branch | `codex/current` or disposable Codex worker branch |
| Task Packet | `orchestration/agent_inbox/codex/codex-waiting-room-review-harness.md` |
| Goal | Plan, then after approval prepare review scripts/checklists and guardrails for room-to-waiting-area defaults and Waiting Room user review |
| In Scope | Orchestration docs, sprint closeout draft/checklist, PowerShell API snippets, design guardrails |
| Out of Scope | Production backend/frontend code, migrations, taskpane/Command Centre, Bernie runtime, drag/drop/resize, duplicating Claude/Antigravity scopes |
| Verification | Plan packet first; after approval, `git diff --check` |
| Plan Gate | Required before coding |
| Status | Integrated |

## Sprint 14: Plan-Gated Receptionist Workflow Foundations

| Item | Value |
|---|---|
| Status | Integrated |
| Launch Gate | Complete |
| Implementation Gate | Complete |
| Theme | Clarify receptionist workflow semantics before further diary/Waiting Room coding or Bernie tools |

### Workstream AO - Waiting Area Check-In Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-waiting-area-checkin-contract.md` |
| Goal | Plan, then after approval implement, the backend contract for assigning waiting areas during check-in and status transitions |
| In Scope | Appointment status/update semantics, waiting-area assignment, practice scoping, patient identity/status separation, focused backend tests |
| Out of Scope | Diary frontend, taskpane, room admin UI, Bernie implementation, SMS/reminder confirmation, billing/finalisation locking |
| Verification | Plan packet first; after approval, focused pytest and backend py_compile |
| Plan Gate | Required before coding |
| Status | Integrated |

### Workstream AP - Diary Waiting Room UX Clarity

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-waiting-room-ux-clarity.md` |
| Goal | Plan, then after approval implement, Waiting Room side-panel clarity improvements for receptionist workflow |
| In Scope | `docs/diary/` Waiting Room panel only: area tabs, panel counts, card density/stacking inside the side panel, action wording |
| Out of Scope | Diary grid appointment positioning, booking slot geometry, booking modal semantics, backend, taskpane, drag/drop/resize, Bernie |
| Verification | Plan packet first; after approval, `node --check docs\diary\diary.js`, `git diff --check`, visual acceptance notes |
| Plan Gate | Required before coding |
| Status | Integrated |

### Workstream AQ - Resource Admin and Bernie Tool Design

| Item | Value |
|---|---|
| Owner | Codex |
| Branch | `codex/resource-admin-bernie-tool-design` |
| Task Packet | `orchestration/agent_inbox/codex/codex-resource-admin-bernie-tool-design.md` |
| Goal | Plan the resource/admin foundation and safe Bernie tool boundaries needed before supervised receptionist assistance |
| In Scope | Design docs, implementation-plan notes, future endpoint/tool boundaries, room/resource/waiting-area terminology |
| Out of Scope | Production UI, autonomous Bernie actions, LLM agent runtime, schema migration unless plan-approved, drag/drop/resize |
| Verification | Plan packet first; after approval, docs diff check or explicit code checks if implementation is approved |
| Plan Gate | Required before coding |
| Status | Integrated |

## Sprint 13: Waiting Areas, Patient Editing, and Bernie Prerequisites

| Item | Value |
|---|---|
| Status | Integrated |
| Launch Gate | Complete |
| Integration Gate | Complete |
| Theme | Build the room/waiting-area and patient-edit foundations Bernie will need later, without starting autonomous copilot work yet |

### Workstream AL - Waiting Area Resource Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-waiting-area-resource-contract.md` |
| Goal | Add the minimal backend contract for named physical waiting areas linked to rooms/resources and waiting-room filtering/grouping |
| In Scope | `app/models/tenancy.py`, `app/models/diary.py`, `app/schemas/diary.py`, `app/schemas/appointments.py`, `app/routers/diary.py`, `app/routers/appointments.py`, Alembic migration if needed, `seed.py`, focused tests, plus `tests/conftest.py` only for pgvector test fixture hardening |
| Out of Scope | Diary frontend, taskpane/Command Centre, Bernie implementation, patient-edit UI, drag/drop/resize, SMS, billing/completion, ADHA/IHI live integration |
| Verification | Focused waiting-room/diary/appointment pytest, fresh-DB pgvector fixture check if `tests/conftest.py` changes, migration checks if needed, backend compile check, `git diff --check` |
| Status | Queued |

### Workstream AM - Diary Waiting Area Tabs

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-waiting-area-tabs.md` |
| Goal | Make the diary patient-flow panel support physical waiting-area tabs/groups while preserving simple fallback behaviour |
| In Scope | `docs/diary/diary.{html,css,js}` and diary cache-bust only |
| Out of Scope | Backend routes/models/tests/migrations, taskpane/Command Centre, Bernie implementation, patient edit details UI, drag/drop/resize, SMS, billing/completion |
| Verification | `node --check docs\diary\diary.js`, `git diff --check`, live/smoke checks for no-area fallback, multiple areas, linked/provisional action, narrow layout, and status changes |
| Status | Queued |

### Workstream AN - Patient Edit Details Foundation

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/patient-edit-details-foundation` |
| Task Packet | `orchestration/agent_inbox/codex/codex-patient-edit-details-foundation.md` |
| Goal | Add safe patient-detail editing for the loaded patient while preserving hard duplicate protections |
| In Scope | `app/routers/patients.py`, `app/schemas/patients.py`, `tests/test_patients.py`, `EMR4 Sidebar/src/taskpane/taskpane.{html,css,js}`, synced `docs/taskpane/*`, taskpane cache-bust if assets change |
| Out of Scope | Diary frontend, waiting-area backend contract, appointment routes/models, Command Centre clinical coding, generated Word document rewrite, OneDrive import tooling, ADHA/IHI live verification, OCR, Bernie implementation |
| Verification | Focused patient pytest, taskpane JS syntax checks on source/docs, `sync_taskpane.py` if source changes, `git diff --check`, edit/cancel/save/duplicate-block smoke notes |
| Status | Queued |

## Sprint 12: Provisional Booking Link and State Model

| Item | Value |
|---|---|
| Status | Integrated locally |
| Launch Gate | Complete |
| Integration Gate | Complete |
| Theme | Finish the practical provisional-to-linked-patient booking workflow while clarifying appointment state and waiting-area semantics before drag/drop/resize |

### Workstream AI - Provisional Booking Link Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-provisional-link-contract.md` |
| Goal | Finish the backend contract for linking provisional appointments to existing patient records while preserving patient identity/linkage versus attendance status separation |
| In Scope | Appointment/diary backend models, schemas, routers, focused tests, migration only if needed, seed/test helpers only if needed |
| Out of Scope | Diary frontend, taskpane/Command Centre, drag/drop/resize, SMS confirmation, billing/completion workflow, full waiting-area model, real ADHA/IHI integration |
| Verification | Focused appointment patient-link/create-edit/status/conflict tests, touched diary break/roster tests, migration check if needed, `git diff --check` |
| Status | Integrated |

### Workstream AJ - Diary Provisional Patient Linking

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-link-provisional-patient.md` |
| Goal | Add diary UI to link a provisional/free-text booking to an existing patient record and warn before saving bookings that cross break blocks |
| In Scope | `docs/diary/diary.{html,css,js}` and diary cache-bust if assets change |
| Out of Scope | Backend routes/models/tests/migrations, taskpane/Command Centre, drag/drop/resize, SMS workflow, billing/completion workflow, full waiting-area model |
| Verification | `node --check docs\diary\diary.js`, `git diff --check`, smoke/live checks for provisional create, link, status warning, break-crossing warning, narrow layout, and failures |
| Status | Integrated |

### Workstream AK - Appointment State and Waiting-Area Model

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/appointment-state-waiting-area-model` |
| Task Packet | `orchestration/agent_inbox/codex/codex-appointment-state-and-waiting-area-model.md` |
| Goal | Produce the design note and review harness for appointment identity/status/waiting-area semantics before drag/drop/resize |
| In Scope | Orchestration/design docs, implementation-plan notes if appropriate, Sprint 12 review checklist, exact PowerShell API snippets for user review |
| Out of Scope | Production backend/frontend implementation, migrations, diary/taskpane feature work, Gemini/AI, billing implementation, real ADHA/IHI integration |
| Verification | `git diff --check`; focused syntax/check only if any helper script is added |
| Status | Integrated |

## Sprint 11: Patient-Link Semantics and New Patient Safety

| Item | Value |
|---|---|
| Status | Integrated locally |
| Launch Gate | Complete |
| Integration Gate | Complete |
| Theme | Split patient identity/linkage from appointment attendance while hardening New Patient duplicate handling |

### Workstream AF - Appointment Patient-Link Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-appointment-patient-link-contract.md` |
| Goal | Make the backend distinguish linked patient records from provisional free-text diary names, without treating Confirmed as an attendance state |
| In Scope | Appointment model/schema/router/tests, migration if needed, focused appointment create/edit/status/waiting-room/conflict tests |
| Out of Scope | Diary frontend, taskpane/Command Centre UI, drag/drop/resize, SMS reminder confirmation, billing/completion guard design beyond noting risks |
| Verification | Focused appointment pytest, migration check if a migration is added, `git diff --check` |
| Status | Integrated |

### Workstream AG - Diary Patient-Link UI Semantics

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-patient-link-ui.md` |
| Goal | Make linked versus provisional patient identity legible in the diary and remove Confirmed from routine attendance-status treatment |
| In Scope | `docs/diary/diary.{html,css,js}` and cache-bust if assets change |
| Out of Scope | Backend routes/models/tests/migrations, taskpane/Command Centre, drag/drop/resize, SMS reminder workflow, billing/completion workflow |
| Verification | `node --check docs\diary\diary.js`, live/smoke visual checks where possible, `git diff --check` |
| Status | Integrated |

### Workstream AH - New Patient Duplicate Workflow

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/new-patient-duplicate-workflow` |
| Task Packet | `orchestration/agent_inbox/codex/codex-new-patient-duplicate-workflow.md` |
| Goal | Harden New Patient creation with cancel/escape/success paths and duplicate-candidate warning before record/file creation |
| In Scope | `EMR4 Sidebar/src/taskpane/taskpane.{html,css,js}`, mirrored `docs/taskpane/*` via `sync_taskpane.py`, focused checks/tests if available |
| Out of Scope | Diary frontend, appointment patient-link backend, Command Centre clinical coding, OneDrive import tooling, ADHA/IHI live integration, OCR |
| Verification | `node --check` on taskpane JS source and docs copy, `git diff --check`, `sync_taskpane.py` if source changes, focused patient tests if backend is touched |
| Status | Integrated |

## Sprint 10: Nurse Bookability and Patient Identity Foundation

| Item | Value |
|---|---|
| Status | Integrated locally |
| Launch Gate | Complete |
| Integration Gate | Complete |
| Theme | Make Nurse/Room 2 deliberately bookable via a practitioner-backed resource while starting the safer patient-identity foundation in a separate lane |

### Workstream AC - Nurse Practitioner Dev-Data Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-nurse-practitioner-dev-data-contract.md` |
| Goal | Make Room 2/Nurse deliberately bookable by representing Nurse as a real practitioner/staff resource in dev data and tests |
| In Scope | `seed.py`, focused diary roster/template tests, focused appointment create/edit/slots tests, minimal backend fixes only if the current contract blocks safe nurse representation |
| Out of Scope | Diary frontend, taskpane/Command Centre, patient identity/duplicate work, waiting-area UI, room/resource-only bookings without `practitioner_id`, drag/drop/resize |
| Verification | Focused diary roster/template and appointment/slots pytest suites plus `git diff --check` |
| Status | Integrated |

### Workstream AD - Diary Nurse Bookability Affordance

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-nurse-bookability-affordance.md` |
| Goal | Make practitioner-backed Nurse/Room 2 columns clearly bookable while label-only/non-practitioner columns remain visibly non-bookable |
| In Scope | `docs/diary/diary.{html,css,js}` and cache-bust bump |
| Out of Scope | Backend routes/models/tests/migrations, taskpane/Command Centre, patient identity/duplicate work, waiting-area data model, drag/drop/resize |
| Verification | `node --check docs\diary\diary.js`, live/smoke/narrow visual checks, `git diff --check` |
| Status | Integrated |

### Workstream AE - Patient Identity Duplicate Foundation

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/patient-identity-duplicates` |
| Task Packet | `orchestration/agent_inbox/codex/codex-patient-identity-duplicates.md` |
| Goal | Start the backend foundation for safer patient creation with focused tests and minimal API/model support for identity fields and duplicate-candidate handling |
| In Scope | `app/models/patients.py`, `app/schemas/patients.py`, `app/routers/patients.py`, patient tests, Alembic migration if needed, `create_patient_file.py` only for minimal generated-file mapping |
| Out of Scope | Diary frontend, appointment/roster/nurse booking work, taskpane UI implementation, OneDrive import tooling, ADHA/IHI service integration, Medicare claiming integration |
| Verification | Focused patient pytest, migration check if needed, `git diff --check`, generator smoke if touched |
| Status | Integrated |

## Sprint 9: Patient Flow and Patient Entry Hardening

| Item | Value |
|---|---|
| Status | Integrated and user-reviewed |
| Launch Gate | Complete |
| Integration Gate | Complete |
| Theme | Harden the practical patient-flow layer before drag/drop/resize and roster-admin work |

### Workstream Z - Booking Patient-Flow Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-booking-patient-flow-contract.md` |
| Goal | Strengthen appointment update/status/waiting-room contract for the next diary operations layer |
| In Scope | Appointment schemas/router/models as needed, focused appointment create/edit/status/waiting-room/slots tests |
| Out of Scope | Diary frontend, drag/drop/resize UI, roster admin UI, taskpane/Command Centre/Gemini, patient search/New Patient work |
| Verification | Focused appointment pytest suites plus any new patient-flow contract tests |
| Status | Integrated |

### Workstream AA - Diary Patient-Flow Workbench

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-patient-flow-workbench.md` |
| Goal | Improve the receptionist-facing diary patient-flow surface while preserving booking create/edit behaviour |
| In Scope | `docs/diary/diary.{html,css,js}` |
| Out of Scope | Backend routes/models/tests/migrations, drag/drop, resize handles, roster admin UI, online booking portal, patient import tooling |
| Verification | JS syntax plus live/smoke/narrow create/edit/status/patient-flow visual checks |
| Status | Integrated |

### Workstream AB - Patient Search and New Patient Hardening

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/patient-search-new-patient-hardening` |
| Task Packet | `orchestration/agent_inbox/codex/codex-patient-search-new-patient-hardening.md` |
| Goal | Add meaningful tests and minimal fixes for DB-backed patient search and New Patient creation |
| In Scope | Focused patient tests, `app/routers/patients.py`, `app/schemas/patients.py`, `create_patient_file.py`, seed/test helpers only as needed |
| Out of Scope | OneDrive import tools, diary frontend, appointment/status routes, taskpane UI, Command Centre, Gemini/AI behaviour |
| Verification | Focused patient pytest suite, `git diff --check`, generator smoke test if touched |
| Status | Integrated |

## Sprint 8: Booking Create/Edit First Slice

| Item | Value |
|---|---|
| Status | Integrated and user-reviewed |
| Launch Gate | Complete |
| Integration Gate | Complete |
| Theme | Add a practical create/edit booking path without starting drag/drop/resize |

### Workstream W - Booking Create/Edit Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-booking-create-edit-contract.md` |
| Goal | Harden the backend appointment create/edit contract for diary use |
| In Scope | Appointment models/schemas/router, focused create/edit/conflict/auth/scope tests, minimal seed/test helper changes if needed |
| Out of Scope | Diary frontend, drag/drop/resize UI, roster admin UI, waiting-room display app, taskpane/Command Centre/Gemini, online booking portal |
| Verification | Focused appointment conflict/status/waiting-room/slots pytest suites plus any new booking create/edit tests |
| Status | Integrated |

### Workstream X - Diary Create/Edit Modal

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-create-edit-modal.md` |
| Goal | Add restrained diary create/edit controls using the existing appointments API |
| In Scope | `docs/diary/diary.{html,css,js}` |
| Out of Scope | Backend routes/models/tests, drag/drop/resize, recurring appointments, roster admin UI, waiting-room display app, taskpane/Command Centre/Gemini, online booking portal |
| Verification | JS syntax plus live/smoke/narrow create/edit/failure visual checks |
| Status | Integrated |

### Workstream Y - Booking Create/Edit Review Plan

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/booking-create-edit-review-plan` |
| Task Packet | `orchestration/agent_inbox/codex/codex-booking-create-edit-review-plan.md` |
| Goal | Prepare integration and user-review checklist for the create/edit booking slice |
| In Scope | Orchestration/review documentation, including exact PowerShell API snippets for user review |
| Out of Scope | Production backend/frontend code, migrations, drag/drop/resize, roster admin UI, taskpane/Command Centre/Gemini |
| Verification | `git diff --check` |
| Status | Integrated |

## Sprint 7: Controlled Status Mutation

| Item | Value |
|---|---|
| Status | Integrated and user-reviewed |
| Launch Gate | Complete |
| Integration Gate | Complete |
| Theme | Add safe receptionist-facing appointment status changes before booking create/edit/drag/drop work |

### Workstream T - Appointment Status Mutation Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-appointment-status-mutation-contract.md` |
| Goal | Harden backend status mutation behavior and regression coverage |
| In Scope | Appointment status router/schema/tests; minimal production fixes only if tests expose unsafe behavior |
| Out of Scope | Diary frontend, taskpane/Command Centre/Gemini, booking create/edit/drag/drop, roster admin UI |
| Verification | Focused appointment status/waiting-room/slots pytest suites |
| Status | Integrated |

### Workstream U - Diary Status Controls

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-status-controls.md` |
| Goal | Add restrained diary controls for status-only mutation |
| In Scope | `docs/diary/diary.{html,css,js}` |
| Out of Scope | Backend, taskpane/Command Centre/Gemini, booking create/edit/drag/drop, roster admin UI |
| Verification | JS syntax plus live/smoke/narrow/failure/session visual checks |
| Status | Integrated |

### Workstream V - Status Mutation Review Plan

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/status-mutation-review-plan` |
| Task Packet | `orchestration/agent_inbox/codex/codex-status-mutation-review-plan.md` |
| Goal | Define the post-integration review path for controlled status mutation |
| In Scope | Small orchestration/checklist documentation only |
| Out of Scope | Production backend/frontend implementation, tests, migrations, booking create/edit/drag/drop |
| Verification | `git diff --check` |
| Status | Integrated |

## Sprint 6: Read-Only Patient Flow Visibility

| Item | Value |
|---|---|
| Status | Integrated and user-reviewed |
| Launch Gate | Complete |
| Integration Gate | Complete |
| Theme | Make appointment status and waiting-room/patient-flow state reviewable before booking or status mutation UI |

### Workstream Q - Waiting Room Status Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-waiting-room-status-contract.md` |
| Goal | Harden read-only waiting-room/status API behavior and tests |
| In Scope | Appointment models/schemas/router and appointment/waiting-room tests |
| Out of Scope | Diary frontend, taskpane/Command Centre/Gemini, booking/status mutation UI |
| Verification | Focused appointment/waiting-room pytest suites |
| Status | Integrated |

### Workstream R - Diary Status Affordances

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-status-affordances.md` |
| Goal | Make appointment lifecycle/status easier to scan in the read-only diary |
| In Scope | `docs/diary/diary.{html,css,js}` |
| Out of Scope | Backend, taskpane/Command Centre/Gemini, booking/status mutation controls |
| Verification | JS syntax plus live/smoke/narrow visual checks |
| Status | Integrated |

### Workstream S - Patient Flow Review Notes

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/patient-flow-review-notes` |
| Task Packet | `orchestration/agent_inbox/codex/codex-patient-flow-review-notes.md` |
| Goal | Define review expectations for read-only patient-flow/status visibility |
| In Scope | Small orchestration/checklist documentation only |
| Out of Scope | Production backend/frontend implementation, tests, migrations, booking/status mutations |
| Verification | `git diff --check` |
| Status | Integrated |

## Sprint 5: Diary Polish and Test Infrastructure

| Item | Value |
|---|---|
| Status | Integrated and user-reviewed |
| Launch Gate | Complete |
| Integration Gate | Complete |
| Theme | Smooth the diary user-review rough edges and harden the test infrastructure before booking mutations |

### Workstream N - Test DB Teardown Hardening

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-test-db-teardown-hardening.md` |
| Goal | Fix the recurring partial PostgreSQL test DB teardown/reset failure seen during rapid pytest reruns |
| In Scope | `tests/conftest.py` and narrow test DB setup/teardown helpers/tests as needed |
| Out of Scope | Production app behavior, migrations, diary frontend, taskpane/Command Centre/Gemini, booking mutations |
| Verification | Repeat focused diary roster/template pytest runs; broader tests only if fixture changes risk shared behavior |
| Status | Integrated |

### Workstream O - Diary Date and Now Marker Refinement

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-ui-date-now-refinement.md` |
| Goal | Add a practical date control and soften the current-time marker without regressing narrow diary layout |
| In Scope | `docs/diary/diary.{html,css,js}` |
| Out of Scope | Backend, tests beyond narrow frontend smoke helpers, taskpane/Command Centre/Gemini, booking mutations |
| Verification | JS syntax plus live/smoke/narrow/date-picker/Now-marker browser checks |
| Status | Integrated |

### Workstream P - Diary Smoke/Live Review Checklist

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/diary-smoke-live-review` |
| Task Packet | `orchestration/agent_inbox/codex/codex-diary-smoke-live-review.md` |
| Goal | Clarify smoke-mode versus live-diary expectations and prepare the post-integration review checklist |
| In Scope | Small orchestration/checklist documentation only |
| Out of Scope | Production backend/frontend implementation, migrations, seed data, taskpane/Command Centre/Gemini |
| Verification | `git diff --check`; JS syntax only if JS is touched |
| Status | Integrated |

## Sprint 4: Diary Roster Consumption

| Item | Value |
|---|---|
| Status | Integrated and user-reviewed |
| Launch Gate | Complete |
| Integration Gate | Complete |
| Theme | Make date-specific roster data visible in the diary without starting booking mutation work |

### Workstream K - Diary Roster Dev-Data Contract

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-diary-roster-dev-data-contract.md` |
| Goal | Make roster backend data seedable, scoped, ordered, and predictable enough for frontend consumption |
| In Scope | `app/models/diary.py`, `app/schemas/diary.py`, `app/routers/diary.py`, `seed.py`, migrations/tests as needed |
| Out of Scope | `docs/diary/*`, booking mutations, Gemini/taskpane/Command Centre |
| Verification | Focused diary roster/template tests plus migration checks if changed |
| Status | Integrated |

### Workstream L - Diary Roster Consumption

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-diary-roster-consumption.md` |
| Goal | Fetch and merge date-specific roster entries into the read-only diary frontend with safe fallback |
| In Scope | `docs/diary/diary.{html,css,js}` |
| Out of Scope | Backend routes/models/tests, booking mutations, taskpane/Command Centre/Gemini |
| Verification | JS syntax plus normal/smoke/narrow/date-navigation browser checks |
| Status | Integrated |

### Workstream M - Diary Roster Smoke Review

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/diary-roster-smoke-review` |
| Task Packet | `orchestration/agent_inbox/codex/codex-diary-roster-smoke-review.md` |
| Goal | Prepare the review/smoke-test surface for roster consumption without duplicating implementation scopes |
| In Scope | Small orchestration/checklist or smoke-review artifacts; tiny non-overlapping smoke fixture only if safe |
| Out of Scope | Backend roster implementation, production frontend roster merge, booking mutations |
| Verification | `git diff --check`; `node --check docs\diary\diary.js` if JS touched |
| Status | Integrated |

## Sprint 3: Diary Operations Foundation

| Item | Value |
|---|---|
| Status | Integrated and user-reviewed |
| Launch Gate | Complete |
| Integration Gate | Complete |

### Workstream H - Diary Time-Ruler UX

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/diary-time-ruler-ux` |
| Task Packet | `orchestration/agent_inbox/codex/codex-diary-time-ruler-ux.md` |
| Goal | Make flexible diary times visible and navigable without starting booking mutation work |
| In Scope | `docs/diary/diary.{html,css,js}` |
| Out of Scope | Backend roster models, appointment mutation routes, drag/drop booking edits |
| Verification | JS syntax plus desktop/narrow smoke checks |
| Status | Queued |

### Workstream I - Room and Diary Roster Foundation

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-diary-roster-foundation.md` |
| Goal | Persist room/roster configuration so diary columns can become date-specific |
| In Scope | Backend models, migration, schemas/router/service/tests |
| Out of Scope | Diary frontend, booking drag/drop, Gemini migration |
| Verification | Relevant pytest plus migration checks |
| Status | Queued |

### Workstream J - Gemini SDK Migration Spike

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-gemini-sdk-migration-spike.md` |
| Goal | De-risk migration away from deprecated `vertexai.generative_models` before removal |
| In Scope | Gemini/Vertex imports and calls, dependency notes, a small compatibility layer only if safe |
| Out of Scope | Prompt redesign, diary backend/frontend, clinical feature redesign |
| Verification | App import / targeted tests, plus exact risks if credentials block live smoke |
| Status | Queued |

## Sprint 1: Diary Interactivity Foundation

## Agent Inbox

Task packets are stored here:

- `orchestration/agent_inbox/claude/`
- `orchestration/agent_inbox/antigravity/`
- `orchestration/agent_inbox/codex/`

Packet status values are lightweight text: `queued`, `in_progress`, `submitted`,
`integrated`, `superseded`, or `blocked`. The submit command pushes the worker
branch only; Codex reviews and integrates afterward.

### Workstream A — Backend Time Model

| Item | Value |
|---|---|
| Owner | Codex |
| Branch | `codex/current` or `codex/time-model` if split further |
| Goal | Define and implement canonical appointment time representation |
| In Scope | `app/models/appointments.py`, `app/schemas/appointments.py`, `app/routers/appointments.py`, Alembic migration, seed updates |
| Out of Scope | Frontend drag/drop UI, room roster UI |
| Plan | Move appointments toward clinic-local `appointment_date` + `start_time_local` + `duration_minutes` + timezone-derived UTC helpers; preserve API compatibility during transition where practical |
| Verification | Migration applies; appointment CRUD tests; `/slots` tests; app import |
| Dissent / Risks | Requires careful transition from existing `start_time` data |
| Status | Integrated |

### Workstream B — Diary Grid Interval Rendering

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` or `antigravity/diary-grid-intervals` |
| Goal | Rebuild the diary grid so appointments occupy intervals, not only start cells |
| In Scope | `docs/diary/diary.js`, `docs/diary/diary.css`, `docs/diary/diary.html` |
| Out of Scope | Backend schema migration, appointment mutation routes |
| Plan | Render appointment duration spans from `start_time`/`end_time`; handle overlaps visibly; preserve silent refresh |
| Verification | Browser visual QA desktop/mobile; JS syntax; no spinner flash on auto-refresh |
| Dissent / Risks | Needs stable backend `end_time`; should avoid drag/drop until backend time model lands |
| Status | Integrated |

### Workstream C — Appointment Tests and Security Gates

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` or `claude/appointment-tests` |
| Goal | Add regression tests around auth, practice scoping, appointment conflicts, and slots |
| In Scope | Test framework setup if absent, appointment/consultation route tests, fixture seed helpers |
| Out of Scope | UI implementation |
| Plan | Create minimal pytest suite using FastAPI TestClient or direct route/service tests; cover P0/P1 fixes |
| Verification | Tests pass locally in `.venv`; failures are actionable |
| Dissent / Risks | Existing app imports initialize Vertex AI; tests may need dependency overrides/mocking |
| Status | Integrated |

### Workstream D — Gemini SDK Migration Spike

| Item | Value |
|---|---|
| Owner | Codex or Claude Code |
| Branch | Separate branch after Sprint 1 starts |
| Goal | Replace deprecated Vertex AI `generative_models` usage before the 2026-06-24 removal date |
| In Scope | `app/routers/consultation.py`, config, minimal smoke test |
| Out of Scope | Prompt redesign, SNOMED deterministic mapping |
| Plan | Identify current supported Google Gen AI client path for Vertex; migrate with behavior preserved |
| Verification | App import without deprecation warning; analyze/scribe smoke test with credentials |
| Dissent / Risks | Needs careful check against current Google docs and installed SDK versions |
| Status | Proposed, urgent technical debt |

## Sprint 2: Diary App Foundation

### Workstream E — Independent Diary Grid

| Item | Value |
|---|---|
| Owner | Antigravity |
| Branch | `antigravity/current` |
| Task Packet | `orchestration/agent_inbox/antigravity/antigravity-independent-diary-grid.md` |
| Goal | Replace shared table-row diary rendering with independent positioned columns |
| In Scope | `docs/diary/diary.{html,css,js}` only |
| Out of Scope | Backend changes, drag/drop, booking/status mutations |
| Verification | JS syntax plus desktop/narrow browser visual QA |
| Status | Integrated |

### Workstream F — Canonical Time Regression Tests

| Item | Value |
|---|---|
| Owner | Claude Code |
| Branch | `claude/current` |
| Task Packet | `orchestration/agent_inbox/claude/claude-time-model-regression-tests.md` |
| Goal | Prove legacy `start_time` and new `appointment_date + start_time_local` behavior |
| In Scope | Tests and minimal fixtures/helpers; tiny production fixes only if blocked |
| Out of Scope | Frontend, schema redesign, Room/DiaryRoster |
| Verification | `.venv\Scripts\python.exe -m pytest tests` |
| Status | Superseded by integrated canonical time test coverage |

### Workstream G — Diary Template API Foundation

| Item | Value |
|---|---|
| Owner | Codex worker |
| Branch | `codex/diary-template-api` |
| Task Packet | `orchestration/agent_inbox/codex/codex-diary-template-api.md` |
| Goal | Add backend Room/DiaryRoster/template foundation compatible with current diary config |
| In Scope | Backend models/schemas/router/migration/tests as needed |
| Out of Scope | Frontend consumption, drag/drop, booking mutations |
| Verification | compileall, relevant pytest, Alembic head/current/upgrade if migration added |
| Status | Integrated |
