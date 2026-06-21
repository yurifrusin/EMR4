# EMR4 Sprint Closeout

This file tracks what the user should review after each integrated sprint batch
of parallel-agent work. Codex updates it after submitted work has been polled,
reviewed, integrated, verified, pushed, and audited.

## Current Closeout

| Item | Value |
|---|---|
| Batch | Sprint 13: Waiting Areas and Patient Details Foundation |
| Integrated through | local integration, pending push |
| Status | Integrated locally and verified |
| Last updated | 2026-06-21 |

## What Changed

- Added first-class `WaitingArea` backend resources for physical waiting areas,
  with practice scoping, active/ordered listing, and room default linkage.
- Added appointment `waiting_area_id` and `queue_position` support, including
  waiting-room filtering by area and same-day waiting-room query behaviour.
- Added `GET /api/v1/diary/waiting-areas` for diary clients.
- Added migration `f6a7b8c9d0e1_add_waiting_area.py` and dev seed data for
  Main Waiting Room and Children's Area.
- Added diary patient-flow tabs for waiting areas and reconciled them with the
  new backend waiting-area IDs while preserving legacy string fallback.
- Added taskpane Patient Details editing for the loaded patient, including
  save/cancel/error/duplicate-block handling.
- Hardened patient update duplicate checks so re-saving a patient's own strong
  identifiers is allowed, but duplicate IHI or Medicare+IRN from another patient
  is blocked inside the same practice.
- Hardened appointment timezone fallback so missing timezone data cannot crash
  the waiting-room path.
- Updated diary assets to `v=63` and taskpane assets to `v=42`.

## Recommended User Review

1. Run migrations if your local DB is not current:
   `.venv\Scripts\python.exe -m alembic upgrade head`.
2. Restart the backend and hard refresh the taskpane/diary.
3. Confirm the live diary loads `diary.js?v=63`.
4. Open the Waiting Room panel and check that area tabs appear sensibly when
   waiting-area data or assigned appointments exist.
5. Move an appointment into Arrived/InConsult/Completed and confirm the waiting
   panel sections still update correctly.
6. Open a patient file in the taskpane and use the pencil button to edit patient
   details.
7. Confirm Save Details updates the taskpane banner and cancel/Escape exits the
   Patient Details overlay cleanly.
8. Try changing a patient to duplicate another patient's IHI or Medicare+IRN and
   confirm the duplicate is blocked with a readable error.
9. Confirm New Patient and Search overlays still open and close normally after
   using Patient Details.

## Not Required Before Moving On

- No drag/drop/resize appointment testing is required yet.
- No Command Centre, Scribe, Gemini, billing, results, letters, medications, or
  clinical-note regression is required for this sprint.
- No patient document rewrite testing is required; editing demographics updates
  the DB/taskpane state only and intentionally does not rewrite existing Word
  document headings or file names yet.
- No public online-booking or kiosk testing is required.

## Known Follow-Up

- Patient Details is a foundation slice. Add stronger validation, Medicare IRN
  polish, IHI/Medicare verification hooks, duplicate-candidate review, and a
  proper shared demographic model before relying on it in routine use.
- Physical waiting areas now exist in the backend, but room/resource admin and
  per-room default waiting-area editing are still future work.
- The diary waiting-area UI should eventually auto-focus the area associated with
  the active room/column and support stacked/condensed cards for high-volume
  sections such as Finished.
- Appointment state still needs the planned distinction between patient identity
  linkage, attendance workflow, and future SMS/reminder confirmation.
- Bernie should wait until the booking/resource and patient-identity rules are
  stable enough to expose as supervised backend tools.
- Drag/drop/resize should remain deferred until the resource model and patient
  flow semantics are settled.
- The `pytest_asyncio` loop-scope deprecation warning remains.
- Do not run two pytest processes against the same `gp_pms_test` database in
  parallel; concurrent runs can collide during fixture setup/teardown.

## Verification

Codex/orchestrator verification for Sprint 13:

- `python -m py_compile app\routers\appointments.py app\routers\patients.py app\routers\diary.py app\schemas\appointments.py app\schemas\diary.py app\models\appointments.py app\models\diary.py` -> passed
- `node --check docs\diary\diary.js` -> passed
- `node --check "EMR4 Sidebar\src\taskpane\taskpane.js"` -> passed
- `node --check docs\taskpane\taskpane.js` -> passed
- `git diff --check` -> passed
- `.venv\Scripts\python.exe -m pytest tests\test_patients.py tests\test_waiting_area_contract.py -q` -> 29 passed
- `.venv\Scripts\python.exe -m pytest tests\test_waiting_area_contract.py tests\test_break_overlap_contract.py tests\test_appointment_patient_link.py tests\test_appointment_conflicts.py tests\test_appointment_status_mutations.py tests\test_diary_template.py tests\test_diary_roster.py tests\test_slots.py tests\test_booking_patient_flow.py tests\test_nurse_practitioner.py tests\test_patients.py -q -p no:randomly` -> 123 passed, 1 warning

## Recommended Next Direction

The next sprint should keep consolidating the receptionist workflow rather than
jumping to drag/drop. Recommended slices: assign waiting areas during check-in,
make diary/Waiting Room state transitions clearer, add room/resource admin
foundations, and continue preparing the safe backend tools Bernie will later use
for supervised slot-finding and booking suggestions.
