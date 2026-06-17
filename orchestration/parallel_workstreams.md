# EMR4 Parallel Workstreams

This is the live board for Codex-orchestrated parallel work. `AGENTS.md` remains the
single source of truth for durable project state; this file tracks active branch work.

## Operating Rules

- Every agent starts with `python scripts\agent_worktrees.py handin`.
  This now performs the full intake ritual: sync, infer agent, list inbox, and
  print the next task packet.
- Parallel workers finish with `python scripts\agent_worktrees.py submit ...`.
  Packet submit commands include `--task`, which creates a Codex review packet
  in the worker branch.
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
- Only Codex, acting as orchestrator, advances `master` and `handoff/current` in
  parallel mode unless the user explicitly instructs otherwise.
- Every workstream must state files in scope, files out of scope, verification, and
  merge criteria.
- Agents should record concerns or disagreement in the "Dissent / Risks" field.

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

## Sprint 1: Diary Interactivity Foundation

## Agent Inbox

Task packets are stored here:

- `orchestration/agent_inbox/claude/`
- `orchestration/agent_inbox/antigravity/`
- `orchestration/agent_inbox/codex/`

Packet status values are lightweight text: `queued`, `in_progress`, `submitted`,
`blocked`, or `merged`. The submit command pushes the worker branch only; Codex
reviews and integrates afterward.

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
| Status | Dispatched |

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
| Status | Dispatched |

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
| Status | Dispatched |
