# plan-claude-claude-waiting-area-checkin-defaults

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-waiting-area-checkin-defaults` |
| Status | integrated |
| Created | 2026-06-22 15:58 +1000 |
| Source HEAD | `d8f3672` |

## Plan Summary

Add GET /checkin-defaults endpoint (DiaryRoster→Room default lookup) and auto-clear waiting_area_id on terminal status in PATCH /status

## My Understanding

Two gaps remain after the checkin-contract task. (1) Defaulting: when a receptionist marks a patient Arrived, the waiting area must still be selected manually — but the practice has a DiaryRoster mapping each practitioner+date to a Room, and each Room has an optional default_waiting_area_id. A GET endpoint can return that suggested area so the UI/Bernie can pre-populate it for confirmation rather than forcing manual selection every time. (2) Clearing: when a patient is Completed/Cancelled/NoShow/DNA they are no longer in any physical waiting area, but waiting_area_id currently persists silently in the row. PATCH /status should auto-clear it on terminal transitions when the caller has not explicitly provided a waiting_area_id in the request body (model_fields_set absent = auto-policy applies; explicit null or UUID always wins).

## Intended Surface / Boundary

Backend only. New GET /api/v1/appointments/{id}/checkin-defaults route in app/routers/appointments.py. New AppointmentCheckinDefaults response schema in app/schemas/appointments.py. Auto-clear logic added to the existing update_appointment_status route (5 lines). New tests/test_waiting_area_checkin_defaults.py. No frontend, no migrations, no models, no seed changes.

## Out Of Scope

docs/diary frontend, taskpane, Command Centre, room/admin UI, Bernie runtime, SMS/voice confirmation, billing/finalisation locking, drag/drop/resize, migrations, AppointmentCreate, queue_position management, seed.py, any non-appointment-status route

## Files I Expect To Edit

app/schemas/appointments.py (add AppointmentCheckinDefaults with suggested_waiting_area_id and room_name fields), app/routers/appointments.py (add TERMINAL_STATUSES constant; add GET checkin-defaults route; add 4-line auto-clear block in update_appointment_status), tests/test_waiting_area_checkin_defaults.py (new: 9 tests)

## Implementation Steps

1. In app/schemas/appointments.py add AppointmentCheckinDefaults(suggested_waiting_area_id: Optional[uuid.UUID]=None, room_name: Optional[str]=None). 2. In app/routers/appointments.py: (a) add import for Room, DiaryRoster; (b) define TERMINAL_STATUSES=(Completed,Cancelled,NoShow,DNA); (c) add GET /{id}/checkin-defaults route: auth=get_current_user, fetch appointment (practice-scoped), query DiaryRoster WHERE practice_id+practitioner_id+roster_date=appointment_date, join Room, check Room.default_waiting_area_id is set and WaitingArea.is_active=True, return AppointmentCheckinDefaults; (d) in update_appointment_status add: if body.status in TERMINAL_STATUSES and waiting_area_id not in body.model_fields_set: appt.waiting_area_id=None. 3. Write tests/test_waiting_area_checkin_defaults.py with 9 tests: auth gate on GET, 404 on wrong-practice appointment, no-roster returns null suggestion, roster+room+default returns UUID, inactive-area returns null, GET does not mutate any state; PATCH to terminal auto-clears area (test Completed and Cancelled), PATCH to active status does not auto-clear, explicit UUID on terminal wins over auto-clear. 4. Run pytest on new file + full previously-verified suite. 5. py_compile + git diff --check.

## Visual / Behavioural Acceptance Checks

9 new tests pass. 111 previously-verified tests still pass. GET /checkin-defaults with no DiaryRoster returns {suggested_waiting_area_id:null,room_name:null}. GET with DiaryRoster+active-default returns the room name and UUID. PATCH /status to Completed/Cancelled/NoShow/DNA auto-clears waiting_area_id when field absent. Explicit waiting_area_id in PATCH always wins. Active-status transitions do not clear area.

## Risks / Ambiguities

1. DiaryRoster import: Room and DiaryRoster are in app/models/diary.py, already partially imported (WaitingArea, DiaryBreak, DiaryColumn, DiaryTemplate are imported). Need to add Room and DiaryRoster to the import. 2. TERMINAL_STATUSES vs NON_BLOCKING_STATUSES: NON_BLOCKING_STATUSES omits Completed (Completed blocks conflict checks). TERMINAL_STATUSES adds it — must not reuse NON_BLOCKING_STATUSES for clearing. 3. Auto-clear on terminal is a policy decision: a receptionist who accidentally marks Completed loses the area assignment. Mitigated by: explicit waiting_area_id in the PATCH always wins, so a corrective PATCH can re-assign. 4. GET /checkin-defaults is read-only and has no side effects, but adds a new auth-gated route — verify require_role vs get_current_user choice (all authenticated users can see the default suggestion; no mutation role required).

## Codex Plan Review

- Review result: Approved and implemented by Claude; integrated as part of Sprint 15.
- Required changes before implementation: none
- Approved to proceed: yes
