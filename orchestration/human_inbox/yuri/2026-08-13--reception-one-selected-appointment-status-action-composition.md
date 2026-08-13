# Reception One selected-appointment status action

Date: 2026-08-13

Timestamp: 2026-08-13T22:46:00+10:00 (Australia/Brisbane)

Attention required: no

## Lay summary

Reception One can now change the status of one selected current appointment
without sending the receptionist back to the full Diary. For example, the
staff member can select an appointment, choose an existing status such as
Arrived, review the change through the same safety interaction already used by
the Diary, and see the focused view refresh from current truth.

This does not give Reception One a new or separate power. It reuses the one
secured status-changing route that already existed. If the action is cancelled,
blocked, stale, fails, or is interrupted, Reception One does not pretend that
it succeeded. If the appointment has changed or moved out of the focused view,
the old selection and Back history are cleared rather than being reused.

The interaction was inspected at desktop, tablet and phone sizes, including
keyboard focus and Escape cancellation. One duplicated patient-timeline
heading found during inspection was fixed and retested.

## Technical summary

Accepted source is `b6c6a983c4936c1f0bd5e9daf03924bbcd4ddd33`.
The meta-grid bridge resolves the exact current appointment and delegates only
to the existing `setAppointmentStatus` proposal/confirm interaction. It has no
network or command implementation of its own. GraphQL stays read-only; no
FastAPI, OpenAPI, database, event-runtime or generated-client surface changed.

The route-intercepted browser acceptance passes 8 cases, the full native Diary
browser suite passes 144 cases, the focused packet passes 171 tests and the
canonical fast profile passes all 193 of its tests. The evidence record is
schema-valid and source-bound. No provider, patient/product data, database,
deployment, release, Pages or protected ref was touched.

## Next

I will now perform a fresh read-only programme orientation. Its job is to find
the narrowest next useful tranche already supported by the repository after
this visible milestone. Anything that still requires your decision—such as a
new command or event family, representative participant sessions or the first
patient channel—will remain closed rather than being silently assumed.
