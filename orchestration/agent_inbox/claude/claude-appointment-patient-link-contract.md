# claude-appointment-patient-link-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 90a951f |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-appointment-patient-link-contract --commit-message "Add appointment patient-link contract" --message "Appointment patient-link contract ready for Codex review"` |

## Mission

Split patient identity/linkage semantics from appointment attendance status. Add a minimal backend contract so appointments can distinguish linked patient records from provisional free-text names, without treating Confirmed as an attendance state.

## Scope

### In Scope

app/models/appointments.py, app/schemas/appointments.py, app/routers/appointments.py, Alembic migration if needed, focused appointment create/edit/status/waiting-room tests, seed/test helpers only if needed.

### Out of Scope

Diary frontend, taskpane/Command Centre UI, drag/drop/resize, SMS reminder confirmation, billing/completion guards beyond documenting test expectations.

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

Run focused appointment create/edit/status/waiting-room/conflict tests plus migration check if a migration is added; run git diff --check. Include exact commands/results in the Codex review packet.

## Merge Criteria

Existing linked-patient booking API remains backward compatible; tests define provisional patient-name behaviour and patient-link/attendance separation; no non-orchestrator merge to master or handoff/current.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
