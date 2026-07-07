# Sprint 154 - Diary/API Header Gap Preflight

## Request

Review the remaining diary/API `Idempotency-Key` gaps after Sprint 153.

## Context

- Sprint 153 wired the real diary create-proposal caller to send an
  `Idempotency-Key` header.
- Backend runtime `minLength: 8` enforcement remains deferred.
- Existing proposal-only routes are intentionally not confirmation replay
  ledgers.
- Sprint 154 should be an inventory/preflight, not broad route behavior
  change.

## Scope

Inspect:

- `docs/diary/diary.js`
- `app/routers/appointments.py`
- `docs/api-spine/openapi/appointment-commands.yaml`
- `tests/test_api_spine_create_proposal_header_alignment.py`
- recent idempotency docs under `orchestration/`

## Deliverable

Write your plan/review back to Ariadne as an artifact or final response covering:

1. Which diary callers emit HTTP `Idempotency-Key` headers today.
2. Which appointment command surfaces still lack client header emission.
3. Which backend proposal routes still lack FastAPI header binding.
4. The safest Sprint 155 implementation slice.
5. Tests that should guard the Sprint 154 inventory.

## Boundaries

Do not wire runtime behavior. Do not open provider, GraphQL mutation,
H15/H-series, memory/RAG/GraphRAG, raw compatibility idempotency, or historical
diary trove gates.
