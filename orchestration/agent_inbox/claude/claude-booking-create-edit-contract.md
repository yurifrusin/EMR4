# claude-booking-create-edit-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 9ccd838 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-booking-create-edit-contract --commit-message "Booking create/edit contract" --message "claude-booking-create-edit-contract ready for Codex review"` |

## Mission

Harden the backend appointment create/edit contract so the diary can safely create and edit bookings through the existing API surface.

## Scope

### In Scope

app/models/appointments.py, app/schemas/appointments.py, app/routers/appointments.py, focused appointment conflict/create/update tests, and minimal seed/test helper changes if needed. Cover appointment_date + start_time_local, duration, practitioner/patient/type validation, conflict behavior, role/auth gates, and response shape.

### Out of Scope

docs/diary frontend, drag/drop/resize UI, roster admin UI, waiting-room display app, taskpane/Command Centre/Gemini, online booking portal, broad refactors.

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

.venv\\Scripts\\python.exe -m pytest tests/test_appointment_conflicts.py tests/test_appointment_status_mutations.py tests/test_waiting_room.py tests/test_slots.py -q plus any new focused booking create/edit tests.

## Merge Criteria

Existing behavior remains compatible; create/edit failures are explicit and tested; conflict and practice-scope protections are covered; Codex review packet includes changed files, commands run, pass/fail output, and remaining risks.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
