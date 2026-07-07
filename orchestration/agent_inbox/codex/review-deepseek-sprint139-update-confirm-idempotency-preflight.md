# DeepSeek Review - Sprint 139 Update-Confirm Idempotency Preflight

| Item | Value |
|---|---|
| Sprint | 139 |
| Lane | DeepSeek worker |
| Date | 2026-07-07 |
| Status | Integrated into Ariadne preflight |

## Recommendation

Stay with `update-confirm` as the next confirmation family before
`delete-confirm`.

DeepSeek independently compared:

- `POST /api/v1/appointments/proposals/update/confirm`
- `POST /api/v1/appointments/proposals/delete-confirm`

The review confirmed Ariadne's preflight choice. `delete-confirm` is simpler to
wire, but `update-confirm` should come first because it is reversible and
exercises the important revalidation pattern before the destructive soft-cancel
path.

## Key Findings

- `update-confirm` delegates from `confirm_update_proposal_route()` to
  `confirm_update_proposal()`.
- `confirm_update_proposal()` re-runs `propose_update_appointment()` before
  writing, so replay must return before revalidation and first execution must
  roll back started claims on any blocked revalidation.
- `_apply_appointment_update()` currently commits internally and needs the same
  scoped `commit=False` refactor that Sprint 138 applied to
  `_apply_appointment_status_update()`.
- Full validated confirmation-body hashing should remain the default:
  `request_body=body.model_dump(mode="json")`.
- `_UPDATE_CONFIRM_METADATA_FIELDS` is signed-evidence payload shaping only and
  must not become the idempotency request-body canonicalizer.

## Sprint 140 Contract Requirements

Sprint 140 should add the guarded update-confirm route-test contract for:

- missing `Idempotency-Key`;
- invalid typed payload without ledger row;
- first confirmed update with one appointment update, one audit row, and one
  completed ledger row;
- same-key/same-body replay with no second update or audit row;
- same-key/different-body conflict;
- active `in_progress`, stale `in_progress`, and `failed_transient` rows;
- no bypass of `confirmed=true`, signed evidence, freshness, or update
  revalidation;
- blocked revalidation rolling back or removing the started claim.

## User Decision

No explicit user decision is required for Sprint 140 if Ariadne stays with the
preflight recommendation:

- family order: update-confirm before delete-confirm;
- blocked revalidation: roll back the claim;
- implementation shape: add `commit=False` to `confirm_update_proposal()` and
  `_apply_appointment_update()`;
- replay decision mapping: reuse the existing generic idempotency decision
  mapper.

No route behavior changed in Sprint 139.
