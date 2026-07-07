# Claude Packet - Sprint 144 Delete-Confirm Idempotency Wiring Review

| Item | Value |
|---|---|
| Sprint | 144 |
| Requested lane | Claude review |
| Date | 2026-07-07 |
| Status | Queued protocol packet; Ariadne wired delete-confirm locally |

## Review Target

Review the narrow delete-confirm idempotency wiring:

- `app/routers/appointments.py`
- `tests/test_api_spine_delete_confirm_idempotency_route_contract.py`
- `tests/test_appointment_status_mutations.py`
- `tests/test_api_spine_appointment_idempotency_route_integration_preflight.py`

## Acceptance Questions

- Does only `POST /api/v1/appointments/proposals/delete-confirm` gain
  `Idempotency-Key` enforcement?
- Does `_apply_appointment_delete(..., commit=False)` keep appointment delete,
  audit row, ledger completion, and final commit in one transaction, while raw
  `DELETE` still uses the default commit path?
- Do blocked destructive checks roll back started claims before returning?
- Do replay/conflict/preclaim tests prove no duplicate soft-cancel or audit row?

## Out Of Scope

Raw delete idempotency, proposal-only delete idempotency, providers, GraphQL
mutation, H15/H-series runtime imports, memory/RAG/GraphRAG, runtime FGA,
external patient clients, and broad historical diary trove work remain closed.
