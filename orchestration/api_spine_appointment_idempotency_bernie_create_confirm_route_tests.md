# API Spine Bernie Create-Confirm Idempotency Route Tests

| Item | Value |
|---|---|
| Sprint | 134 |
| Programme | Programme 2G / EMR4 API Spine |
| Date | 2026-07-07 |
| Status | Sprint 135 wiring completed; `confirm-bernie` route tests executable |
| Steward posture | Define deterministic Bernie create-confirm idempotency route tests before enabling HTTP `Idempotency-Key` |

## Source Pass

Reviewed sources:

- `orchestration/api_spine_appointment_idempotency_bernie_create_confirm_preflight.md`
- `orchestration/api_spine_appointment_idempotency_staff_create_confirm_route_tests.md`
- `app/routers/appointments.py`
- `app/schemas/appointments.py`
- `app/services/appointment_idempotency.py`
- `tests/test_bernie_confirm_create_proposal.py`
- `tests/test_bernie_route_outcome_events.py`
- `tests/test_bernie_session_store.py`
- `tests/test_api_spine_staff_create_confirm_idempotency_route_contract.py`
- `orchestration/agent_inbox/codex/review-deepseek-sprint134-bernie-create-confirm-idempotency-route-contract.md`

## Route Under Test

- route: `POST /api/v1/appointments/proposals/create/confirm-bernie`;
- handler: `confirm_bernie_create_proposal`;
- typed body: `BernieCreateProposalConfirmationIn`, after manual validation;
- canonical operation id: `confirmAppointmentCreateProposal`;
- route family: `create-confirm-bernie`.

Sprint 134 scope: Guarded route-test contract only. Sprint 135 consumed that
contract and wired `Idempotency-Key` enforcement for `confirm-bernie` only.

## Explicitly Out Of Scope

Do not wire beyond the approved `confirm-bernie` surface:

- staff create-confirm, which is already covered by Sprint 132;
- update/status/delete confirmation routes;
- raw compatibility writes;
- proposal-only routes such as `POST /api/v1/appointments/proposals/create`;
- slot-search, Bernie interpretation, supervised-booking, or Bernie session event routes;
- provider, GraphQL, H15/H-series, memory/RAG/GraphRAG, broad historical diary trove, or model-to-database surfaces.

## Executable Behavior Matrix

Sprint 135 wiring enables deterministic tests for:

1. missing `Idempotency-Key` returns a fail-closed error before appointment,
   audit, ledger, `confirm_submitted`, or `confirmation_outcome` mutation;
2. invalid manually validated payload preserves current structured blocked
   response unless a compatibility sprint approves an HTTP status change, and
   does not create a ledger row by default;
3. first confirmed Bernie create with a bound session writes exactly one
   appointment, one audit trail, one completed ledger row, one
   `confirm_submitted`, and one `confirmation_outcome`;
4. same-key/same-body replay returns the stored response without a second
   appointment, audit row, `confirm_submitted`, or `confirmation_outcome`;
5. same-key/different-body returns `409 idempotency_key_conflict` without a
   second appointment, audit row, or Bernie session event;
6. same-key active `in_progress` returns `409 idempotency_key_in_progress`
   or a reviewed equivalent, without appointment, audit, or Bernie session
   event mutation;
7. stale `in_progress` returns `409 idempotency_key_stale_in_progress`
   without appointment, audit, or Bernie session event mutation;
8. `failed_transient` returns `503 idempotency_key_failed_transient` without
   appointment, audit, or Bernie session event mutation;
9. stale or mismatched `session_binding` remains fail-closed and is not bypassed
   by idempotency;
10. post-claim business-rule blocks roll back or remove the claim unless a
    later policy explicitly makes blocked Bernie confirmations replayable;
11. replay telemetry is distinguishable from a new confirmed mutation and does
    not look like a second appointment write or second Bernie session transition.

## Session-Event Replay Boundary

`confirm-bernie` differs from staff create-confirm because it mutates the
server-owned Bernie session store when a binding is present. The appointment
command ledger must therefore be claimed before any `confirm_submitted` or
`confirmation_outcome` append, and replay/conflict/in-progress decisions must
return before session-store mutation.

The minimum safe replay invariant is:

- completed same-body replay returns the stored appointment-confirm response;
- appointment and audit row counts do not change;
- the Bernie session event list does not gain another `confirm_submitted`;
- the Bernie session event list does not gain another `confirmation_outcome`;
- session state and revision do not advance from replay alone.

DeepSeek review for Sprint 134 identified `confirmation_outcome` as the most
concrete double-event risk: `confirm_submitted` has a deterministic per-event
idempotency key tied to session/proposal freshness, but `confirmation_outcome`
is appended by the route outcome helper and must not rely on the session store
to deduplicate replay. Sprint 135 wiring must therefore prove the route-level
appointment command ledger returns replay/conflict/in-progress decisions before
the `_append_confirmation_outcome` closure can run.

The route-test contract should cover both:

- session-bound confirmation, where `confirm_submitted` and
  `confirmation_outcome` are expected on first write and forbidden on replay;
- non-session-bound confirmation, where replay still must not create a second
  appointment/audit row even though no Bernie session event is present.

## Guarded Test File

`tests/test_api_spine_bernie_create_confirm_idempotency_route_contract.py` now:

- passes static scope checks;
- executes the behavior matrix above;
- asserts the current router wires `confirm-bernie` with `Idempotency-Key`,
  `claim_appointment_command`, and `complete_appointment_command`;
- asserts existing Bernie confirm tests now send idempotency keys deliberately;
- asserts the current route still contains `confirm_submitted` and
  `confirmation_outcome`, so no-double-session-event replay remains guarded.

## Smallest Next Alignment Slice

Recommended Sprint 136:

**Next confirmation-family preflight.**

Review whether update, status, or delete confirmation is the safest next
appointment command family. Keep raw, proposal-only, provider, GraphQL,
H15/H-series, memory/RAG/GraphRAG, and broad trove gates closed.
