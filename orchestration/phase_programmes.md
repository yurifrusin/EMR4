# EMR4 Phase Programmes

This file sits between the long implementation phases in `implementation_plan.md`
and the short tactical sprints in `orchestration/parallel_workstreams.md`.

Use it when Ariadne is deciding what to do next. A programme is a coherent
outcome-oriented slice, usually 3-6 sprints, that lets us see progress through a
phase without either overloading one sprint or atomising the work into ceremony.

## Planning Grammar

| Level | Purpose | Typical Size | Owner |
|---|---|---:|---|
| Phase | Strategic product capability from `implementation_plan.md` | months | Yuri + Ariadne |
| Programme | Coherent outcome within a phase | 3-6 sprints | Ariadne |
| Sprint | Tactical integrated increment | 1-3 worker streams | Ariadne + workers |
| Workstream | One agent's bounded implementation/review slice | one branch | Worker agent |

## Sprint Sizing Rule

Keep sprints narrow enough to review safely, but not so narrow that process
overhead dominates. The preferred sprint unit is:

- one coherent product outcome;
- backend + frontend + tests + docs allowed when they serve that one outcome;
- split only when ownership conflicts, blast radius, security/privacy risk, or
  unclear acceptance criteria would make review unsafe;
- security/tooling/process sprints stay smaller because mistakes there affect
  project trust rather than one feature surface.

In short: **narrow by outcome, not by file count**.

## Phase 2 Current Programmes

Phase 2 has already pivoted from a Word-hosted "Living Diary" document toward a
native web diary plus Word clinical notes. The intermediate programme map below
tracks that actual architecture.

### Programme 2A - Native Diary Operations Foundation

| Item | Value |
|---|---|
| Status | Mostly integrated |
| Outcome | Staff can view the diary, statuses, waiting-room state, rooms, locations, waiting areas, and resource defaults coherently |
| Representative Sprints | Diary grid foundation, roster consumption, status controls, waiting room tabs/check-in, location-aware diary, resource admin, room default waiting-area invariant |
| Done Signals | Active rooms/waiting areas/locations have stable vocabulary and admin controls; Waiting Room pane reflects appointment status and physical waiting areas; backend contracts enforce practice/location safety |
| Remaining Edges | Live Admin v84 smoke; taskpane logout/accessibility if it recurs; broad pytest timeout triage; stale `codex/time-model` disposable worktree review |

### Programme 2B - Safe Appointment Mutation Workbench

| Item | Value |
|---|---|
| Status | In progress |
| Outcome | Reception can create, edit, link, and status-change appointments through proposal-first flows with clear conflict/break/provisional warnings |
| Representative Sprints | Command proposal layer, create proposal flow, appointment update/status proposal contract, provisional patient linking, duplicate review API, patient search alerts |
| Next Candidate Sprints | Sprint 25 status/waiting-area proposal retrofit dispatched; then drag/reschedule design groundwork, cancel/no-show/DNA confirmation semantics, recurrence/reason-note polish |
| Done Signals | All high-risk receptionist appointment writes pass through deterministic proposal/confirmation contracts before mutation |

### Programme 2C - Ariadne Tooling and Review Automation

| Item | Value |
|---|---|
| Status | In progress |
| Outcome | Ariadne can run most sprint verification herself before asking Yuri for only genuinely human checks, and frontend/backend deploys carry preview, smoke, promotion, rollback, and version evidence |
| Representative Sprints | Security baseline, security alert triage, backend/frontend dev-loop tooling, provider-neutral Pushover notifications, deterministic UI review harness, Vercel-style preview deployment harness |
| Next Candidate Sprints | Browser/Chrome smoke automation harness, broad pytest timeout segmentation, GitHub security alert automation, CI/base-ref frontend asset checks, protected preview deployment harness |
| Done Signals | Sprint closeouts routinely include tool-run browser/API/security evidence and a very short Yuri-only residual review list; frontend-affecting changes can be reviewed at immutable preview URLs with smoke results before promotion |

### Programme 2D - Reception Copilot Readiness

