# EMR4 Sprint Closeout

This file tracks what the user should review after each integrated sprint batch
of parallel-agent work. Codex updates it after submitted work has been polled,
reviewed, integrated, verified, pushed, and audited.

## Current Closeout

| Item | Value |
|---|---|
| Batch | Sprint 8: Booking Create/Edit First Slice |
| Integrated through | `14bc9e4` on `master` / `handoff/current` |
| Status | User review passed |
| Last updated | 2026-06-19 |

## What Changed

- Added `tests/test_booking_create_edit.py` with 31 backend tests covering
  booking create/edit auth, role/scope gates, local time pair handling,
  UTC fallback, response shape, conflict behavior, adjacent bookings,
  non-blocking terminal statuses, duration changes, practitioner changes,
  and appointment type updates.
- Added a diary create/edit modal for practical staff booking work:
  click an empty slot to create, open an appointment and use Edit to modify.
- The modal supports patient search, practitioner/room selection where a
  practitioner ID is known, appointment type, date, time, duration, status,
  and reason.
- Existing status controls remain separate and available on expanded cards.
- The former "delete" action is represented as cancellation because the current
  backend `DELETE` route status-cancels an appointment rather than hard-deleting
  it.
- User-review hotfix: normal 15-minute appointment reasons now render in cards,
  off-grid/free 5-minute gaps are clickable, appointment conflict errors are
  human-readable, and cancellation now uses an explicit in-modal confirmation.
- User-review hotfix 2: sub-grid bookings now render at their actual duration
  instead of visually expanding to the full 15-minute grid interval.
- User-review hotfix 3: cancelled appointments are hidden from the working
  diary layer and visible appointment count, while DNA/no-show remain visible
  as greyed attendance outcomes.
- Diary asset cache-bust moved to `v=48`.
- Added `orchestration/booking_create_edit_review.md` for the Sprint 8 API/UI
  review path, including exact PowerShell snippets.

## Recommended User Review

User review result: passed.

1. Open the live diary from the taskpane and create one booking from an empty
   slot in a practitioner-backed room. **Passed.**
2. Confirm patient search works, the created card appears in the correct
   date/room/time/duration position, and the grid refreshes after save.
   **Passed.**
3. Edit the same booking's time, duration, reason, appointment type, and status;
   confirm changes appear only after a successful save. **Passed.**
4. Try an overlapping booking and confirm the UI shows a readable conflict
   without silently changing the grid. **Passed after hotfix.**
5. Use Cancel Booking on the test appointment and confirm it becomes visually
   terminal/non-active rather than disappearing as a hard delete. **Policy
   adjusted: cancelled appointments are hidden from the working layer.**
6. Create a 5-minute booking in a visible free gap between two existing
   appointments and confirm unusual start/end times show via the hover edge
   labels. **Passed after hotfix.**
7. Narrow the diary window and confirm the create/edit modal and expanded card
   controls remain usable without crowding patient names, notes, status controls,
   breaks, Refresh, Now, or date navigation. **Passed.**
8. Optionally run the PowerShell API snippets in
   `orchestration/booking_create_edit_review.md` for direct API confirmation.

## Not Required Before Moving On

- Drag/drop and resize are still intentionally out of scope.
- Roster admin UI is not built yet.
- Online booking portal behaviour is not applicable yet.
- A full live waiting-room display app is not built yet.
- No state-machine guard exists yet; any valid status can currently be corrected
  to any other valid status by mutating staff roles.

## Known Follow-Up

- The `pytest_asyncio` loop-scope deprecation warning remains and should be
  addressed before it becomes a default-behaviour change.
- The PostgreSQL test DB can retain enum types after interrupted/parallel pytest
  runs. Resetting the public schema fixed the issue during integration; avoid
  running two pytest processes against the same `gp_pms_test` database in parallel.
- Dirty stale disposable worktree `codex/time-model` remains visible and should be
  reviewed before retirement.
- `AppointmentUpdate` now supports appointment type updates, but partial date-only
  or time-only update requests remain router-tolerant rather than schema-rejected.
- Practitioner mapping in the diary modal depends on AHPRA-to-ID data discoverable
  from roster or appointments. Non-practitioner/label-only rooms should not be
  treated as fully bookable yet.

## Verification

These are Codex/orchestrator verification notes, not commands the user is expected
to run.

- `node --check docs\diary\diary.js` -> passed
- `git diff --check` -> passed
- `.venv\Scripts\python.exe -m pytest tests/test_booking_create_edit.py -q` -> 31 passed
- `.venv\Scripts\python.exe -m pytest tests/test_appointment_conflicts.py tests/test_appointment_status_mutations.py tests/test_waiting_room.py tests/test_slots.py -q` -> 54 passed
- `.venv\Scripts\python.exe -m pytest tests/test_diary_roster.py -q` -> 11 passed

Historical Sprint 7 verification:

- `node --check docs\diary\diary.js` -> passed
- `git diff --check` -> passed
- `.venv\Scripts\python.exe -m pytest tests\test_appointment_status_mutations.py -q` -> 23 passed
- `.venv\Scripts\python.exe -m pytest tests\test_waiting_room.py tests\test_appointment_conflicts.py tests\test_slots.py -q` -> 31 passed after resetting stale test schema
- `.venv\Scripts\python.exe -m pytest tests\test_appointment_status_mutations.py tests\test_waiting_room.py tests\test_appointment_conflicts.py tests\test_slots.py -q` -> 54 passed sequentially
- `.venv\Scripts\python.exe -m pytest tests\test_diary_roster.py -q` -> 11 passed

## Recommended Next Direction

Sprint 8 user review passed. Sprint 9 has been dispatched to harden the next
operational layer before drag/drop/resize:

- backend appointment patient-flow/status contract work
- diary patient-flow/waiting-room UI refinement
- DB-backed patient search and New Patient creation reliability

Drag/drop/resize should still wait until the patient-flow and patient-entry
paths are tested and feel dependable.
