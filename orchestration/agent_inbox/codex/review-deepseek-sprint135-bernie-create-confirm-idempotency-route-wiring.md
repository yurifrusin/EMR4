# review-deepseek-sprint135-bernie-create-confirm-idempotency-route-wiring

| Item | Value |
|---|---|
| From | deepseek-worker |
| Source Task | Sprint 135 Bernie create-confirm idempotency route wiring review |
| Status | integrated |
| Date | 2026-07-07 |

## Review Summary

DeepSeek reviewed the Sprint 134 contract and current `confirm_bernie_create_proposal`
route before wiring. Its core implementation advice was:

- validate `BernieCreateProposalConfirmationIn` before canonical hashing;
- claim the appointment command ledger before signed evidence, freshness,
  session binding, entity checks, `confirm_submitted`, or
  `confirmation_outcome`;
- return replay/conflict/in-progress/stale/failed-transient decisions before any
  Bernie session event append;
- change `_create_appointment_from_body(...)` to `commit=False`;
- complete the appointment command ledger and commit once after appointment,
  audit, response body, and ledger result are prepared;
- make no-double-session-event replay the primary safety invariant.

## Integrated Decision

Sprint 135 implemented the route-level replay gate before session events and
kept blocked responses rolling back the uncommitted ledger claim, matching the
Sprint 133/134 default policy. Session-bound blocked outcomes may still append
the existing Bernie session outcome event when current route semantics do so,
but they do not leave a durable completed appointment idempotency row.

No provider, GraphQL, H15/H-series runtime import, memory/RAG/GraphRAG, broad
historical diary trove, raw compatibility, proposal-only, update, status, or
delete idempotency wiring was added.
