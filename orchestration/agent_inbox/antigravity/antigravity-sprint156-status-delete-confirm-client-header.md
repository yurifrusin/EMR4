# Sprint 156 - Status/Delete Confirm Client Headers

## Request

Review the UI/client slice for adding HTTP `Idempotency-Key` headers to
status-confirm and delete-confirm requests.

## Context

Sprint 155 closed the first create-confirm client gap. Sprint 156 should extend
the pattern to the dedicated status/delete helpers without touching update
confirm, raw compatibility writes, backend ledger logic, or OpenAPI.

## Focus

Inspect:

- `docs/diary/diary.js`
- `docs/diary/diary.html`
- `review/test_diary_smoke.py`
- `tests/test_api_spine_frontend_header_inventory.py`

## Questions

1. Which exact status/delete confirm call sites should receive headers?
2. How should keys remain stable for the same proposal object?
3. Which route-intercepted/static tests should prove the behavior?
4. What UI behavior should stay unchanged?

## Boundaries

No backend route behavior, OpenAPI schema, ledger semantics, raw compatibility
writes, proposal-only backend binding, update-confirm wiring, Bernie tool-intent
confirm wiring, providers, GraphQL mutations, H15/H-series runtime imports,
memory/RAG/GraphRAG, or strict `minLength: 8` runtime enforcement.
