# plan-claude-claude-waiting-area-checkin-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-waiting-area-checkin-contract` |
| Status | integrated |
| Created | 2026-06-22 12:57 +1000 |
| Source HEAD | `e551706` |

## Plan Summary

Extend PATCH /status to accept optional waiting_area_id, enabling single-call check-in

## My Understanding

Reception check-in is: mark Arrived AND assign waiting area. PATCH /status currently only accepts status. Adding optional waiting_area_id to AppointmentStatusUpdate lets both happen atomically. model_fields_set distinguishes absent (no change) from null (clear) from UUID (assign). _ensure_waiting_area cross-practice guard already exists.

## Intended Surface / Boundary

Backend only: schemas, router, new test file. No frontend, no new endpoints, no migrations.

## Out Of Scope

diary frontend, taskpane, queue_position, terminal-status auto-clear, AppointmentCreate, Bernie, new models

## Files I Expect To Edit

app/schemas/appointments.py, app/routers/appointments.py, tests/test_waiting_area_checkin_contract.py (new)

## Implementation Steps

1. Add waiting_area_id: Optional[uuid.UUID] = None to AppointmentStatusUpdate in schemas. 2. In update_appointment_status route branch on model_fields_set: UUID value calls _ensure_waiting_area then assigns; None clears; absent does nothing. 3. Write 8 focused tests covering backward compat, assign, clear, cross-practice 404, inactive 404, re-assign, auth gate, no-area-loss. 4. Run pytest on new + existing status/waiting-room tests. 5. py_compile + diff --check.

## Visual / Behavioural Acceptance Checks

8 new tests pass; full 103-test suite passes; no-field-sent preserves area; UUID assigns atomically; null clears; cross-practice/inactive return 404.

## Risks / Ambiguities

1. model_fields_set with FastAPI: verify absent fields are truly absent (same pattern works in AppointmentUpdate). 2. expire_on_commit handled by existing re-fetch. 3. Concurrent writes are out of scope for MVP.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
