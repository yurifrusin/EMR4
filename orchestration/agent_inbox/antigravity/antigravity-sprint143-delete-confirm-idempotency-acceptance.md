# Antigravity Packet - Sprint 143 Delete-Confirm Idempotency Acceptance

| Item | Value |
|---|---|
| Sprint | 143 |
| Requested lane | Antigravity acceptance |
| Date | 2026-07-07 |
| Status | Queued protocol packet; Antigravity is considered available through the project protocol/UI |

## Acceptance Target

Validate the Sprint 143 guarded route-test contract for delete-confirm
idempotency before Sprint 144 route wiring.

Files to inspect:

- `orchestration/api_spine_appointment_idempotency_delete_confirm_route_tests.md`
- `tests/test_api_spine_delete_confirm_idempotency_route_contract.py`
- `orchestration/agent_inbox/codex/review-deepseek-sprint143-delete-confirm-idempotency-route-contract.md`

## Expected Posture

- Sprint 143 must leave `confirm_delete_proposal_route` unwired for
  `Idempotency-Key`.
- The contract must preserve destructive soft-cancel safeguards and make Sprint
  144's future behavior matrix explicit.
- Raw `DELETE /api/v1/appointments/{appointment_id}`, proposal-only delete
  routes, provider calls, runtime FGA/external clients, GraphQL mutations,
  H15/H-series runtime imports, memory/RAG/GraphRAG, and broad historical diary
  trove work remain out of scope.

## Acceptance Signal

Accept if the contract is narrow, test-backed, and sufficient for the next
single-route wiring sprint. Flag any missing destructive replay or rollback case
before Sprint 144 starts.
