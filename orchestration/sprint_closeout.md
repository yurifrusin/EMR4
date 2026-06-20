# EMR4 Sprint Closeout

This file tracks what the user should review after each integrated sprint batch
of parallel-agent work. Codex updates it after submitted work has been polled,
reviewed, integrated, verified, pushed, and audited.

## Current Closeout

| Item | Value |
|---|---|
| Batch | Sprint 10: Nurse Bookability and Patient Identity Foundation |
| Integrated through | `0b94c23` |
| Status | Integrated locally and verified |
| Last updated | 2026-06-20 |

## What Changed

- Made Room 2/Nurse practitioner-backed in dev data by adding Nurse Sarah Chen
  with AHPRA `NMW0001234567`, weekday schedules, Room 2 template/roster wiring,
  and a sample nurse appointment.
- Added focused nurse practitioner tests for diary template/roster wiring,
  nurse appointment creation/conflict behaviour, and nurse slot availability.
- Removed a redundant appointment-create `db.refresh(appt)` round trip before the
  existing fresh appointment reload.
- Updated the diary frontend so practitioner-backed columns remain bookable,
  while label-only/non-practitioner columns get a restrained non-bookable visual
  treatment and no empty chevrons.
- Added backend patient identity foundations: `medicare_irn`, IHI search/index
  support, and `GET /api/v1/patients/duplicate-candidates` for warning-only
  duplicate-patient checks.
- Added patient tests for Medicare IRN validation, IHI/IRN search, duplicate
  candidate matching, practice scoping, and formatted identifier normalisation.
- Updated diary assets to `v=55`.

Historical Sprint 9 changes:

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
- User-review hotfix 4: bookable free-space hover now shows a custom 5-minute
  start-time preview chip and faint line before the booking modal opens, with
  gentle snapping near visible gridlines.

## Recommended User Review

1. After pulling the new code locally, run migrations and seed data if your dev
   DB is not already current: `alembic upgrade head`, then `python seed.py`, then
   restart the backend.
2. Open the live diary from the taskpane and confirm Room 2 shows Nurse Sarah
   Chen or an equivalent nurse-backed label, not a purely label-only Nurse.
3. Click an empty Room 2/Nurse slot and confirm the booking modal opens with the
   nurse-backed room selected; save a test nurse appointment and confirm it
   appears in Room 2.
4. Confirm Room 3 remains visually non-bookable and does not show empty chevrons
   or silently open an invalid booking modal.
5. Confirm Room 1 booking create/edit/status behaviour still works, including a
   quick 5-minute booking and the waiting-room status actions.
6. Optional API check: call `/api/v1/patients/duplicate-candidates` with an
   existing patient's DOB plus formatted Medicare or phone values and confirm it
   returns warning candidates without blocking patient creation.
7. Narrow the diary window and confirm the non-bookable Room 3 treatment and
   nurse booking affordances stay readable without crowding the header or cards.

## Not Required Before Moving On

- Drag/drop and resize are still intentionally out of scope.
- Roster admin UI is not built yet.
- Online booking portal behaviour is not applicable yet.
- A separate wallboard-style waiting-room display app is not built yet.
- Room/resource-only bookings are still intentionally deferred; booking creation
  still requires a practitioner-backed column.
- No state-machine guard exists yet; any valid status can currently be corrected
  to any other valid status by mutating staff roles.
- The duplicate-candidate API is backend-only for now; no taskpane patient-entry
  duplicate warning is required before the next sprint.
- Real IHI/Medicare verification is not implemented yet.

## Known Follow-Up

- The `pytest_asyncio` loop-scope deprecation warning remains and should be
  addressed before it becomes a default-behaviour change.
- The PostgreSQL test DB can retain enum types after interrupted or parallel
  pytest runs. Do not run two pytest processes against `gp_pms_test` in parallel.
- Dirty stale disposable worktree `codex/time-model` remains visible and should be
  reviewed before retirement.
- Practitioner mapping in the diary modal depends on AHPRA-to-ID data discoverable
  from roster or appointments. Non-practitioner/label-only rooms should not be
  treated as fully bookable yet.
- User-review hotfix: the booking save button is wired directly again after the
  modal footer moved outside the form, Enter-to-save is preserved inside the
  booking form, and broad free-session booking targets now calculate the clicked
  5-minute time rather than always using the start of the free block.
- Waiting-room design follow-up: model physical waiting areas explicitly rather
  than as one flat list. Rooms should be able to point to a default waiting
  area, and the diary patient-flow panel can later expose area tabs or auto-focus
  the area associated with the active room/column.
