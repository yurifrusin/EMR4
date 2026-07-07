# API Spine Status-Confirm Idempotency Route Tests

| Item | Value |
|---|---|
| Sprint | 137 |
| Programme | Programme 2G / EMR4 API Spine |
| Date | 2026-07-07 |
| Status | Guarded route-test contract only; no route behavior changed |
| Steward posture | Define deterministic status-confirm idempotency route tests before enabling HTTP `Idempotency-Key` |

## Source Pass

Reviewed sources:

- `orchestration/api_spine_appointment_idempotency_status_confirm_preflight.md`
- `orchestration/api_spine_appointment_idempotency_staff_create_confirm_route_tests.md`
- `orchestration/api_spine_appointment_idempotency_bernie_create_confirm_route_tests.md`
- `app/routers/appointments.py`
- `app/schemas/appointments.py`
- `app/services/appointment_idempotency.py`
- `tests/test_appointment_status_mutations.py`
- `tests/test_reason_code_backend.py`
- `tests/test_appointment_audit.py`
- `orchestration/agent_inbox/codex/review-deepseek-sprint136-status-confirm-idempotency-preflight.md`
- `orchestration/agent_inbox/codex/review-deepseek-sprint137-status-confirm-idempotency-route-contract.md`

## Route Under Test

- route: `POST /api/v1/appointments/proposals/status-confirm`;
- canonical OpenAPI path alias:
  `POST /api/v1/appointments/proposals/status/confirm`;
- handler: `confirm_status_proposal_route`;
- typed body: `AppointmentStatusProposalConfirmationIn`;
- canonical operation id: `confirmAppointmentStatusProposal`;
- route family: `status-confirm`.

Sprint 137 does not wire the route. It creates the guarded route-test contract
that Sprint 138 should enable while adding HTTP `Idempotency-Key` enforcement.
DeepSeek's Sprint 136 review is the recorded reason this contract targets
`status-confirm` before `update-confirm` or `delete-confirm`.

## Explicitly Out Of Scope

Do not wire beyond the approved `status-confirm` route-test surface:

- update-confirm and delete-confirm;
- raw compatibility writes such as `PUT /{appointment_id}`,
  `PATCH /{appointment_id}/status`, and `DELETE /{appointment_id}`;
- proposal-only routes such as `POST /api/v1/appointments/proposals/status/{id}`;
- slot-search, Bernie interpretation, supervised-booking, or Bernie session
  event routes;
- provider, GraphQL, H15/H-series, memory/RAG/GraphRAG, broad historical diary
  trove, external patient client, runtime FGA, or model-to-database surfaces.

## Future Executable Behavior Matrix

Sprint 138 wiring should enable deterministic tests for:

1. missing `Idempotency-Key` returns a fail-closed error before ledger,
   appointment, waiting-area, or audit mutation;
2. invalid status confirmation payload does not create a ledger row by default;
3. first confirmed status change writes exactly one appointment status update,
   one audit row, and one completed ledger row;
4. first confirmed waiting-area command writes exactly one waiting-area update,
   one audit row, and one completed ledger row;
5. same-key/same-body status replay returns the stored response without a
   second audit row or repeated status mutation;
6. same-key/same-body waiting-area replay returns the stored response without a
   second audit row or repeated waiting-area mutation;
7. same-key/different-body returns `409 idempotency_key_conflict` without an
   appointment or audit mutation;
8. active `in_progress` returns `409 idempotency_key_in_progress` without an
   appointment or audit mutation;
9. stale `in_progress` returns `409 idempotency_key_stale_in_progress` without
   an appointment or audit mutation;
10. `failed_transient` returns `503 idempotency_key_failed_transient` without
    an appointment or audit mutation;
11. `Idempotency-Key` does not bypass `confirmed=true`;
12. `Idempotency-Key` does not bypass signed confirmation evidence verification;
13. `Idempotency-Key` does not bypass `status_proposal_freshness_id`;
14. status proposal and waiting-area proposal union variants canonicalize
    stably and distinct effective commands do not collide;
15. blocked responses after a started claim roll back or remove the claim unless
    a future reviewed policy makes blocked status confirmations replayable;
16. replay telemetry is distinguishable from a new confirmed status mutation.

## Commit Boundary Gotcha

`confirm_status_proposal_route` currently calls `_apply_appointment_status_update`,
and `_apply_appointment_status_update` commits internally. Sprint 138 wiring
must not complete the appointment/audit transaction before completing the
idempotency ledger. The expected wiring shape is:

1. apply status/waiting-area state;
2. write status-change audit;
3. complete the appointment command ledger with the response body and target
   appointment id;
4. commit once.

Because `_apply_appointment_status_update` is also used by raw
`PATCH /api/v1/appointments/{appointment_id}/status`, the no-early-commit path
must stay scoped to the proposal-confirm route and must not accidentally wire
raw compatibility status changes.

## Metadata Boundary

`_STATUS_CONFIRM_METADATA_FIELDS` is part of signed-evidence payload shaping.
It removes proposal metadata such as `confirm_endpoint`, `confirm_payload`,
`status_proposal_freshness_id`, and signed-evidence fields from the signed
payload. It must not be treated as the idempotency request-body canonicalizer.
Future tests should prove stored-response replay remains structurally valid
while canonical request hashing still uses the validated confirmation body.

DeepSeek's Sprint 137 review suggested excluding these metadata fields from the
idempotency hash. Ariadne leaves that as an explicit Sprint 138 decision because
the current storage design says to include confirmation payload fields that the
write depends on, and the already wired create-confirm routes hash the full
validated confirmation body. Sprint 138 chooses the same full validated
confirmation body hashing for `status-confirm`; metadata exclusion remains a
future cross-route canonicalization-version decision.

## Guarded Test File

`tests/test_api_spine_status_confirm_idempotency_route_contract.py` now:

- passes static scope checks;
- records skipped future behavior tests for the matrix above;
- asserts the current router has not yet wired `status-confirm` with
  `Idempotency-Key`, `claim_appointment_command`, or
  `complete_appointment_command`;
- asserts current status-confirm tests cover signed-evidence, freshness,
  waiting-area, terminal/historical, and audit behavior that Sprint 138 must
  preserve.

## Smallest Next Alignment Slice

Recommended Sprint 138:

**Status-confirm idempotency route wiring.**

Wire only `POST /api/v1/appointments/proposals/status-confirm` after turning the
guarded Sprint 137 behavior matrix into executable tests. Keep update-confirm,
delete-confirm, raw compatibility writes, proposal-only routes, providers,
GraphQL, H15/H-series, memory/RAG/GraphRAG, runtime FGA, external patient
clients, and broad trove material out of scope.
