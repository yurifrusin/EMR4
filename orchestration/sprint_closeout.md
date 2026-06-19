# EMR4 Sprint Closeout

This file tracks what the user should review after each integrated sprint batch
of parallel-agent work. Codex updates it after submitted work has been polled,
reviewed, integrated, verified, pushed, and audited.

## Current Closeout

| Item | Value |
|---|---|
| Batch | Sprint 6: Read-Only Patient Flow Visibility |
| Integrated through | Sprint 6 pushed to `master`; baton and mirrors aligned |
| Status | User-reviewed and closed |
| Last updated | 2026-06-19 |

## What Changed

- Added `tests/test_waiting_room.py` with 18 tests covering the read-only
  waiting-room endpoint: auth, included/excluded statuses, date/practice scoping,
  practitioner filtering, ordering, and embedded appointment fields.
- Diary appointment cards now show clearer lifecycle/status affordances with
  status-specific tints, right-side status bars, and compact status badges.
- Diary asset cache-bust moved to `v=41`.
- Added `orchestration/patient_flow_review.md` to define read-only appointment
  status semantics before booking/status mutation controls begin.
- Replaced active EMR logo references with `emr_cube1.png` across the taskpane,
  Command Centre, diary, taskpane source assets, and add-in manifest/ribbon icon
  URLs.

## Recommended User Review

After the final push has deployed:

1. Reopen the Word Online add-in and confirm the taskpane/banner/ribbon logo uses
   the new cube image.
2. Open the diary from the taskpane and confirm the diary and Command Centre logo
   surfaces use the new cube image.
3. In smoke mode, verify Booked, Confirmed, Arrived, InConsult, Completed,
   Cancelled, NoShow, and DNA appointments are visually distinguishable.
4. Narrow the diary window and confirm status badges do not crowd patient names,
   booking notes, break labels, or header controls.
5. Confirm long appointments, overlapping appointments, off-grid appointments,
   booking notes, Refresh, Now, and the current-time marker still feel usable.
6. If testing the API directly, confirm `/appointments/waiting-room` includes
   Booked/Confirmed/Arrived/InConsult and excludes Completed/Cancelled/NoShow/DNA.
7. Decide whether the compact status badges feel useful or too noisy before the
   next sprint introduces status mutation controls.

## Not Required Before Moving On

- Booking create/edit/drag/drop/status mutations are still intentionally out of scope.
- Roster admin UI is not built yet.
- Online booking portal behaviour is not applicable yet.
- A full live waiting-room UI is not built yet; this sprint hardens the read-only
  backend contract and diary visual language.

## Known Follow-Up

- The `pytest_asyncio` loop-scope deprecation warning remains and should be
  addressed before it becomes a default-behaviour change.
- `tests/test_waiting_room.py` uses import-time `date.today()`; it may be fragile
  around timezone midnight and can be hardened later if CI exposes it.
- Dirty stale disposable worktree `codex/time-model` remains visible and should be
  reviewed before retirement.
- Archimedes did not start the documentation-only Codex task; the orchestrator
  recovered it directly in `orchestration/patient_flow_review.md`.

## Verification

These are Codex/orchestrator verification notes, not commands the user is expected
to run.

- `node --check docs\diary\diary.js` -> passed
- `git diff --check` -> passed
- `python -c "import xml.etree.ElementTree as ET; ET.parse(...)"` for
  `EMR4 Sidebar\manifest.xml` -> passed
- `.venv\Scripts\python.exe -m pytest tests\test_waiting_room.py tests\test_appointment_conflicts.py tests\test_slots.py tests\test_auth_required.py -q` -> 37 passed

## Recommended Next Direction

User review passed: waiting-room API status counts were correct, terminal
statuses were absent, and diary status colours/badges were useful without feeling
cluttered. Sprint 7 has been dispatched toward controlled receptionist-facing
status mutation before booking create/edit/drag/drop work.