| Item | Value |
|---|---|
| Status | Design groundwork only |
| Outcome | Bernie can later suggest receptionist actions safely without direct model-to-database mutation |
| Representative Sprints | Resource admin and Bernie tool design, command proposal harnesses, appointment proposal contracts |
| Start Gate | Programme 2B's appointment mutation contracts are stable; audit trail and human-confirmation semantics are explicit |
| Next Candidate Sprints | Tool-schema audit log foundation, staff message-taking model, slot-search proposal contract, non-autonomous Bernie command preview |

### Programme 2E - Practice Messaging and Daily Admin

| Item | Value |
|---|---|
| Status | Not started |
| Outcome | Diary/admin mode gains internal messages, daily billing review, and operational queues without confusing them with clinical notes |
| Candidate Sprints | Internal message model/API, diary message panel, billing review queue, operational notification semantics |
| Start Gate | Appointment/status/resource foundations are steady enough that new queues will not obscure core diary workflow |

### Programme 2F - Access AI API

| Item | Value |
|---|---|
| Status | In progress |
| Outcome | EMR4 has one identity-aware, role-aware, keyless internal API for invoking AI capabilities across clinical copilot, Bernie, and later modalities |
| Representative Sprints | Access AI architecture record, keyless GCP dev auth runbook, AI capability registry, entitlement model, typed audit event catalog, invocation service, audit/cost envelope, enterprise-auth seam, Bernie/Copilot migrations, caller-context pending booking proposals, multi-provider knowledge-base adapter |
| Next Candidate Sprints | Caller-context booking proposal groundwork or Wiley/Cochrane licensed knowledge-base integration spike |
| Done Signals | No frontend or router calls model providers directly; dev uses service-account impersonation rather than JSON keys; every AI call passes through capability policy, product entitlement, provider adapter, and bounded audit metadata; external knowledge bases such as future Wiley/Cochrane integrations route through the same Access AI policy and citation envelope; EMR4's internal org/role/resource model can later map to enterprise SSO/SCIM/FGA without a rewrite |
| Design Record | `orchestration/access_ai_api_design.md` |

## Recommended Next Planning Move

Do not launch another micro-sprint solely because one small snag appeared. Pick
the next sprint from the active programme that best advances the phase:

1. If AI platform safety is the priority: choose caller-context booking proposal
   groundwork or a Wiley/Cochrane licensed knowledge-base integration spike.
2. If product flow is the priority: continue **Programme 2B** with the active
   Sprint 25 status/waiting-area proposal retrofit, then drag/reschedule design.
3. If orchestration confidence is the priority: continue **Programme 2C** with a
   browser-smoke automation harness plus broad pytest timeout segmentation.
4. If Bernie is becoming tempting: keep it in **Programme 2D** design/tool-schema
   preparation until Programme 2B's mutation contracts are mature.

The default recommendation after Sprint 91 remains **Programme 2F** until
caller-context booking proposals and licensed knowledge-base retrieval are safe
enough to expose through product surfaces.

## Deployment Readiness Pattern

Vercel is a useful deployment benchmark, especially for frontend/product review
workflows. EMR4 is not moving its FastAPI/Postgres clinical backend to Vercel by
default, but should borrow these deployment primitives:

- immutable deploy artifacts and versioned URLs
- automatic preview deployments for branch/PR changes
- protected previews when realistic or sensitive data is available
- build once, then promote the same artifact through preview/staging/production
- fast rollback to a known-good deployed artifact
- deployment metadata: commit, asset versions, environment, smoke result, and
  reviewer notes
- deploy-attached observability: logs, errors, traces, and request/version
  correlation

Near-term sprint candidate:

### Sprint 84 - Preview Deployment Harness

Goal: every frontend-affecting branch can produce a protected preview URL with
version metadata, deterministic diary/taskpane smoke checks, and a clear
promotion/rollback record. Keep GitHub Pages for the current live static assets
unless the sprint proves a better preview host is needed. Do not move the
FastAPI backend, database, PHI processing, Office integration, or Access AI
runtime to Vercel as part of this sprint.
