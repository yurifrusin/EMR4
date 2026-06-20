# EMR4 Parallel Workstreams

This is the live board for Codex-orchestrated parallel work. `AGENTS.md` remains the
single source of truth for durable project state; this file tracks active branch work.

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
- Codex dispatches concrete task packets to `orchestration/agent_inbox/<agent>/`.
- Agents read their next packet with `python scripts\agent_worktrees.py brief --agent <agent>`.
- Codex polls submissions with `python scripts\agent_worktrees.py poll --fetch`.
  This includes Claude/Antigravity branches and submitted `codex/*` worker branches,
  excluding the durable `codex/current` mirror.
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
- During a sprint, Codex must not push sprint work through to `master` until all
  active sprint agents, including any Codex subagent worker, have submitted or
  been explicitly stood down.
- Prefer batching non-urgent orchestration protocol edits until discussion
  settles. Codex should remind the user before launch when agreed protocol edits
  are pending.
- Every workstream must state files in scope, files out of scope, verification, and
  merge criteria.
- Agents should record concerns or disagreement in the "Dissent / Risks" field.

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
- **User Review:** what the user should manually test before the next dispatch,
  or "none required" with the reason.
- **Next Direction:** Codex's recommendation for the next project slice and any
  project-level concerns raised by the integrated agent work.

After every fully integrated batch, Codex updates
`orchestration/sprint_closeout.md` with:

- what changed
- recommended user review
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
