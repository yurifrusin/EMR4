# Claude Packet - Sprint 143 Delete-Confirm Idempotency Route Contract

| Item | Value |
|---|---|
| Sprint | 143 |
| Requested lane | Claude review |
| Date | 2026-07-07 |
| Status | Queued protocol packet; Ariadne integrated route-test contract locally |

## Review Target

Review the guarded Sprint 143 route-test contract for
`POST /api/v1/appointments/proposals/delete-confirm`.

Primary files:

- `orchestration/api_spine_appointment_idempotency_delete_confirm_route_tests.md`
- `tests/test_api_spine_delete_confirm_idempotency_route_contract.py`
- `orchestration/api_spine_appointment_idempotency_delete_confirm_preflight.md`
- `app/routers/appointments.py`

## Acceptance Questions

- Does the contract keep Sprint 143 as test/documentation only, with no
  `Idempotency-Key` behavior wired yet?
- Are destructive delete-confirm semantics covered: soft-cancel, audit row,
  waiting-area clear, cancellation/status reason evidence, and rollback on
  blocked started claims?
- Does Sprint 144 have enough executable-test scaffolding to wire only the
  delete-confirm route without touching raw delete, proposal-only delete,
  providers, GraphQL, H15/H-series, memory/RAG/GraphRAG, or broad trove gates?

## Ariadne Notes

DeepSeek's Sprint 143 review was integrated before closeout. It added explicit
future cases for already-cancelled/non-existent appointment blocks, full body
conflict coverage including `confirmed_warnings` and nested `delete_proposal`,
both waiting-area mismatch directions, invalid reason codes, missing signed
evidence, and same-appointment/different-key concurrency scope.
