# EMR4 Sprint Closeout

This file tracks what the user should review after each integrated sprint batch
of parallel-agent work. Codex updates it after submitted work has been polled,
reviewed, integrated, verified, pushed, and audited.

## Current Closeout

| Item | Value |
|---|---|
| Batch | Sprint 7: Controlled Status Mutation |
| Integrated through | Sprint 7 local review branch; pending push to `master` |
| Status | Integrated locally, pending deploy/user review |
| Last updated | 2026-06-19 |

## What Changed

- Added `tests/test_appointment_status_mutations.py` covering status PATCH auth,
  role guard, not-found/cross-practice isolation, valid/invalid statuses,
  response shape, and waiting-room inclusion/exclusion after mutation.
- Diary appointment cards now expose a compact status selector only when an
  appointment is active/expanded.
- The diary PATCHes `/appointments/{id}/status`, refreshes after success, handles
  smoke mode locally, and shows clear errors for failed updates/session expiry.
- Diary asset cache-bust moved to `v=42`.
- Added `orchestration/status_mutation_review.md` for Sprint 7 manual review.

## Recommended User Review

After the final push has deployed:

1. Open the live diary from the taskpane and click an appointment card; confirm
   the status selector appears only on the active/expanded card.
2. Change one appointment through `Booked`, `Confirmed`, `Arrived`, `InConsult`,
   and `Completed`; confirm the visible badge/colour/status updates after each
   successful change.
3. Set an appointment to `Cancelled`, `NoShow`, and `DNA`; confirm the card is
   visually de-emphasised and no longer appears in `/appointments/waiting-room`.
4. Narrow the diary window and confirm the selector does not crowd patient names,
   booking notes, break labels, date controls, Refresh, or Now.
5. Confirm long, overlapping, off-grid, and note-heavy appointments still render
   and can still be inspected.
6. Force or observe an expired session and confirm the diary shows a clear
   session-expired path rather than pretending the update succeeded.
7. Optionally use `orchestration/status_mutation_review.md` for the full manual
   API/UI/failure checklist.

## Not Required Before Moving On

- Booking create/edit/drag/drop/resize is still intentionally out of scope.
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

## Verification

These are Codex/orchestrator verification notes, not commands the user is expected
to run.

- `node --check docs\diary\diary.js` -> passed
- `git diff --check` -> passed
- `.venv\Scripts\python.exe -m pytest tests\test_appointment_status_mutations.py -q` -> 23 passed
- `.venv\Scripts\python.exe -m pytest tests\test_waiting_room.py tests\test_appointment_conflicts.py tests\test_slots.py -q` -> 31 passed after resetting stale test schema
- `.venv\Scripts\python.exe -m pytest tests\test_appointment_status_mutations.py tests\test_waiting_room.py tests\test_appointment_conflicts.py tests\test_slots.py -q` -> 54 passed sequentially
- `.venv\Scripts\python.exe -m pytest tests\test_diary_roster.py -q` -> 11 passed

## Recommended Next Direction

If user review passes, the next sprint can start booking create/edit planning in
a narrow way. Recommended order: simple create/edit form or modal first, then
drag/drop/resize later once mutation semantics and conflict handling feel solid.
