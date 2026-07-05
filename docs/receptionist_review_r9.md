# Receptionist-Domain Governance Review: Sprint R9 Status/Delete Retrospective Policy

Sprint R9 reviews the operations that Sprint R8 intentionally left outside temporal slot-write blocking: appointment status changes and delete/cancellation confirmations. These actions do not allocate a new diary slot or reschedule practitioner time, so they must remain available for retrospective administration, while relying on non-temporal governance controls.

## Policy Boundary

| Operation | Retrospective use case | Temporal block? | Governance requirement |
|---|---|---|---|
| Mark `Arrived` / `InConsult` | Staff records a real event after it happened | No | Authenticated actor and audit trail |
| Mark `Completed` | GP/admin finalises a consultation after slot end | No | Signed confirmation path preferred; audit required |
| Mark `NoShow` / `DNA` | End-of-session or next-day attendance cleanup | No | Clear state transition and audit |
| Cancel/delete appointment | Patient cancellation, duplicate booking, admin correction | No | Cancellation reason and audit evidence |

Blocking these actions because an appointment is in the past would corrupt clinic operations: staff could not clean up waiting-room state, record no-shows, correct duplicated bookings, or finalise billing-adjacent attendance state.

## Recommended Governance

- Keep temporal guards limited to slot-writing create/update/reschedule paths.
- Prefer proposal-confirm routes for status/delete changes because they carry freshness IDs, signed confirmation evidence, warning/block context, and bounded audit evidence.
- Treat legacy raw `PATCH /appointments/{id}/status` and `DELETE /appointments/{id}` as compatibility paths; keep tests proving their behaviour, but avoid expanding new UX onto them.
- Preserve immutable audit records with actor identity, role, timestamp, status before/after, cancellation reason where present, and evidence codes.
- Consider a future schema-backed cancellation reason catalog before enforcing mandatory reason codes, so Australian GP workflows can distinguish patient cancellation, provider cancellation, DNA/no-show, rescheduled, duplicate booking, and admin error.

## Staff Copy

- Historical status update: "You are updating the status of a past appointment. This will not create or move a diary slot, but the change is permanently audited."
- Historical cancellation: "You are cancelling a past appointment. Add a clear reason; the cancellation will be permanently audited."
- Terminal-state change: "This appointment is already finalised. Continue only if this is a deliberate administrative correction."

## Test Focus

Regression tests should prove both halves of the boundary: past-date and elapsed same-day status/delete operations remain permitted, while stale freshness IDs, tampered signed evidence, and missing explicit confirmation still fail closed without writes.
