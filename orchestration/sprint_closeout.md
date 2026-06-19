# EMR4 Sprint Closeout

This file is the user-facing closeout note for the latest fully integrated batch
of parallel-agent work. Codex updates it after submitted work has been polled,
reviewed, integrated, verified, pushed, and audited.

## Current Closeout

| Item | Value |
|---|---|
| Batch | Sprint 4: Diary Roster Consumption |
| Integrated through | `cf47471` |
| Status | User-reviewed and closed |
| Last updated | 2026-06-19 |

## What Changed

- Dev seed data now creates Room 1/2/3 and today's DiaryRoster rows:
  - Room 1 -> Dr Shera with practitioner ID and AHPRA.
  - Room 2 -> label `Nurse`.
  - Room 3 -> label `[Available]`.
- Roster endpoint test coverage now includes missing-date validation and mixed
  assigned/unassigned room responses.
- Diary frontend now fetches `/api/v1/diary/roster?date=YYYY-MM-DD` for the
  selected diary date and merges roster entries into visible diary columns.
- Roster frontend merge preserves template fallback semantics:
  - Empty/unassigned roster entries reuse matching template column assignment,
    practitioner AHPRA, breaks, tint, and slot interval.
  - Explicit label-only rooms such as `[Available]` still render as labels.
  - Roster `401 Unauthorized` is re-thrown so session expiry remains visible
    instead of silently falling back to template columns.
- Diary asset cache-bust moved to `v=38`.
- Added `orchestration/diary_roster_smoke_review.md` as the manual review
  checklist for this sprint.

## Recommended User Review

After the final push has deployed:

1. Run/apply latest migrations if the local DB is not current.
2. Run `python seed.py` if you want the dev roster rows for today's date.
3. Open/reopen the Word Online add-in, then open the diary.
4. On today's date, confirm Room 1/2/3 show the expected roster assignments:
   Dr Shera, Nurse, and `[Available]`.
5. Navigate to a date without roster rows and confirm the diary falls back to the
   normal template assignments rather than making every room `[Available]`.
6. Confirm date navigation refetches roster state for the selected date.
7. Confirm Refresh, Now/current-time marker, long appointments, booking notes,
   break blocks, off-grid hover bubbles, and narrow layout still behave as before.
8. If convenient, verify smoke mode still works:
   `https://yurifrusin.github.io/EMR4/diary/diary.html?smoke=true`.

## Not Required Before Moving On

- Booking create/edit/drag/drop/status mutations are still intentionally out of scope.
- Roster admin UI is not built yet; this sprint only consumes existing/seeded data.
- Online booking portal behaviour is not applicable yet.

## Known Follow-Up

- The test DB teardown can occasionally deadlock while dropping tables during
  rapid reruns, leaving a partial test DB. This is a test infrastructure issue,
  not introduced by the roster work. Suggested fix: harden the session-scoped
  engine fixture teardown with retry/connection cleanup.
- Consider adding an explicit backend `has_roster_entry` or equivalent flag later
  so the frontend can distinguish "room exists but no roster row" from an
  intentionally blank roster assignment without inference.
- Clean durable worker mirrors were realigned after final push.
- Dirty stale disposable worktree `codex/time-model` remains visible and should be
  reviewed before retirement.

## Verification

These are Codex/orchestrator verification notes, not commands the user is expected
to run.

- `node --check docs\diary\diary.js`
- `.venv\Scripts\python.exe -m pytest tests\test_agent_worktrees.py -q` -> 2 passed
- Initial diary roster/template pytest run hit the known partial test DB teardown
  issue (`relation "practices" does not exist`); reset the test DB schema using
  the documented SQLAlchemy reset command.
- `.venv\Scripts\python.exe -m pytest tests\test_diary_roster.py tests\test_diary_template.py -q` -> 18 passed after reset
- `git diff --check` -> only CRLF normalization warnings in markdown/review
  packet files; no whitespace errors

## Recommended Next Direction

User review passed. Sprint 5 has been dispatched:

- Claude: harden the test DB teardown/reset path.
- Antigravity: add a diary date control and soften the current-time marker.
- Codex worker: clarify smoke/live diary review expectations and prepare the
  post-integration checklist.

Booking mutation should remain deferred until the diary polish and test
infrastructure hardening have been reviewed.
