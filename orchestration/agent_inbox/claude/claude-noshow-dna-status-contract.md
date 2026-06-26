# claude-noshow-dna-status-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 90ef76b |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-noshow-dna-status-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-noshow-dna-status-contract --commit-message "No-show/DNA status contract" --message "claude-noshow-dna-status-contract ready for Codex review"` |

## Mission

Plan, then after approval harden or prove the backend appointment status proposal contract for NoShow and DNA attendance outcomes so they are terminal, non-blocking, practice-scoped, and do not mutate state before explicit confirmation.

## Scope

### In Scope

Plan packet first. After approval: app/routers/appointments.py, app/schemas/appointments.py only if needed, focused appointment status/proposal/waiting-area tests for NoShow and DNA terminal transitions, slot-conflict/non-blocking coverage, and no direct mutation before proposal confirmation.

### Out of Scope

Diary frontend, taskpane, Command Centre, cancellation reason/note capture, cancelled appointment review UI, recurrence, SMS/reminders, billing, broad audit logging, migrations unless a verified backend contract gap requires one.

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

Plan packet first. After approval: py_compile touched appointment modules, focused pytest for appointment status/proposal/waiting-area/no-show-DNA coverage, adjacent conflict tests if touched, and git diff --check.

## Merge Criteria

Codex can merge when the plan is approved, NoShow/DNA backend semantics are covered by tests or explicitly proven unchanged, no out-of-scope surface changes are present, and verification passes or any limitation is clearly justified.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
