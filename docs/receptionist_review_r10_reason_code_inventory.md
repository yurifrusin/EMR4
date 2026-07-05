# Sprint R10 — Reason-Code Surface Inventory

This inventory records the current cancellation/status reason-capture surface
before a typed reason-code contract is implemented.

## Data Model

| Surface | Current field | Behaviour |
|---|---|---|
| `Appointment` | `cancellation_reason: String(500), nullable` | Free text only; no enum, code, or constraint. |
| `AppointmentAuditLog` | `cancellation_reason: String(500), nullable` | Copies delete reason into audit entries. |
| `AppointmentAuditAction` | `create`, `update`, `status_change`, `delete` | Captures action type, not reason taxonomy. |

There is no current `reason_code`, `status_reason_code`, or reason reference
table.

## Schema Surface

| Schema | Current reason support |
|---|---|
| `AppointmentOut` | Exposes `cancellation_reason`. |
| `AppointmentDeleteIn` | Accepts optional free-text `cancellation_reason`. |
| `AppointmentDeleteCommand` | Carries optional free-text `cancellation_reason`. |
| `AppointmentAuditLogOut` | Exposes audit `cancellation_reason`. |
| `AppointmentStatusUpdate` | No reason field. |
| `AppointmentStatusProposalIn` | No reason field. |
| `AppointmentStatusCommand` | No reason field. |

Key gap: status mutations to `Cancelled`, `NoShow`, or `DNA` cannot currently
carry a reason through either raw status updates or status proposal-confirm
flows.

## Endpoint Surface

| Endpoint | Reason capture today |
|---|---|
| `DELETE /api/v1/appointments/{id}` | Optional free-text reason. |
| `POST /api/v1/appointments/proposals/delete/{id}` | Optional free-text reason in command payload. |
| `POST /api/v1/appointments/proposals/delete-confirm` | Applies free-text reason from signed payload. |
| `PATCH /api/v1/appointments/{id}/status` | No reason field. |
| `POST /api/v1/appointments/proposals/status/{id}` | No reason field. |
| `POST /api/v1/appointments/proposals/status-confirm` | No reason field. |

## Audit Evidence Surface

Existing `confirmed_warnings` values describe provenance and safeguards, such
as raw-route compatibility, proposal confirmation, signed evidence, stale
freshness IDs, waiting-area clearing, past appointment checks, and same-day
window checks.

Those values answer how a mutation was authorised. They do not answer why a
patient, practitioner, clinic, or receptionist cancelled or changed the
appointment status.

## Test Coverage

Current tests verify that:

- delete routes preserve free-text `cancellation_reason`
- delete-confirm routes preserve signed free-text cancellation reason
- audit output exposes `cancellation_reason`
- overlong cancellation reasons are rejected
- `confirmed_warnings` remains a code-like provenance list

Current tests do not enforce:

- a reason-code allow-list
- invalid-code rejection
- reason-code audit persistence
- status-route reason capture
- migration compatibility for legacy rows

## Minimum Future Contract

The smallest low-risk reason-code contract is:

1. Add a nullable `status_reason_code` field to appointment/status/delete
   command schemas and read schemas.
2. Persist the code on both `Appointment` and `AppointmentAuditLog`.
3. Validate supplied codes with one shared backend allow-list.
4. Keep `cancellation_reason` as optional free text.
5. Return 422 for unknown supplied codes, while accepting null for legacy
   compatibility during the transition.
6. Keep temporal slot-write policy unchanged.

The code should remain application-level first. A database enum, check
constraint, or reference table should wait until the taxonomy has been tested
against receptionist workflow.
