# Sprint 155 - Create-Confirm Client Header Emission

## Request

Review the implementation plan for wiring Diary client HTTP `Idempotency-Key`
headers on create-confirm and confirm-Bernie calls.

## Context

- Sprint 153 wired create-proposal client header emission.
- Sprint 154 proved only create-proposal currently emits the HTTP header.
- Backend create-confirm and confirm-Bernie routes already require
  `Idempotency-Key` and use the appointment command idempotency ledger.

## Scope

Inspect:

- `docs/diary/diary.js`
- `review/test_diary_smoke.py`
- `tests/test_api_spine_frontend_header_inventory.py`
- `orchestration/api_spine_appointment_idempotency_diary_header_gap_preflight.md`

## Questions

1. Should staff create-confirm reuse the existing modal-scoped create-proposal
   key, or use a separate stable confirm key?
2. Which Bernie confirm surfaces should Sprint 155 cover?
3. What frontend/static tests should prove retry-stable header emission?
4. What must remain out of scope?

## Boundaries

No backend route behavior, OpenAPI schema, ledger semantics, raw compatibility
writes, providers, GraphQL mutations, H15/H-series runtime imports,
memory/RAG/GraphRAG, or strict `minLength: 8` runtime enforcement.
