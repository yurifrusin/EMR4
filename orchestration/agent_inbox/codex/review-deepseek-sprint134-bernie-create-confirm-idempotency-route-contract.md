# review-deepseek-sprint134-bernie-create-confirm-idempotency-route-contract

| Item | Value |
|---|---|
| From | deepseek-worker |
| Source Task | Sprint 134 Bernie create-confirm idempotency route-test contract review |
| Status | integrated |
| Date | 2026-07-07 |

## Review Summary

DeepSeek reviewed the Sprint 133 preflight, current `confirm_bernie_create_proposal`
route, Bernie route outcome/session tests, and the staff create-confirm
idempotency route-test pattern.

The key recommendation was to make the no-double-session-event replay case the
headline Sprint 134 contract. `confirm_submitted` currently has a deterministic
session/proposal idempotency key, but `confirmation_outcome` is appended through
the route outcome helper and should not be trusted to deduplicate replay inside
the session store. Future wiring must return appointment-command replay,
conflict, in-progress, stale, and failed-transient decisions before the route can
append either `confirm_submitted` or `confirmation_outcome`.

## Required Contract Cases

- Missing `Idempotency-Key` must fail closed before appointment, audit, ledger,
  or Bernie session event mutation.
- First session-bound confirmed write must create one appointment, one audit
  trail, one completed ledger row, one `confirm_submitted`, and one
  `confirmation_outcome`.
- Same-key/same-body replay must return the stored response without a second
  appointment, audit row, ledger row, `confirm_submitted`, or
  `confirmation_outcome`.
- Same-key/different-body and preclaimed in-progress/stale/failed-transient rows
  must fail closed without appointment, audit, or session event mutation.
- Stale or mismatched `session_binding` must remain fail-closed and must not be
  bypassed by idempotency.
- Blocked post-claim outcomes should roll back/remove the ledger claim by
  default until a later policy explicitly approves replayable blocked responses.
- Non-session-bound confirmation must also replay without a second appointment or
  audit row, even though no Bernie session events are present.

## Integrated Into Sprint 134

The review was integrated into:

- `orchestration/api_spine_appointment_idempotency_bernie_create_confirm_route_tests.md`;
- `tests/test_api_spine_bernie_create_confirm_idempotency_route_contract.py`.

No route wiring, provider wiring, GraphQL mutation, H15/H-series runtime import,
memory/RAG/GraphRAG use, broad historical diary trove access, or update/status/
delete/raw/proposal-only idempotency change was made.
