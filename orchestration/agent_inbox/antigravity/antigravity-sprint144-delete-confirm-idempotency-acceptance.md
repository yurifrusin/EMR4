# Antigravity Packet - Sprint 144 Delete-Confirm Idempotency Acceptance

| Item | Value |
|---|---|
| Sprint | 144 |
| Requested lane | Antigravity acceptance |
| Date | 2026-07-07 |
| Status | Queued protocol packet; Antigravity is considered available through the project protocol/UI |

## Acceptance Target

Validate the Sprint 144 delete-confirm idempotency wiring against the Sprint 143
contract.

Files to inspect:

- `app/routers/appointments.py`
- `tests/test_api_spine_delete_confirm_idempotency_route_contract.py`
- `tests/test_appointment_status_mutations.py`
- `orchestration/agent_inbox/codex/review-deepseek-sprint144-delete-confirm-idempotency-wiring.md`

## Expected Posture

- `POST /api/v1/appointments/proposals/delete-confirm` requires
  `Idempotency-Key`.
- Same-key replay returns the stored completed response without duplicate audit
  or soft-cancel effects.
- Same-key/different-body conflicts without mutation.
- Started claims are rolled back on blocked confirmation responses.
- Raw delete and proposal-only delete routes remain outside idempotency wiring.

## Acceptance Signal

Accept if destructive replay/rollback behavior is test-backed and the wiring is
strictly scoped to delete-confirm.
