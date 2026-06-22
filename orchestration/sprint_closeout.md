# EMR4 Sprint Closeout

This file tracks what the user should review after each integrated sprint batch
of parallel-agent work. Codex updates it after submitted work has been polled,
reviewed, integrated, verified, pushed, and audited.

## Current Closeout

| Item | Value |
|---|---|
| Batch | Sprint 14: Receptionist Workflow Foundations |
| Integrated through | pending commit |
| Status | Integrated locally and verified; push/audit pending |
| Last updated | 2026-06-22 |

## What Changed

- Added an atomic backend check-in/status contract: `PATCH
  /api/v1/appointments/{id}/status` now accepts optional `waiting_area_id`.
  If omitted, the current waiting area is preserved; if set to a UUID, the
  appointment is assigned to that active practice-scoped waiting area; if set to
  `null`, the waiting area is cleared.
- Added focused backend regression tests for waiting-area assignment during
  status transitions, including auth, assign, clear, reassign, inactive-area,
  cross-practice, and no-area-loss behaviour.
- Improved the diary Waiting Room side panel only:
  collapsible sections, cleaner count badges, segmented waiting-area tabs,
  compact cards, and lower-noise edit/link controls.
- Kept the main diary grid appointment positioning unchanged. The prior
  accidental appointment-card stacking/cascade behaviour was not reintroduced.
- Added `orchestration/resource_admin_bernie_tool_design.md`, the Sprint 14
  design reference for rooms, bookable resources, diary columns, waiting areas,
  provisional vs linked patient identity, attendance status, SMS/reminder
  confirmation, and future Bernie supervised tool boundaries.
- Updated `implementation_plan.md`, `parallel_workstreams.md`, and task/review
  packets to point future room/resource/waiting-area and Bernie work at that
  design boundary.
- Updated diary assets to `v=65`.

## Recommended User Review

1. Restart the backend and hard refresh the diary.
2. Confirm the live diary loads `diary.js?v=65`.
3. Open the Waiting Room panel and check that:
   - the section counts no longer show widely spaced parentheses
   - Waiting Room / In Consult / Expected Today / Finished sections can collapse
     and expand
   - collapsed/open section state persists after refresh
   - area tabs still behave sensibly when waiting-area data exists
   - cards are more compact and edit/link affordances are less visually noisy
4. Confirm ordinary appointment cards in the main diary grid are not stacked or
   cascaded on top of each other unless their times genuinely overlap.
5. Optional direct API check: choose an appointment and a waiting-area ID, then
   call `PATCH /appointments/{id}/status` with both `status` and
   `waiting_area_id`; confirm the returned appointment includes that
   `waiting_area_id`.

User review result: pending.

## Not Required Before Moving On

- No drag/drop/resize appointment testing is required yet.
- No taskpane Patient Details duplicate testing is required for Sprint 14; that
  was Sprint 13.
- No Command Centre, Scribe, Gemini, billing, results, letters, medications, or
  clinical-note regression is required for this sprint.
- No patient document rewrite, public online-booking, kiosk, SMS/reminder, or
  Bernie runtime testing is required.

## Known Follow-Up

- Patient Details is still a foundation slice. Add stronger validation, Medicare
  IRN polish, IHI/Medicare verification hooks, duplicate-candidate review, and a
  proper shared demographic model before relying on it in routine use.
- GitHub Pages deployment should be kept to canonical `master`.
- Physical waiting areas now exist in the backend, but room/resource admin and
  per-room default waiting-area editing are still future work. The Sprint 14
  design reference is `orchestration/resource_admin_bernie_tool_design.md`.
- Decide whether terminal appointment statuses such as Completed, Cancelled,
  NoShow, and DNA should automatically clear `waiting_area_id` or merely become
  invisible through waiting-room filters.
- The diary waiting-area UI should eventually auto-focus the area associated with
  the active room/column and support true stacked/condensed cards inside
  high-volume Waiting Room sections such as Finished.
- Appointment state still needs the planned distinction between patient identity
  linkage, attendance workflow, and future SMS/reminder confirmation.
- Bernie should continue to follow
  `orchestration/resource_admin_bernie_tool_design.md`: typed proposals,
  human-confirmed writes, and audit.
- Drag/drop/resize should remain deferred until the resource model and patient
  flow semantics are settled.
- The `pytest_asyncio` loop-scope deprecation warning remains.
- Do not run two pytest processes against the same `gp_pms_test` database in
  parallel; concurrent runs can collide during fixture setup/teardown.

## Verification

Codex/orchestrator verification for Sprint 14:

- `node --check docs\diary\diary.js` -> passed
- `.venv\Scripts\python.exe -m py_compile app\schemas\appointments.py app\routers\appointments.py tests\test_waiting_area_checkin_contract.py` -> passed
- `git diff --check` -> passed, with only CRLF/LF warnings on Markdown files
- `.venv\Scripts\python.exe -m pytest tests\test_waiting_area_checkin_contract.py -q -p no:randomly` -> 8 passed
- `.venv\Scripts\python.exe -m pytest tests\test_waiting_area_checkin_contract.py tests\test_waiting_area_contract.py tests\test_appointment_status_mutations.py tests\test_break_overlap_contract.py tests\test_appointment_patient_link.py tests\test_appointment_conflicts.py tests\test_diary_template.py tests\test_diary_roster.py tests\test_slots.py tests\test_booking_patient_flow.py tests\test_nurse_practitioner.py -q --tb=short -p no:randomly` -> 111 passed, 1 warning

## Recommended Next Direction

The next sprint should build on the clarified receptionist workflow without yet
jumping to drag/drop. Recommended slices: expose waiting-area assignment in the
diary check-in UI, add small room/waiting-area admin endpoints or admin UI
foundation, and begin a tool-schema-only Bernie proof path after audit/write
confirmation rules are explicit.
