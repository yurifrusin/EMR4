# DeepSeek Review - Sprint 137 Status-Confirm Idempotency Route Contract

| Item | Value |
|---|---|
| Sprint | 137 |
| Lane | DeepSeek worker |
| Date | 2026-07-07 |
| Status | Integrated as review guidance; no route wiring |

## Review Summary

DeepSeek reviewed the guarded route-test contract for
`POST /api/v1/appointments/proposals/status-confirm` and confirmed the main
Sprint 137 test matrix:

- missing `Idempotency-Key` must block before ledger, appointment, waiting-area,
  or audit mutation;
- invalid typed payloads should not create a ledger row by default;
- first confirmed status/waiting-area writes should create one status or
  waiting-area mutation, one audit row, and one completed ledger row;
- same-key/same-body replay must return the stored response without a second
  status/waiting-area mutation or audit row;
- same-key/different-body should return `409 idempotency_key_conflict`;
- active `in_progress`, stale `in_progress`, and `failed_transient` claims
  should fail closed without mutation;
- idempotency must not bypass `confirmed=true`, signed evidence, or
  `status_proposal_freshness_id`;
- replay telemetry must be distinguishable from a new status mutation.

## Critical Sprint 138 Gotchas

1. `_apply_appointment_status_update()` commits internally. Sprint 138 wiring
   must not commit the appointment/audit write before completing the
   idempotency ledger. The preferred path remains a scoped no-early-commit
   option for the status-confirm route.
2. `AppointmentStatusProposalConfirmationIn.status_proposal` is a union of
   `AppointmentStatusProposalOut | AppointmentWaitingAreaProposalOut`. Future
   executable tests should prove distinct effective commands do not collide.
3. `_block_status_confirmation()` is currently a pure response builder. If a
   claim is started before business-rule checks and the checks block, Sprint 138
   wiring must roll back or remove the claim before returning the blocked
   response.
4. Terminal status changes can clear waiting-area state. Replay must not
   reapply that side effect or create a second audit row.

## Open Canonicalization Decision

DeepSeek recommended excluding `_STATUS_CONFIRM_METADATA_FIELDS` from the
idempotency request-body hash so retries with equivalent command content but
different signed-evidence metadata do not conflict.

Ariadne did not adopt that as settled Sprint 137 policy. The existing storage
design says canonicalization should parse the typed body, exclude transient
request metadata such as correlation id, and include confirmation payload fields
that the write depends on. Existing wired create-confirm routes currently hash
the full validated confirmation body. Sprint 138 should make an explicit,
tested decision for status-confirm rather than changing canonicalization policy
by implication.

Until that decision is made, Sprint 137 documents `_STATUS_CONFIRM_METADATA_FIELDS`
as signed-evidence payload shaping, not as the idempotency canonicalizer.

## Integrated Result

The review reinforced the Sprint 137 route-test contract:

- `orchestration/api_spine_appointment_idempotency_status_confirm_route_tests.md`
- `tests/test_api_spine_status_confirm_idempotency_route_contract.py`

No route behavior was changed in Sprint 137.
