# plan-codex-codex-sprint-n8-route-outcome-invariants

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/sprint-n8-route-outcome-invariants` |
| Source Task | `codex-sprint-n8-route-outcome-invariants` |
| Status | integrated |
| Created | 2026-07-04 00:34 +1000 |
| Source HEAD | `5f2c680` |

## Plan Summary

Route outcome event wiring plan accepted

## My Understanding

Wire actual Bernie interpretation, supervised booking, proposal, and confirmation route outcomes into the N7 server-owned session event substrate without changing visible Diary behaviour or allowing writes before explicit confirmation.

## Intended Surface / Boundary

Backend-only route/session semantics in app/routers/appointments.py plus appointment schemas, session store identity coordinates, and focused tests.

## Out Of Scope

No persisted session table, migration, GraphRAG, Diary UI redesign, taskpane, Command Centre, auto-mode, or broad API-spine rewrite.

## Files I Expect To Edit

app/routers/appointments.py; app/schemas/appointments.py; app/services/bernie/session_store.py; tests/test_bernie_route_outcome_events.py

## Implementation Steps

Add optional server_session route coordinates; append compact interpretation/context/slot/proposal/confirmation outcomes when supplied; stamp session binding into signed confirm evidence; keep legacy callers backward compatible; add focused route tests.

## Visual / Behavioural Acceptance Checks

Successful interpretation advances recognition to context_enrichment; no-slot paths advance no_slot/clinic_day_exhausted; proposal staging records freshness IDs and IDs without writing; session-bound confirmation transitions through confirmation and records confirmed only after write; focused tests pass.

## Risks / Ambiguities

Diary does not yet send server_session_* fields, so route wiring is available for a later UI sprint; external Claude/Antigravity lanes were unavailable/no-artifact.

## Codex Plan Review

- Review result: Accepted by Ariadne and implemented as the Sprint N8 backend/session-authority slice.
- Required changes before implementation: Keep route-session coordinates optional/backward compatible; no Diary UI wiring in this sprint.
- Approved to proceed: yes
