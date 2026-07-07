# DeepSeek Review - Sprint 142 Delete-Confirm Idempotency Preflight

| Item | Value |
|---|---|
| Sprint | 142 |
| Lane | DeepSeek worker |
| Date | 2026-07-07 |
| Status | Integrated into Ariadne preflight |

## Verdict

The delete-confirm preflight is ready. No route behavior should change in
Sprint 142.

## Key Findings Integrated

- `confirm_delete_proposal_route` has no idempotency wiring yet.
- `_apply_appointment_delete()` currently commits internally and needs a scoped
  `commit=False` path before route wiring.
- Delete-confirm is simpler than update-confirm because it does not re-run a
  proposal/revalidation helper, but it is semantically more destructive because
  it soft-cancels the appointment and clears waiting-area state.
- Existing freshness and waiting-area-state checks are the right confirm-time
  revalidation boundary.
- Blocked started claims should use `db.rollback()`, matching status/update
  confirm.
- Raw `DELETE /api/v1/appointments/{appointment_id}` must keep default commit
  behavior and gain no `Idempotency-Key` semantics.
- Sprint 143 route tests should include replay after an intervening raw delete,
  proving replay returns the original stored response rather than revalidating.

## Next Step

Proceed to Sprint 143: guarded delete-confirm route-test contract before any
destructive route wiring.
