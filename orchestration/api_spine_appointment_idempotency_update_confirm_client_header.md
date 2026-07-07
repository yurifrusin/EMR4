# Sprint 157 - Update Confirm Client Header Emission

## Scope

Sprint 157 wires client-side HTTP `Idempotency-Key` emission for ordinary Diary
signed update-confirm calls.

This covers:

- edit modal appointment detail updates that confirm through
  `/api/v1/appointments/proposals/update/confirm`;
- human drag, move, and resize updates that confirm through the same signed
  update-confirm route.

This does not cover:

- Bernie tool-intent update confirmation;
- proposal-only route header binding;
- raw `PUT /appointments/{id}` compatibility paths;
- backend idempotency ledger behaviour;
- OpenAPI `minLength: 8` runtime enforcement;
- provider calls, GraphQL mutations, memory/RAG/GraphRAG runtime wiring,
  H15/H-series runtime imports, or broad historical diary trove mining.

## Key Strategy

Ordinary update-confirm calls now derive their header from the backend proposal
freshness token:

```text
Idempotency-Key: update-confirm-<update_proposal_freshness_id>
```

If a future proposal envelope lacks a usable freshness value or the derived key
would exceed the client-side length guard, the existing generated
proposal-scoped fallback is used. That keeps retries stable for the active
proposal object without granting replay semantics to raw compatibility routes.

## Verification

Sprint 157 adds static and route-intercepted checks for the two ordinary update
surfaces:

- `tests/test_api_spine_frontend_header_inventory.py` asserts both
  `saveBooking()` and `handleMoveResize()` update-confirm branches send
  `headers: confirmHeaders`.
- `review/test_diary_smoke.py` asserts the modal edit and drag/resize flows
  send `update-confirm-edit-fresh-1` and `update-confirm-human-fresh-1`.

## Deferred Work

Sprint 159 wires `confirmBernieToolIntentChange()` with the same
freshness-derived update-confirm header strategy. Proposal-only header binding,
raw compatibility paths, strict `minLength: 8` runtime enforcement, and backend
ledger behaviour remain separate follow-up decisions.
