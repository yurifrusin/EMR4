# API Spine Delete-Confirm Idempotency Preflight

| Item | Value |
|---|---|
| Sprint | 142 |
| Programme | Programme 2G / EMR4 API Spine |
| Date | 2026-07-07 |
| Status | Preflight/review only; no route behavior changed |
| Steward posture | Choose the delete-confirm route-test shape before wiring the destructive soft-cancel confirmation path |

## Source Pass

Reviewed sources:

- `orchestration/api_spine_adr.md`
- `orchestration/api_spine_programme.md`
- `orchestration/api_spine_appointment_idempotency_update_confirm_route_tests.md`
- `orchestration/agent_inbox/codex/review-deepseek-sprint141-update-confirm-idempotency-wiring.md`
- `app/routers/appointments.py`
- `app/schemas/appointments.py`
- `app/services/appointment_idempotency.py`
- `tests/test_appointment_status_mutations.py`
- `tests/test_appointment_audit.py`
- `tests/test_reason_code_backend.py`
- `orchestration/agent_inbox/codex/review-deepseek-sprint142-delete-confirm-idempotency-preflight.md`

## Candidate Family Decision

The next narrow confirmation family should be:

- route: `POST /api/v1/appointments/proposals/delete-confirm`;
- handler: `confirm_delete_proposal_route`;
- implementation helper: `_apply_appointment_delete`;
- typed body: `AppointmentDeleteProposalConfirmationIn`;
- canonical operation id: `confirmAppointmentDeleteProposal`;
- proposed route family label: `delete-confirm`;
- writes today: one existing appointment row soft-cancel, waiting-area clear,
  optional cancellation/status reason evidence, and one
  `AppointmentAuditAction.delete` audit row.

`delete-confirm` is the next family after update-confirm because it is the last
proposal-confirm appointment mutation family still missing HTTP idempotency. It
is more destructive than update-confirm because it soft-cancels the appointment
and clears waiting-area state, so Sprint 142 deliberately stops at preflight and
does not wire the route.

## Do Not Wire Yet

Do not enforce HTTP `Idempotency-Key` on `delete-confirm` in Sprint 142. Do not
wire raw compatibility `DELETE /api/v1/appointments/{appointment_id}`,
proposal-only routes such as `POST /api/v1/appointments/proposals/delete/{id}`,
slot-search routes, Bernie session routes, providers, GraphQL mutations,
memory/RAG/GraphRAG, H15/H-series runtime imports, external patient clients,
runtime FGA clients, or broad historical diary trove material.

## Extra Boundary Compared With Update-Confirm

Delete-confirm has a smaller revalidation surface than update-confirm but a
higher semantic risk:

1. `confirm_delete_proposal_route` performs all confirmation checks in the route
   body today;
2. it verifies `confirmed=true`, proposal safety, signed evidence, delete
   proposal freshness, and waiting-area state;
3. it applies a soft cancel through `_apply_appointment_delete()`;
4. `_apply_appointment_delete()` currently commits internally;
5. delete confirmation sets `status=Cancelled`, clears `waiting_area_id`,
   persists optional `cancellation_reason` and optional `status_reason_code`,
   and writes `AppointmentAuditAction.delete`.

Sprint 143 should add the guarded route-test contract before Sprint 144 wiring.
Sprint 144 wiring should mirror update-confirm: add a scoped `commit=False`
path to `_apply_appointment_delete`, apply the soft-cancel and audit row,
complete the ledger, then commit once.

## Proposed Claim Order

1. authenticate and authorize actor/practice;
2. require and normalize HTTP `Idempotency-Key`;
3. validate `AppointmentDeleteProposalConfirmationIn`;
4. canonicalize the validated body using `model_dump(mode="json")`;
5. claim the appointment command ledger with operation id
   `confirmAppointmentDeleteProposal` and route family `delete-confirm`;
6. return replay/conflict/in-progress/stale/failed-transient decisions before
   `confirmed=true`, signed evidence, freshness, waiting-area state, soft
   cancel, or audit mutation checks;
7. run existing `confirmed=true`, proposal safety, signed evidence, freshness,
   and waiting-area-state checks;
8. if blocked after the claim, call `db.rollback()` before returning the blocked
   response;
9. on confirmed write, soft-cancel the appointment without an early commit,
   complete the ledger with the final response body and target appointment id,
   then commit once;
10. on same-key replay, return the stored response without re-running delete
    checks, clearing waiting-area state again, or adding another audit row.

## Required Route-Test Contract

Recommended Sprint 143 should add guarded or executable tests for:

- missing `Idempotency-Key` blocks before ledger, appointment, or audit mutation;
- blank/whitespace `Idempotency-Key` is treated as missing;
- invalid delete confirmation payload does not create a ledger row;
- first confirmed delete writes exactly one soft-cancel, one audit row, clears
  waiting-area state when applicable, persists reason evidence, and completes
  one ledger row;
- same-key/same-body replay returns the stored response without a second audit
  row or repeated soft-cancel side effect;
- same-key replay after an intervening raw `DELETE /api/v1/appointments/{id}`
  returns the stored response without re-running delete checks;
- same-key/different-body returns `409 idempotency_key_conflict` without
  appointment or audit mutation;
- active `in_progress`, stale `in_progress`, and `failed_transient` rows fail
  closed without appointment or audit mutation;
- `Idempotency-Key` does not bypass `confirmed=true`, signed confirmation
  evidence, `delete_proposal_freshness_id`, or waiting-area state checks;
- blocked checks after a started claim roll back the claim;
- full validated confirmation-body hashing remains consistent with create,
  status, and update-confirm unless a future versioned cross-route
  canonicalization change is explicitly approved;
- delete-confirm remains scoped away from raw `DELETE`, proposal-only routes,
  and already-wired create/status/update confirmation routes.
- raw `DELETE /api/v1/appointments/{appointment_id}` keeps default
  `_apply_appointment_delete()` commit behavior and gains no
  `Idempotency-Key` semantics.

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

Recommended Sprint 143:

**Delete-confirm idempotency route-test contract.**

Add the guarded route-test contract for
`POST /api/v1/appointments/proposals/delete-confirm` before enforcing HTTP
`Idempotency-Key` on that route.
