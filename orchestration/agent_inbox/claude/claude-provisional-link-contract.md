# claude-provisional-link-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | c96c637 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-provisional-link-contract --commit-message "Add provisional booking link contract" --message "Provisional booking link contract ready for Codex review"` |

## Mission

Finish the backend contract for moving a provisional appointment into a linked patient-record booking, while preserving the separation between patient identity/linkage and attendance status. Add a warning-oriented contract for bookings that cross soft break blocks if a minimal backend helper or test fixture is useful, but do not make breaks hard blockers.

## Scope

### In Scope

app/models/appointments.py, app/schemas/appointments.py, app/routers/appointments.py, app/models/diary.py, app/schemas/diary.py, app/routers/diary.py, focused appointment and diary tests, Alembic migration only if truly needed, seed/test helpers only as needed.

### Out of Scope

Diary frontend implementation, taskpane/Command Centre UI, drag/drop/resize, SMS reminder confirmation, billing/completion workflow, full waiting-area modelling, real ADHA/IHI integration.

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

Run focused appointment patient-link/create-edit/status/conflict tests and any diary break/roster tests touched; run migration check if a migration is added; run git diff --check. Include exact commands/results and remaining risks in Completion Notes.

## Merge Criteria

Backend/API allows a provisional appointment to be linked to an existing patient record without losing appointment details; tests cover patient-link update and identity/attendance separation; break-overlap semantics are documented or testable as warning-only/soft-block compatible; no non-orchestrator merge to master or handoff/current.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
