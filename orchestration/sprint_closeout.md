# EMR4 Sprint Closeout

This file tracks what the user should review after each integrated sprint batch
of parallel-agent work. Codex updates it after submitted work has been polled,
reviewed, integrated, verified, pushed, and audited.

## Current Closeout

| Item | Value |
|---|---|
| Batch | Sprint 9: Patient Flow and Patient Entry Hardening |
| Integrated through | current Sprint 9 closeout tip on `master` / `handoff/current` |
| Status | Integrated locally, pending user review |
| Last updated | 2026-06-20 |

## What Changed

- Added backend patient-flow contract coverage in
  `tests/test_booking_patient_flow.py`: partial date/time update validation,
  Cancelled recoverability, DNA/NoShow visibility/non-blocking behaviour,
  appointment type updates, status filtering, queue position updates, and
  waiting-room ordering.
- Hardened appointment mutating routes by caching `practice_id` and `booked_by`
  before commits, avoiding expired ORM access after SQLAlchemy commits.
- Added a diary patient-flow workbench sidebar with Waiting Room, In Consult,
  Expected Today, and Finished sections, plus quick actions such as Check In,
  Start Consult, and Complete.
- Updated diary assets to `v=49`.
- Added focused patient API coverage in `tests/test_patients.py` for patient
  creation, DB-backed search by name/Medicare/phone, practice scoping, and
  `/patients/with-file`.
- Changed `/patients/with-file` so new generated-file patients always start
  with `document_url = null`; the Word/taskpane auto-detect flow can backfill
  the document URL later.
- Integration cleanup: removed trailing whitespace from the diary workbench
  submit before final verification.
- User-review hotfix: moved the diary footer inside the scrollable grid
  container so it no longer competes with the grid as a horizontal flex item,
  and tightened the Waiting Room count display.
- User-review hotfix 2: exposed `practitioner_id` through the diary template
  API and preserved it in the diary frontend, so Dr Shera's column remains
  bookable even on days with zero existing appointments.
- User-review hotfix 3: template columns now resolve missing practitioner IDs
  from matching AHPRA numbers at response time, covering older DB rows where
  `diary_columns.practitioner_id` is null. The booking form now submits on
  Enter via the normal form submit path.

## Recommended User Review

1. Open the live diary from the taskpane and confirm the new Waiting Room button
   opens/closes a right-side patient-flow panel.
2. Change an appointment through Booked/Confirmed -> Arrived and confirm it
   appears in the Waiting Room section and the header count updates.
3. From the panel, use Start Consult and Complete on a test appointment; confirm
   the main diary card updates and the appointment moves between panel sections.
4. Confirm Cancelled appointments stay hidden from the working diary layer, while
   DNA/NoShow remain visible as greyed attendance outcomes.
5. Confirm create/edit booking still works, including 5-minute bookings and
   human-readable conflict errors.
6. Narrow the diary window and confirm the patient-flow panel behaves as an
   overlay without making booking cards, the date controls, Refresh, or Now
   unusable.
7. Create a New Patient from the taskpane and confirm patient search can find the
   patient by name and phone/Medicare-style identifiers. The generated file
   should still open through the normal Word/taskpane flow.

## Not Required Before Moving On

- Drag/drop and resize are still intentionally out of scope.
- Roster admin UI is not built yet.
- Online booking portal behaviour is not applicable yet.
- A separate wallboard-style waiting-room display app is not built yet.
- Nurse/Room 2 remains label-only unless a real practitioner/staff resource is
  rostered there; booking creation still requires a practitioner-backed column.
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
- The `pytest_asyncio` loop-scope deprecation warning remains and should be
  addressed before it becomes a default-behaviour change.
- The PostgreSQL test DB can retain enum types after interrupted or parallel
  pytest runs. Do not run two pytest processes against `gp_pms_test` in parallel.
- Dirty stale disposable worktree `codex/time-model` remains visible and should be
  reviewed before retirement.
- Practitioner mapping in the diary modal depends on AHPRA-to-ID data discoverable
  from roster or appointments. Non-practitioner/label-only rooms should not be
  treated as fully bookable yet.

## Verification

These are Codex/orchestrator verification notes, not commands the user is expected
to run.

- `node --check docs\diary\diary.js` -> passed
- `git diff --check` -> passed after integration whitespace cleanup
- Hotfix verification: `node --check docs\diary\diary.js` and
  `git diff --check` -> passed
- Practitioner-ID hotfix verification: `node --check docs\diary\diary.js`,
  `git diff --check`, and
  `.venv\Scripts\python.exe -m pytest tests\test_diary_template.py tests\test_diary_roster.py -q`
  -> 18 passed
- Practitioner-ID resolver hotfix verification: `node --check docs\diary\diary.js`,
  `git diff --check`, and
  `.venv\Scripts\python.exe -m pytest tests\test_diary_template.py tests\test_diary_roster.py -q`
  -> 19 passed
- `.venv\Scripts\python.exe -m pytest tests\test_patients.py -q` -> 8 passed
- `.venv\Scripts\python.exe -m pytest tests\test_booking_patient_flow.py -q` -> 20 passed
- `.venv\Scripts\python.exe -m pytest tests\test_booking_create_edit.py tests\test_booking_patient_flow.py tests\test_appointment_conflicts.py tests\test_appointment_status_mutations.py tests\test_waiting_room.py tests\test_slots.py tests\test_patients.py -q` -> 113 passed

Historical Sprint 7 verification:

- `node --check docs\diary\diary.js` -> passed
- `git diff --check` -> passed
- `.venv\Scripts\python.exe -m pytest tests\test_appointment_status_mutations.py -q` -> 23 passed
- `.venv\Scripts\python.exe -m pytest tests\test_waiting_room.py tests\test_appointment_conflicts.py tests\test_slots.py -q` -> 31 passed after resetting stale test schema
- `.venv\Scripts\python.exe -m pytest tests\test_appointment_status_mutations.py tests\test_waiting_room.py tests\test_appointment_conflicts.py tests\test_slots.py -q` -> 54 passed sequentially
- `.venv\Scripts\python.exe -m pytest tests\test_diary_roster.py -q` -> 11 passed

## Recommended Next Direction

After user review, Codex recommends deciding how Room 2/Nurse should become
bookable: either seed a real nurse/staff practitioner resource for the room, or
design room/resource-only bookings. The first path is smaller and probably right
for the next sprint. Drag/drop/resize should still wait until practitioner versus
resource booking semantics are clear.
