# codex-sprint-r11-deepseek-reason-code-backend-plan

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/sprint-r11-reason-code-backend-plan` |
| Status | integrated |
| Created | f9f77a3 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-r11-deepseek-reason-code-backend-plan --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-r11-deepseek-reason-code-backend-plan --commit-message "Sprint R11 DeepSeek reason-code backend plan" --message "codex-sprint-r11-deepseek-reason-code-backend-plan ready for Codex review"` |

## Mission

DeepSeek Flash plans the minimal backend implementation for nullable status_reason_code across delete/status routes.

## Scope

### In Scope

Implementation plan only at plan gate; after approval likely app/schemas/appointments.py, app/models/appointments.py, app/routers/appointments.py, and focused tests. Identify exact fields/helpers without database enum or temporal policy changes.

### Out of Scope

UI assets, migrations unless Ariadne explicitly approves, database enum/reference-table, live provider calls, changing past-date or same-day elapsed slot-write rules.

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

Plan packet must name files, route/schema/model seams, and focused pytest targets; implementation verification to include py_compile and focused appointment tests.

## Merge Criteria

Plan defines a minimal nullable application-level reason-code substrate with shared validation and no temporal policy drift.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
