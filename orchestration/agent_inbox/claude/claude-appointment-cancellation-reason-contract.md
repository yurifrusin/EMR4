# claude-appointment-cancellation-reason-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 24c76b4 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-appointment-cancellation-reason-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-appointment-cancellation-reason-contract --commit-message "Appointment cancellation reason contract" --message "claude-appointment-cancellation-reason-contract ready for Codex review"` |

## Mission

Plan first, then after approval add a minimal backend contract so receptionist cancellation/delete can capture a short cancellation reason or note without weakening proposal-first safety semantics.

## Scope

### In Scope

app/routers/appointments.py; app/schemas/appointments.py; app/models/appointments.py only if a separate persisted cancellation field is justified; Alembic migration only if a new field is chosen; focused appointment cancellation/proposal tests; minimal seed/test helpers if needed

### Out of Scope

Diary frontend implementation; taskpane; Command Centre; patient demographics; billing; SMS/reminders; broad audit logging; proposal review history; changing non-cancel appointment reason semantics unless required by the plan

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Before editing project code, write an implementation plan and stop. The plan
   must be shown in the agent GUI and captured for Codex with the plan command
   above. Do not code until the user/Codex says `complete sprint task`.
5. After plan approval, work only inside the stated scope unless the user or Codex
   expands it.
6. Do not merge to `master`.
7. Do not move `handoff/current`.
8. Run the verification listed below.
9. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
10. Finish with the submit command above.

## Implementation Plan Requirements

Before coding, the implementation plan must include:

- My Understanding
- Intended Surface / Boundary
- Out of Scope
- Files I Expect To Edit
- Implementation Steps
- Visual / Behavioural Acceptance Checks
- Risks / Ambiguities

Pay special attention to visually loaded words such as cards, slots, stacking,
panels, waiting room, diary grid, booking slot, and status. State exactly which
surface is affected and which nearby surfaces must not change.

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

Plan packet first; after approval run py_compile touched appointment router/schema/model, focused cancellation/delete proposal pytest, migration checks if added, adjacent status/update proposal tests if contract touched, git diff --check

## Merge Criteria

Codex can verify cancellation reason/note is represented consistently in proposal command and final mutation, terminal status safety remains intact, waiting_area clearing still works, tests cover auth/practice scope/abort-safe proposal/no stranded waiting area, and no frontend files are changed by this workstream

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
