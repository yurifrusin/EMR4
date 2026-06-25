# plan-claude-claude-appointment-cancellation-reason-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-appointment-cancellation-reason-contract` |
| Status | integrated |
| Created | 2026-06-25 12:32 +1000 |
| Source HEAD | `7c9c7f5` |

## Plan Summary

Add cancellation_reason column + optional body to DELETE and proposals/delete endpoints; echo through proposal command payload; 4 focused tests

## My Understanding

Appointment model has reason (booking reason) and notes (booking notes) but no cancellation-specific field. DELETE and POST /proposals/delete take no body. Task: add optional cancellation_reason that flows through proposal command payload and persists on the row, without touching safety semantics. PATCH /status is a separate path, out of scope.

## Intended Surface / Boundary

Backend only: models, migration, schemas, router, test file. No frontend.

## Out Of Scope

Diary frontend, taskpane, Command Centre, PATCH /status reason capture, audit log, billing, any non-cancel endpoints

## Files I Expect To Edit

app/models/appointments.py; alembic/versions new migration; app/schemas/appointments.py; app/routers/appointments.py; tests/test_appointment_status_mutations.py

## Implementation Steps

1. Add cancellation_reason=Column(String(500),nullable=True) to Appointment model. 2. alembic revision --autogenerate -m add_cancellation_reason_to_appointments; verify ADD COLUMN only. 3. Add AppointmentDeleteIn with cancellation_reason Optional[str] max_length=500; add field to AppointmentDeleteCommand and AppointmentOut. 4. cancel_appointment (DELETE) accepts optional AppointmentDeleteIn body; writes reason to row. 5. propose_delete_appointment (POST /proposals/delete) same body; echoes reason in command. 6. Add 4 tests: reason persists on delete, no-body -> null, proposal echoes reason in command, too-long reason -> 422.

## Visual / Behavioural Acceptance Checks

DELETE with reason -> 204, db shows cancellation_reason persisted. DELETE with no body -> 204, reason null. POST proposals/delete with reason -> command.cancellation_reason echoed, row unchanged. Reason >500 chars -> 422. All 30 existing tests still pass.

## Risks / Ambiguities

HTTP DELETE with body is RFC-legal but some proxies strip it; FastAPI handles it correctly. PATCH /status to Cancelled bypasses this field by design. Migration is additive nullable column; zero data risk.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