- Waiting-room interaction follow-up: when clicking a patient-flow card expands
  and highlights the corresponding diary booking, auto-collapse the booking after
  a short idle period, approximately 3 seconds, unless the user starts interacting
  with that booking. Preserve this selection/expansion state as local-only UI
  behaviour if live multi-user diary updates are added later.
- Patient-record follow-up: New Patient creation is only the first slice. Add an
  edit-patient-details workflow, duplicate-patient detection before file/record
  creation, Medicare card reference number, IHI number, and a fuller demographic
  and identifier model before relying on patient creation in routine use.
- New Patient workflow follow-up: make the form a proper modal workflow with
  cancel/escape, validation, duplicate warning, successful file creation, and clear
  open-file guidance. Design it to share a patient-details model with later printed
  forms, waiting-area tablet entry, and patient mobile/PWA self-entry. AI-assisted
  OCR for paper forms is a later optional intake helper, not the canonical record.
- Booking-over-break policy follow-up: keep appointments allowed to overlap
  break blocks, because breaks are soft operational blocks rather than absolute
  booking constraints, but warn the user before saving when a booking crosses a
  room/practitioner break. Starting a new booking inside a break can remain
  blocked/not offered for now.
- Appointment-state model follow-up: split patient identity/linkage confirmation
  from appointment attendance workflow. The old EMR "confirmed" concept meant the
  diary name was confirmed/linked to a patient record, not that the patient had
  replied to a reminder or reached an attendance stage. Future booking flow should
  allow provisional free-text patient-name bookings, then a later confirm/link
  patient step before Arrived/InConsult/Completed.
- Appointment attendance follow-up: allow staff correction/backtracking between
  most attendance statuses, but design guards carefully around completion and
  future billing so accidental double-billing is not enabled.
- Add taskpane New Patient/Edit Patient fields for Medicare IRN and IHI, then
  surface duplicate candidates as a warning/confirm step rather than a hard
  block.
- Revisit room/resource modelling so future rooms can be linked to physical
  waiting areas and non-practitioner resources without pretending every bookable
  resource is a login-capable GP.
- Waiting-room panel follow-up: appointment cards can be stacked/condensed,
  especially in high-volume sections such as Finished.
- Taskpane/Command Centre follow-up: preserve the tabbed taskpane as a real
  patient summary/navigation surface and continue observing its usability in the
  constrained Word pane. Grow Command Centre gradually as the larger work surface
  for workflows that prove they need space, microphone access, review panes, or
  sustained focus; do not add Command Centre tabs before the workflow boundary is
  clear.

## Verification

These are Codex/orchestrator verification notes, not commands the user is expected
to run.

- Sprint 10 verification:
  - `node --check docs\diary\diary.js` -> passed
  - `git diff --check` -> passed
  - `.venv\Scripts\python.exe -m pytest tests\test_nurse_practitioner.py -q`
    -> 6 passed
  - `.venv\Scripts\python.exe -m pytest tests\test_patients.py -q`
    -> 14 passed after resetting stale `gp_pms_test` enum state
  - `.venv\Scripts\python.exe -m pytest tests\test_nurse_practitioner.py tests\test_diary_template.py tests\test_diary_roster.py tests\test_booking_create_edit.py tests\test_slots.py tests\test_patients.py -q`
    -> 75 passed
  - `.venv\Scripts\python.exe -m alembic upgrade head` and
    `.venv\Scripts\python.exe -m alembic current` -> current at
    `d4e5f6a7b8c9`
  - `.venv\Scripts\python.exe seed.py` -> created Nurse Sarah Chen locally and
    backfilled Room 2 to the nurse practitioner in the dev DB

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
- Booking modal/gap-target hotfix verification: `node --check docs\diary\diary.js`
  and `git diff --check` -> passed
- Booking hover-preview hotfix verification: `node --check docs\diary\diary.js`
  and `git diff --check` -> passed
- New Patient modal escape hotfix verification: `node --check "EMR4 Sidebar\src\taskpane\taskpane.js"`,
  `node --check docs\taskpane\taskpane.js`, and `git diff --check` -> passed
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

Sprint 11 should make the booking workflow safer around operational exceptions:
warn before saving a booking across a break, continue to refine waiting-area
semantics, and start splitting patient identity confirmation from appointment
attendance workflow. Drag/drop/resize should remain deferred until bookable
resources and patient-flow semantics are settled enough that we are not smoothing
over the wrong rules.
