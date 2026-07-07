# DeepSeek Review - Sprint 141 Update-Confirm Idempotency Wiring

| Item | Value |
|---|---|
| Sprint | 141 |
| Lane | DeepSeek worker |
| Date | 2026-07-07 |
| Status | Integrated into Ariadne wiring and tests |

## Verdict

The update-confirm wiring follows the Sprint 140 accepted shape:

- `Idempotency-Key` is owned by `confirm_update_proposal_route()`;
- claims use `confirmAppointmentUpdateProposal` and route family
  `update-confirm`;
- replay/conflict/in-progress/stale/failed decisions return before
  `confirm_update_proposal()` can re-run update revalidation;
- request hashing uses `request_body=body.model_dump(mode="json")`;
- blocked started claims roll back transactionally;
- `_apply_appointment_update()` has a scoped `commit=False` path for
  confirmation wiring while raw PUT keeps default commit behavior.

## Integrated Follow-Ups

- Converted the Sprint 140 guarded future cases into executable route tests.
- Updated existing update-confirm tests to send `Idempotency-Key`.
- Kept raw PUT and proposal-only routes out of scope.
- Recorded actor-scoped and stale replay semantics as accepted boundaries.

## Residual Risk

Replay after an intervening raw update returns the stored response body by
design. This is consistent with idempotency semantics but can show an older
appointment snapshot to the retrying client; consumers should treat replay
responses as the original command result, not as a fresh read model.
