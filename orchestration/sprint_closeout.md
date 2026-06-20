# EMR4 Sprint Closeout

This file tracks what the user should review after each integrated sprint batch
of parallel-agent work. Codex updates it after submitted work has been polled,
reviewed, integrated, verified, pushed, and audited.

## Current Closeout

| Item | Value |
|---|---|
| Batch | Sprint 11: Patient-Link Semantics and New Patient Safety |
| Integrated through | `a58e98a` |
| Status | Integrated locally and verified |
| Last updated | 2026-06-20 |

## What Changed

- Added provisional booking support to appointments: `patient_id` is now nullable
  and `patient_name_provisional` stores free-text names for phone/walk-in bookings
  before a patient record is linked.
- Added Alembic migration `e5f6a7b8c9d0_add_provisional_patient_to_appointments.py`.
- Kept the existing linked-patient appointment API backward compatible while
  allowing provisional bookings and later patient linking via appointment update.
- Added focused `tests/test_appointment_patient_link.py` coverage for provisional
  create, missing-identity validation, linked-patient create, patient-link update,
  cross-practice protection, status changes on provisional bookings, and the
  integration guard that prevents clearing all patient identity from an appointment.
- Updated the diary UI to distinguish linked patient records from provisional
  names, tolerate `patient: null`, and treat legacy `Confirmed` status as booked
  for attendance display rather than as a routine status option.
- Removed the submitted SMS/phone confirmation checkbox during integration because
  it conflicted with the project decision that patient-record linkage and future
  reminder/SMS confirmation are separate concepts.
- Updated diary assets to `v=56`.
- Hardened the New Patient taskpane flow: duplicate candidates are checked before
  `/patients/with-file`, possible duplicates show a warning list, and users can
  review details, create anyway, cancel, escape, close, or create another after
  success.
- Updated taskpane assets to `v=38` and synced `docs/taskpane/*`.

## Recommended User Review

1. After pulling the new code locally, run migrations and restart the backend:
   `alembic upgrade head`, then `python seed.py` if seed data is stale.
2. Open the live diary and confirm existing linked-patient bookings still render,
   open, edit, save, and change attendance status.
3. Create a booking by typing a name that is not in patient search and choosing
   the provisional booking option. Confirm it saves and displays as provisional
   rather than crashing because `patient` is null.
4. Edit that provisional booking and confirm its name, reason, time, duration,
   and status remain stable.
5. Search/select an existing patient in the booking modal and confirm linked
   bookings still show as linked records, visually distinct from provisional
   bookings.
6. Confirm the status dropdown no longer offers `Confirmed` as a normal attendance
   status for new bookings.
7. In the taskpane New Patient form, create a clearly non-duplicate patient and
   confirm success gives usable `Close` and `Create Another` actions.
8. Try creating a likely duplicate patient and confirm the warning list appears
   before creation, with `Review Details`, `Create Anyway`, cancel, close, and
   Escape paths all behaving sensibly.
9. Confirm the New Patient form no longer traps you over the taskpane after close,
   cancel, success, or Escape.

## Not Required Before Moving On

- No drag/drop/resize testing is required yet.
- No Command Centre, Scribe, Gemini, billing, results, letters, or medication
  review is required for this sprint.
- No live SMS/reminder confirmation review is required; that is intentionally not
  implemented and should remain separate from patient-record linkage.
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

- Sprint 11 verification:
  - `node --check docs\diary\diary.js` -> passed
  - `node --check "EMR4 Sidebar\src\taskpane\taskpane.js"` and
    `node --check docs\taskpane\taskpane.js` -> passed
  - `.venv\Scripts\python.exe -m py_compile app\routers\appointments.py app\schemas\appointments.py app\models\appointments.py`
    -> passed
  - `.venv\Scripts\python.exe -m alembic upgrade head` and
    `.venv\Scripts\python.exe -m alembic current` -> current at
    `e5f6a7b8c9d0`
  - `git diff --check` -> passed
  - After resetting stale `gp_pms_test` public schema:
    `.venv\Scripts\python.exe -m pytest tests\test_appointment_patient_link.py -q`
    -> 9 passed
  - After per-file schema resets:
    `tests\test_patients.py` -> 14 passed;
    `tests\test_booking_create_edit.py` -> 31 passed;
    `tests\test_nurse_practitioner.py` -> 6 passed;
    `tests\test_appointment_status_mutations.py` -> 23 passed;
    `tests\test_waiting_room.py` -> 18 passed
  - A larger combined focused pytest bundle timed out or hit the known stale
    PostgreSQL enum state; this remains a test-infrastructure issue rather than
    an observed product assertion failure.

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

Sprint 12 should finish the practical patient-link workflow: link a provisional
diary booking to an existing/new patient record from the booking modal, keep
booking-over-break warning on the near-term list, and continue refining
waiting-area semantics. Drag/drop/resize should remain deferred until
bookable-resource and patient-flow rules are stable enough that we are not
smoothing over the wrong rules.
