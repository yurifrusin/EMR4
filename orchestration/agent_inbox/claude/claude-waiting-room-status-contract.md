# claude-waiting-room-status-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | submitted |
| Created | 62cfeaa |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-waiting-room-status-contract --commit-message "Harden waiting room status contract" --message "Waiting room status contract ready for Codex review"` |

## Mission

Harden the read-only waiting-room/status API contract before booking/status mutation UI work. Build on the existing /api/v1/appointments/waiting-room endpoint and appointment status model.

## Scope

### In Scope

Inspect app/models/appointments.py, app/schemas/appointments.py, app/routers/appointments.py, and existing appointment tests. Add or tighten tests for GET /appointments/waiting-room and status-filtered appointment listing: practice scoping, date scoping to today, included statuses (Booked, Confirmed, Arrived, InConsult), excluded statuses (Completed, Cancelled, NoShow, DNA), ordering, and fields needed by the diary. Make only minimal production fixes if a test exposes an actual bug. Fill Completion Notes before submit.

### Out of Scope

Do not edit docs/diary/*, taskpane, Command Centre, Gemini/AI code, roster/template models, booking drag/drop/create/delete UI, or new status mutation UI. Do not move master or handoff/current.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Work only inside the stated scope unless the user or Codex expands it.
5. Do not merge to `master`.
6. Do not move `handoff/current`.
7. Run the verification listed below.
8. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
9. Finish with the submit command above.

## Hard Stop Rules

- Do not push to `master` or `handoff/current`.
- Do not manually work around a failed protocol command (`handin`, `sync`, `submit`,
  `realign`, or related orchestration commands).
- Report every protocol-followed command back to Codex/orchestrator, whether it
  succeeds or fails. For success, include the command, working directory, branch,
  and short success result.
- If any protocol command refuses to run or fails, stop and report the exact command,
  working directory, branch, `git status --short --branch`, and error output to the
  orchestrator. On push failure, `submit` will also try to publish a
  `submit-alert/...` branch for Codex to poll.
- If these instructions conflict with remembered prior protocol, trust the current
  `handin` alerts and this task packet.

## Verification

Run focused appointment tests, including any new waiting-room tests. At minimum run .venv\Scripts\python.exe -m pytest tests\test_appointment_conflicts.py tests\test_slots.py -q plus the new test file if created. Run broader tests only if shared fixtures/contracts are touched. Report exact commands/results.

## Merge Criteria

Waiting-room/status read API behavior is covered by tests; fields needed by a read-only diary status display are stable; no frontend/status-mutation work is introduced; any production changes are minimal and justified by tests.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

- **Files changed:** `tests/test_waiting_room.py` (new, 18 tests). No production code changed — existing endpoint passes all tests without modification.

- **What is tested:** auth gate; empty result; all 4 included statuses (Booked/Confirmed/Arrived/InConsult, parametrized); all 4 excluded statuses (Completed/Cancelled/NoShow/DNA, parametrized); date scoping (past date excluded; mixed-date set returns only today); ordering by `queue_position` then `start_time_local` (nulls last); `?practitioner_id=` filter; practice isolation; embedded `patient`, `practitioner` (with AHPRA), `appointment_type` (with `color_hex`), `end_time`, `start_time_local`, `appointment_date`.

- **Verification run:**
  ```
  python -m pytest tests/test_waiting_room.py -v          → 18 passed in 30.02s
  python -m pytest tests/test_appointment_conflicts.py tests/test_slots.py tests/test_auth_required.py -q  → 19 passed in 26.26s
  ```

- **Remaining risks:** `TODAY = date.today()` is computed at module import time. The endpoint resolves today in practice timezone (Australia/Sydney default). Tests seeding `appointment_date=TODAY` will fail at AEST/AEDT midnight if the date rolls over between import and the request. Known test-infrastructure limitation, not a product bug.
