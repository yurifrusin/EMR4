# API Spine Appointment Idempotency Confirmation-Family Checkpoint

| Item | Value |
|---|---|
| Sprint | 145 |
| Programme | Programme 2G / EMR4 API Spine |
| Date | 2026-07-07 |
| Status | Checkpoint/audit only; no route behavior changed |
| Steward posture | Confirm the appointment proposal-confirm mutation families are wired before any broader idempotency expansion |

## Wired Confirmation Families

| Family | Route | Handler | Operation id | Route family |
|---|---|---|---|---|
| Staff create confirm | `POST /api/v1/appointments/proposals/create/confirm` | `confirm_create_proposal_route` | `confirmAppointmentCreateProposal` | `create-confirm` |
| Bernie create confirm | `POST /api/v1/appointments/proposals/create/confirm-bernie` | `confirm_bernie_create_proposal` | `confirmAppointmentCreateProposal` | `create-confirm-bernie` |
| Status confirm | `POST /api/v1/appointments/proposals/status-confirm` | `confirm_status_proposal_route` | `confirmAppointmentStatusProposal` | `status-confirm` |
| Update confirm | `POST /api/v1/appointments/proposals/update/confirm` | `confirm_update_proposal_route` | `confirmAppointmentUpdateProposal` | `update-confirm` |
| Delete confirm | `POST /api/v1/appointments/proposals/delete-confirm` | `confirm_delete_proposal_route` | `confirmAppointmentDeleteProposal` | `delete-confirm` |

All five routes require and normalize HTTP `Idempotency-Key`, call
`claim_appointment_command()` before the state-changing command body is allowed
to write, return completed replays from stored response JSON, fail closed for
conflict/in-progress/stale/failed rows, and call `complete_appointment_command()`
before the final route commit.

## Fail-Closed Decision Map

| Decision kind | HTTP response | Code/body source |
|---|---|---|
| `replay` | Stored status | Stored response body |
| `conflict` | `409` | `idempotency_key_conflict` |
| `in_progress` | `409` | `idempotency_key_in_progress` |
| `stale_in_progress` | `409` | `idempotency_key_stale_in_progress` |
| `failed_transient` | `503` | `idempotency_key_failed_transient` |

## Transaction Boundary

- Staff create-confirm, status-confirm, update-confirm, and delete-confirm each
  complete the appointment mutation, audit row, idempotency ledger completion,
  and final commit inside the route-owned transaction.
- Bernie create-confirm also includes its appointment/audit/ledger transaction
  plus its existing session-event double-write replay protection.
- Delete-confirm specifically uses `_apply_appointment_delete(..., commit=False)`
  for the confirm route while raw `DELETE /api/v1/appointments/{appointment_id}`
  keeps the default helper commit behavior.

## Gates Still Closed

This checkpoint does not approve or add:

- proposal-only route idempotency enforcement;
- raw compatibility `PUT`, `PATCH`, or `DELETE` idempotency enforcement;
- slot-search reservation or replay semantics;
- Bernie interpreter/session read-route idempotency expansion;
- provider calls or live provider gates;
- runtime FGA clients;
- external patient clients;
- GraphQL mutations;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- broad historical diary trove mining;
- model-to-database writes outside REST command handlers.

## Next Decision

Recommended Sprint 146: add route-level integration tests that exercise the
common replay/conflict/in-progress/stale/failed-transient behavior across all
five wired confirmation families against a real DB session. After those are
green, choose deliberately between proposal-only idempotency, raw compatibility
write idempotency, or moving to a separate Programme 2G concern. Do not open
proposal-only or raw compatibility enforcement in the checkpoint sprint.
