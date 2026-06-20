# EMR4 Sprint Closeout

This file tracks what the user should review after each integrated sprint batch
of parallel-agent work. Codex updates it after submitted work has been polled,
reviewed, integrated, verified, pushed, and audited.

## Current Closeout

| Item | Value |
|---|---|
| Batch | Sprint 12: Provisional Booking Link and State Model |
| Integrated through | this closeout commit |
| Status | Integrated locally and verified |
| Last updated | 2026-06-21 |

## What Changed

- Added a warning-only backend contract for appointments that cross configured
  break blocks: create/update responses now include `breaks_overlap` without
  blocking the booking.
- Added focused `tests/test_break_overlap_contract.py` coverage for create,
  update, outside-break, and no-template cases.
- Updated the diary booking modal so provisional/free-text bookings can be linked
  to an existing patient record without losing time, duration, status, or reason.
- Added a diary-side warning before saving a booking that crosses Morning Tea,
  Lunch, or another configured break block.
- Preserved the project distinction between linked patient identity, provisional
  diary identity, attendance status, and future SMS/reminder confirmation.
- Added `orchestration/appointment_state_waiting_area_review.md` as the Sprint 12
  design and API-review harness for identity/status/waiting-area semantics.
- Updated diary assets to `v=59`.

## Recommended User Review

1. Hard refresh the live diary and confirm it loads `diary.js?v=59`.
2. Create a provisional/free-text booking and confirm it saves and remains
   visually provisional.
3. Edit that provisional booking, search for an existing patient, select/link the
   patient, and confirm the same booking keeps its time, duration, status, and
   reason while becoming linked.
4. Create or edit a booking so its end time crosses Morning Tea or Lunch. Confirm
   the warning appears, cancelling keeps the modal open, and proceeding saves.
5. Confirm existing linked-patient bookings can still be edited and status-changed.
6. Try the identity-warning/status path for provisional patients again: the
   patient should not quietly progress into attendance states without warning.
7. Optional API review: use the snippets in
   `orchestration/appointment_state_waiting_area_review.md` to inspect
   provisional create, link, status mutation, and waiting-room inclusion.

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
- Break-overlap follow-up: `breaks_overlap` is populated on create/update
  responses, not on appointment list/detail GET responses. Add passive GET
  annotation later only if an API client needs it.
- Diary warning follow-up: the current break-crossing warning is intentionally
  soft. Starting inside a break remains discouraged by the diary surface, while
  ending over a break is allowed after warning.
- Sprint 12 review harness follow-up: continue using
  `orchestration/appointment_state_waiting_area_review.md` as the source for
  separating patient identity linkage, attendance state, future SMS confirmation,
  and physical waiting-area assignment.
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
- Browser-window follow-up: the taskpane can now avoid building up multiple diary
  windows by closing/reopening the existing dialog, but Office still shows its
  own window-open prompt each time.

## Verification

These are Codex/orchestrator verification notes, not commands the user is expected
to run.

- Sprint 12 verification:
  - `node --check docs\diary\diary.js` -> passed
  - `.venv\Scripts\python.exe -m py_compile app\routers\appointments.py app\schemas\appointments.py`
    -> passed
  - `git diff --check origin/master..HEAD` -> passed
  - After resetting `gp_pms_test` public schema and ensuring `vector` extension:
    `.venv\Scripts\python.exe -m pytest tests\test_break_overlap_contract.py -q -vv`
    -> 4 passed
  - `.venv\Scripts\python.exe -m pytest tests\test_appointment_patient_link.py tests\test_appointment_conflicts.py tests\test_appointment_status_mutations.py -q`
    -> 40 passed
  - `.venv\Scripts\python.exe -m pytest tests\test_diary_template.py tests\test_diary_roster.py tests\test_slots.py tests\test_booking_patient_flow.py tests\test_nurse_practitioner.py -q`
    -> 50 passed
  - A larger combined focused pytest bundle timed out before useful output; the
    same files passed in smaller sequential groups.

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

After user review, the next sprint should continue the patient-flow/resource model
rather than jumping straight to drag/drop. Recommended slices: physical waiting
areas linked to rooms/resources, a clearer linked-versus-provisional patient
confirmation action, and a small edit-patient-details foundation for the taskpane.
Drag/drop/resize should remain deferred until those rules are stable enough that
we are not smoothing over the wrong rules.
