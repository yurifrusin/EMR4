# Sprint 155 - Create-Confirm Client Header Emission

## Request

Review the UI/client implementation slice for adding HTTP `Idempotency-Key`
headers to create-confirm and confirm-Bernie requests.

## Context

Sprint 154 found that create-proposal is the only Diary caller that sends the
HTTP header today. Sprint 155 should fix the immediate confirm hop after
create-proposal without broadening backend enforcement or touching raw writes.

## Focus

Inspect:

- `docs/diary/diary.js`
- `docs/diary/diary.html`
- `review/test_diary_smoke.py`
- `tests/test_api_spine_frontend_header_inventory.py`

## Questions

1. Which exact create-confirm and confirm-Bernie call sites should receive
   headers?
2. How should the key remain stable across retry/double-submit of the same
   staged confirmation?
3. Which smoke/static tests best prove this without live backend calls?
4. What UI behavior should remain unchanged?

## Boundaries

No backend route behavior, OpenAPI schema, ledger semantics, raw compatibility
writes, providers, GraphQL mutations, H15/H-series runtime imports,
memory/RAG/GraphRAG, or strict `minLength: 8` runtime enforcement.
