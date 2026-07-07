# Sprint 159 - Bernie Tool-Intent Confirm Client Header

## Scope

Sprint 159 wires the remaining user-clickable Bernie update-confirm client
header gap.

`confirmBernieToolIntentChange()` now sends HTTP `Idempotency-Key` when posting
the signed update-confirm payload returned by the Bernie tool-intent proposal
route.

This covers the visible flow where staff ask Bernie to extend an existing
appointment, Bernie returns deterministic update proposal evidence, and staff
click the tool-intent confirm button.

## Key Strategy

The key is derived with the same helper as ordinary update-confirm:

```text
Idempotency-Key: update-confirm-<update_proposal_freshness_id>
```

Using the update proposal freshness id keeps one client key strategy for the
same backend route:

```text
POST /api/v1/appointments/proposals/update/confirm
```

If the envelope lacks a usable freshness value, the existing proposal-scoped
generated fallback is used through `confirmIdempotencyKeyFromFreshness()`.

## Boundaries

This sprint does not change:

- backend idempotency ledger behaviour;
- proposal-only backend header binding;
- strict OpenAPI `minLength: 8` runtime enforcement;
- raw compatibility writes;
- provider calls;
- GraphQL mutations;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- broad historical diary material access.

## Verification Surface

Route-intercepted smoke coverage now captures the visible Bernie tool-intent
confirm request and asserts:

- the request body remains a signed update-confirm payload;
- the HTTP header is `update-confirm-fresh-tool-1`;
- ordinary modal edit and drag/resize update-confirm callers continue using the
  same freshness-derived helper.
