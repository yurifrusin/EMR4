# DeepSeek Review - Sprint 143 Delete-Confirm Idempotency Route Contract

| Item | Value |
|---|---|
| Sprint | 143 |
| Lane | DeepSeek worker |
| Date | 2026-07-07 |
| Status | Integrated into Ariadne route-test contract |

## Verdict

Proceed with the guarded delete-confirm route-test contract before wiring. The
route should remain unwired in Sprint 143.

## Key Findings Integrated

- Add future cases for already-cancelled and non-existent appointments before
  ledger mutation.
- Treat `confirmed_warnings` and the full nested `delete_proposal` as part of
  the same-key conflict surface.
- Preserve replay after intervening raw DELETE as a stored-response behavior.
- Add invalid `status_reason_code`, missing signed evidence, and both
  waiting-area mismatch directions as blocked no-write cases.
- Record that replay should preserve merged `confirmed_warnings`.
- Record that different keys on the same appointment are appointment-write
  concurrency, not idempotency protection.
- Preserve raw DELETE default commit behavior and no `Idempotency-Key` semantics.

## Next Step

Sprint 144 should wire delete-confirm only after converting these guarded cases
to executable tests.
