# Bernie UI Derived-State DAG D4 Preflight

Date: 2026-07-08

Status: preflight/review only. No UI wiring, route wiring, backend response
wiring, provider wiring, database access, memory/RAG/GraphRAG access,
H15/H-series runtime import, historical diary material access, GraphQL resolver,
or appointment write is approved by this packet.

Proposal-surface guard citation:

```powershell
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
```

Expected blocked values: `runtime_or_provider_wiring_ready=false`,
`raw_trove_access_ready=false`, `runtime_gate_decision=blocked`,
`default_provider=disabled`, `live_provider_enabled=false`,
`provider_calls_performed=false`, `route_behavior_changed=false`,
`database_access_performed=false`, `memory_or_rag_access_performed=false`, and
`historical_diary_material_access_performed=false`.

## Candidate D4 Slice

If D4 proceeds, it should be a route-intercepted UI consumer slice over the
existing primary Bernie booking review panel only. It should not wire backend
responses to include `BernieUiViewModel` yet.

Allowed UI surface:

- `renderBernieReview`;
- candidate slot list visibility;
- pending proposal card visibility;
- `bernie-review-confirm-button` visibility/enabled state;
- stale/session warning visibility;
- success copy visibility after the existing signed REST confirm call reports
  success;
- retry/edit or choose-another-time affordances for stale or failed states.

Out of scope:

- `renderBernieToolIntentReview`;
- command payload changes;
- confirm endpoint changes;
- backend route/response changes;
- provider or live-provider checks;
- GraphQL delivery of the view model;
- frontend reimplementation of the Python selector as business logic.

## Route-Intercepted Fixture Contract

The D4 test harness should intercept the same browser/API calls the current
Diary smoke tests already intercept. Fixtures must be labelled
`route_intercepted` and must not be described as live backend or live provider
evidence.

Required fixture states:

| Fixture | Required UI assertions |
|---|---|
| `candidate_slots_available` | candidate list visible; confirm button hidden; success copy hidden |
| `proposal_ready` | proposal card visible; confirm button visible and enabled; choose-another-time visible; success copy hidden |
| `pressed_or_awaiting_backend` | confirm button disabled or hidden; candidate list collapsed; success copy hidden; ordinary copy does not say booked or confirmed |
| `backend_confirmed_success` | success copy visible only after intercepted confirm success; confirm button hidden; candidate list hidden |
| `stale_proposal` | stale warning visible; confirm button hidden or disabled; refresh/retry/edit path visible |
| `backend_rejected` | retry/edit path visible; success copy hidden; raw `Not Found`, UUIDs, and snake_case codes hidden |
| `ambiguous_identity` | clarification/identity prompt visible; proposal/confirm blocked |

## Acceptance Checks Before Wiring

The UI wiring sprint must prove:

- route-intercepted evidence labels are explicit;
- no test claims live backend or live provider evidence;
- pre-confirm ordinary copy excludes raw UUIDs, snake_case codes,
  `missing_practitioner_id`, generic `Not Found`, `booked`, and `confirmed`;
- `pressed` and `awaiting_backend` states do not claim success;
- stale/failed states preserve a visible recovery path;
- command payloads still contain existing signed proposal/freshness/evidence
  fields and do not contain `BernieUiViewModel` fields such as `copy_mode`,
  `confirmation_state`, `freshness_state`, or `flags`;
- `docs/diary/diary.js` remains the only UI file touched unless a separate
  review expands scope;
- no production route imports `app.services.bernie.ui_view_model` until a later
  backend response-delivery review.

## Stop Conditions

D4 wiring must stop and report back if it needs any of:

- backend route or schema changes;
- live provider or provider dry-run evidence;
- new appointment write behavior;
- model-to-database writes;
- GraphQL resolver changes;
- H15/H-series or historical diary runtime inputs;
- memory/RAG/GraphRAG access;
- external patient-client exposure.

## Strategic Position

This is the final review packet before a possible narrow D4 UI consumer sprint.
It reduces the wiring sprint to a known route-intercepted slice and keeps the
selector as display-only state rather than command authority.
