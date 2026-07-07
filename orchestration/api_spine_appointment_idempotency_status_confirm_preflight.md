# API Spine Status-Confirm Idempotency Preflight

| Item | Value |
|---|---|
| Sprint | 136 |
| Programme | Programme 2G / EMR4 API Spine |
| Date | 2026-07-07 |
| Status | Preflight/review only; no route behavior changed |
| Steward posture | Choose the next confirmation family before widening HTTP `Idempotency-Key` enforcement beyond create-confirm |

## Source Pass

Reviewed sources:

- `orchestration/api_spine_adr.md`
- `orchestration/api_spine_programme.md`
- `orchestration/api_spine_appointment_idempotency_bernie_create_confirm_route_tests.md`
- `orchestration/api_spine_appointment_idempotency_route_integration_preflight.md`
- `app/routers/appointments.py`
- `app/schemas/appointments.py`
- `app/services/appointment_idempotency.py`
- `app/services/diary/action_route_contract.py`
- `tests/test_appointment_status_mutations.py`
- `tests/test_reason_code_backend.py`
- `tests/test_appointment_audit.py`
- `tests/test_api_spine_appointment_idempotency_gap.py`
- `orchestration/agent_inbox/codex/review-deepseek-sprint136-status-confirm-idempotency-preflight.md`

## Candidate Family Decision

The next narrow confirmation family should be:

- route: `POST /api/v1/appointments/proposals/status-confirm`;
- canonical OpenAPI path alias: `POST /api/v1/appointments/proposals/status/confirm`;
- handler: `confirm_status_proposal_route`;
- typed body: `AppointmentStatusProposalConfirmationIn`;
- canonical operation id: `confirmAppointmentStatusProposal`;
- proposed route family label: `status-confirm`;
- writes today: one appointment status/waiting-area update plus one
  `AppointmentAuditAction.status_change` audit row.

DeepSeek review changed the initial Ariadne preference from `update-confirm` to
`status-confirm`. The decisive reason is route shape: `status-confirm` has a
self-contained handler, a smaller confirmation body with no `turn_ref` or
`session_binding`, existing signed-evidence/freshness checks, and no
`propose_update_appointment()` revalidation window. It is still a real
appointment mutation, but it is simpler than update-confirm and less
irreversible than delete-confirm.

## Candidate Comparison

| Family | Route | Decision | Rationale |
|---|---|---|---|
| Status confirm | `POST /api/v1/appointments/proposals/status-confirm` | Choose for next route-test contract | Self-contained handler, simple body, signed evidence, freshness check, one status audit row, high-traffic Bernie grammar path |
| Update confirm | `POST /api/v1/appointments/proposals/update/confirm` | Defer | Existing-row mutation is useful later, but it re-runs update proposal revalidation and can shift date/time/practitioner/conflict state |
| Delete confirm | `POST /api/v1/appointments/proposals/delete-confirm` | Defer | Soft-cancels appointment, clears waiting area, persists cancellation/status reason evidence, and has more destructive workflow semantics |

## Do Not Wire Yet

Do not enforce HTTP `Idempotency-Key` on `status-confirm` in Sprint 136. Do not
wire update-confirm, delete-confirm, raw compatibility PUT/PATCH/DELETE routes,
proposal-only routes, slot-search routes, Bernie session routes, providers,
GraphQL mutations, memory/RAG/GraphRAG, H15/H-series runtime imports, external
patient clients, runtime FGA clients, or broad historical diary trove material.

## Extra Boundary Compared With Create-Confirm

Create-confirm idempotency protects against duplicate inserts. Status-confirm
must instead protect against duplicate status and waiting-area side effects:

1. same-key replay must not write a second status audit row;
2. same-key replay must not reapply waiting-area set/clear side effects;
3. same-key conflict must not apply a different status or waiting-area command;
4. idempotency claim must happen after typed body validation and before
   `confirmed=true`, signed evidence, freshness checks, waiting-area lookup,
   appointment mutation, or audit write;
5. blocked confirmation responses after a started claim should roll back the
   claim by default, matching the create-confirm posture until a reviewed
   policy approves replayable blocked responses;
6. successful completion should persist the ledger response in the same
   database transaction as the appointment status update and audit row.

The current helper `_apply_appointment_status_update` commits internally and is
also used by raw `PATCH /api/v1/appointments/{appointment_id}/status`.
Sprint 138 wiring should therefore either add a `commit=False` path for
status-confirm or otherwise prove the ledger cannot be left incomplete after
the appointment/audit commit. The preferred shape is the same as create-confirm:
update appointment state, write audit, complete ledger, then commit once.

## Proposed Claim Order

1. authenticate and authorize actor/practice;
2. require and normalize HTTP `Idempotency-Key`;
3. validate `AppointmentStatusProposalConfirmationIn`;
4. canonicalize the validated body using `model_dump(mode="json")`;
5. claim the appointment command ledger with operation id
   `confirmAppointmentStatusProposal` and route family `status-confirm`;
6. return replay/conflict/in-progress/stale/failed-transient decisions before
   confirmation checks, signed evidence, freshness checks, waiting-area lookup,
   appointment mutation, or audit write;
7. run existing `confirmed=true`, proposal-safety, signed-evidence, freshness,
   and waiting-area checks;
8. if blocked after the claim, roll back or remove the claim unless a future
   reviewed policy makes blocked status confirmations replayable;
9. on confirmed write, apply the status/waiting-area update and audit row
   without an early commit, complete the ledger with the final response body and
   target appointment id, then commit once;
10. on same-key replay, return the stored response without updating status,
    changing waiting-area state, or adding another audit row.

## Required Route-Test Contract

Recommended Sprint 137 should add guarded or executable tests for:

- missing `Idempotency-Key` blocks before ledger, appointment, or audit mutation;
- invalid status confirmation payload does not create a ledger row unless a
  later compatibility policy explicitly chooses replayable invalid responses;
- first confirmed status change writes exactly one appointment status update,
  one audit row, and one completed ledger row;
- same-key/same-body replay returns the stored response without a second audit
  row or repeated status/waiting-area mutation;
- same-key/different-body returns `409 idempotency_key_conflict` without an
  appointment or audit mutation;
- active `in_progress`, stale `in_progress`, and `failed_transient` rows fail
  closed without appointment or audit mutation;
- `Idempotency-Key` does not bypass `confirmed=true`, signed confirmation
  evidence, or status proposal freshness checks;
- status proposal and waiting-area proposal union variants canonicalize
  stably, and different effective commands do not collide;
- `_STATUS_CONFIRM_METADATA_FIELDS` remains separate from idempotency
  canonicalization and stored-response replay is structurally valid;
- completed replay telemetry is distinguishable from a new confirmed mutation;
- status-confirm idempotency remains scoped away from update-confirm,
  delete-confirm, raw compatibility writes, and proposal-only routes.

## Gates Still Closed

This preflight does not open:

- live providers;
- runtime FGA clients;
- external patient clients;
- GraphQL mutations;
- broad historical diary trove mining;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- model-to-database writes.

## Smallest Next Alignment Slice

Recommended Sprint 137:

**Status-confirm idempotency route-test contract.**

Add the guarded route-test contract for
`POST /api/v1/appointments/proposals/status-confirm` before enforcing HTTP
`Idempotency-Key` on that route.
