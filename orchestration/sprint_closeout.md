# EMR4 Sprint Closeout

This file tracks what the user should review after each integrated sprint batch
of parallel-agent work. Codex updates it after submitted work has been polled,
reviewed, integrated, verified, pushed, and audited.

## Current Closeout

| Item | Value |
|---|---|
| Batch | Sprint 5: Diary Polish and Test Infrastructure |
| Integrated through | Sprint 5 closeout commit on `master` |
| Status | User-reviewed and closed |
| Last updated | 2026-06-19 |

## What Changed

- Test database setup now uses SQLAlchemy `NullPool` in `tests/conftest.py`, so
  pooled PostgreSQL connections do not linger between tests or rapid reruns.
- Test database cleanup now retries `TRUNCATE practices RESTART IDENTITY CASCADE`
  up to three times before failing, which adds defence-in-depth without masking
  persistent fixture failures.
- Diary UI now includes a date picker control in the header.
- Diary current-time marker is softer: a strong pill remains in the time column,
  while the grid-spanning line is faint and behind appointments.
- Diary asset cache-bust moved to `v=40`.
- Added `orchestration/diary_smoke_live_review.md` to clarify smoke-mode versus
  live-diary review expectations.

## Recommended User Review

After the final push has deployed:

1. Open/reopen the Word Online add-in, then open the diary from the taskpane.
2. Use the date picker to jump to today, tomorrow, and a manually chosen future
   date; confirm the visible date and columns update each time.
3. Confirm Prev, Next, Today, Now, and Refresh still work after using the date
   picker.
4. On today's seeded date, confirm Room 1/2/3 show Dr Shera, Nurse, and
   `[Available]`.
5. Navigate to a date without roster rows and confirm the diary falls back to the
   normal template columns.
6. Press Now on today's date and confirm the current-time marker is useful but
   visually quiet and does not obscure appointment text or notes.
7. Check that notes, long appointments, break blocks, Refresh, and narrow window
   layout still feel usable.
8. Optionally open
   `https://yurifrusin.github.io/EMR4/diary/diary.html?smoke=true` and confirm
   the smoke fixture still works, remembering that smoke mode is mock data and
   not a live roster/auth test.

## Not Required Before Moving On

- Booking create/edit/drag/drop/status mutations are still intentionally out of scope.
- Roster admin UI is not built yet.
- Online booking portal behaviour is not applicable yet.

## Known Follow-Up

- Dirty stale disposable worktree `codex/time-model` remains visible and should be
  reviewed before retirement.
- Clean stale branch/worktree noise from old Codex diary review branches still
  appears in `poll`; retire or prune it after confirming no useful unmerged work
  remains.
- Consider adding an explicit backend `has_roster_entry` or equivalent flag later
  so the frontend can distinguish "room exists but no roster row" from an
  intentionally blank roster assignment without inference.
- The `pytest_asyncio` loop-scope deprecation warning remains; it is unrelated to
  Sprint 5 but should be addressed before it becomes a default-behaviour change.

## Verification

These are Codex/orchestrator verification notes, not commands the user is expected
to run.

- `node --check docs\diary\diary.js` -> passed
- `git diff --check` -> passed
- `.venv\Scripts\python.exe -m pytest tests\test_agent_worktrees.py -q` -> 4 passed
- `.venv\Scripts\python.exe -m pytest tests\test_diary_roster.py tests\test_diary_template.py -q` -> 18 passed
- Immediate rerun of `.venv\Scripts\python.exe -m pytest tests\test_diary_roster.py tests\test_diary_template.py -q` -> 18 passed

## Recommended Next Direction

User review passed. Codex recommends moving next toward safe read-only
waiting-room or appointment status visibility before drag/drop booking
mutations. The diary is now stable enough to start exposing patient-flow state,
but booking mutation work should still wait until status visibility and review
flows are comfortable.
