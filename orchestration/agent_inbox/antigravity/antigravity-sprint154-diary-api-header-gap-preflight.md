# Sprint 154 - Diary/API Header Gap Preflight

## Request

Review the Diary frontend and appointment API idempotency posture after Sprint
153.

## Context

Sprint 153 made `POST /api/v1/appointments/proposals/create` from the Diary
frontend send an 8+ character HTTP `Idempotency-Key`. Sprint 154 should map the
remaining gap before Sprint 155 chooses one implementation slice.

## Focus

Please inspect:

- `docs/diary/diary.js`
- `review/test_diary_smoke.py`
- `app/routers/appointments.py`
- `docs/api-spine/openapi/appointment-commands.yaml`

## Questions

1. Which frontend calls are now covered by HTTP `Idempotency-Key` emission?
2. Which confirm/proposal/status/delete calls are likely to fail or drift if
   backend idempotency enforcement expands before the client is ready?
3. Should Sprint 155 target create-confirm/confirm-Bernie/status/delete confirm
   header emission, or the next proposal-only backend binding?
4. What UI smoke/static tests should Sprint 154 add before implementation?

## Boundaries

No runtime route wiring, provider calls, GraphQL mutation work, H15/H-series
runtime imports, memory/RAG/GraphRAG, raw compatibility idempotency, or broad
historical diary trove access.
