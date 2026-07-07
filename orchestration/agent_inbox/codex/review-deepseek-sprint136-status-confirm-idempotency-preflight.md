# DeepSeek Review - Sprint 136 Status-Confirm Idempotency Preflight

| Item | Value |
|---|---|
| Sprint | 136 |
| Lane | DeepSeek worker |
| Date | 2026-07-07 |
| Status | Integrated into Ariadne preflight |

## Recommendation

Choose `status-confirm` before `update-confirm` and `delete-confirm`.

DeepSeek's review found that `status-confirm` has the cleanest next wiring
shape:

- route: `POST /api/v1/appointments/proposals/status-confirm`;
- handler: `confirm_status_proposal_route`;
- body: `AppointmentStatusProposalConfirmationIn`;
- operation id: `confirmAppointmentStatusProposal`;
- route family: `status-confirm`.

The main rationale was that status-confirm is self-contained, has no
`turn_ref` or `session_binding`, does not re-run the broader update proposal
revalidation path, and already has strong signed-evidence/freshness coverage.
It is a real appointment mutation, but its route shape is simpler than
update-confirm and less destructive than delete-confirm.

## Comparison Notes

- `update-confirm` remains valuable later, but it shifts date/time/duration/
  practitioner fields and re-runs `propose_update_appointment()`, increasing
  the concurrent-state window.
- `delete-confirm` should remain later because it soft-cancels appointments,
  clears waiting-area state, and carries cancellation/status reason evidence.
- `status-confirm` may still set or clear waiting-area state, so replay tests
  must count both audit rows and waiting-area/status side effects.

## Sprint 137 Gotchas

- `_apply_appointment_status_update()` currently commits internally and is also
  used by raw `PATCH /api/v1/appointments/{appointment_id}/status`. Wiring
  should introduce a safe no-early-commit path for the proposal-confirm route
  or otherwise prove ledger completion cannot be left behind the committed
  appointment/audit write.
- The status confirmation body is a union:
  `AppointmentStatusProposalOut | AppointmentWaitingAreaProposalOut`. Future
  tests should prove canonical hashing is stable and that distinct effective
  commands do not collide.
- `Idempotency-Key` must not bypass `confirmed=true`, signed confirmation
  evidence, or `status_proposal_freshness_id`.
- `_STATUS_CONFIRM_METADATA_FIELDS` is signed-evidence metadata handling, not
  idempotency canonicalization. Sprint 137 tests should keep those concepts
  distinct and prove stored response replay remains structurally valid.
- The backend alias `/status-confirm` and canonical OpenAPI path
  `/status/confirm` should continue to share the same operation identity.

## Integrated Decision

Ariadne accepted the recommendation and pivoted Sprint 136 from the initial
`update-confirm` draft to the committed `status-confirm` preflight:

- `orchestration/api_spine_appointment_idempotency_status_confirm_preflight.md`
- `tests/test_api_spine_status_confirm_idempotency_preflight.py`

No route behavior was changed in Sprint 136.
