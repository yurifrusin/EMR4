# claude-waiting-area-checkin-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 7fd03d0 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-waiting-area-checkin-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-waiting-area-checkin-contract --commit-message "Waiting area check-in contract" --message "claude-waiting-area-checkin-contract ready for Codex review"` |

## Mission

Design and, after plan approval only, implement the backend contract for assigning waiting areas during patient check-in and status transitions. This sprint is plan-gated: first produce the implementation plan and stop.

## Scope

### In Scope

Potentially app/routers/appointments.py, app/schemas/appointments.py, app/models/appointments.py only if required, focused tests around waiting-area assignment/check-in/status mutation, and task/review packet notes. Consider whether status PATCH should accept waiting_area_id or whether update/check-in should remain separate. Preserve practice scoping, patient identity rules, same-day waiting-room semantics, and correction/backtracking rules.

### Out of Scope

No diary frontend changes, no taskpane changes, no room/admin UI, no drag/drop/resize, no Bernie implementation, no SMS/reminder confirmation, no billing/finalisation locking. Do not start coding until Codex/user approves the plan and says complete sprint task.

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

Plan stage: implementation plan packet plus GUI echo. Implementation stage after approval: focused pytest for appointment status/waiting-area/patient-link contracts, plus py_compile for touched backend modules.

## Merge Criteria

Codex accepts the plan before coding; implementation stays scoped; tests pass; API semantics make waiting-area assignment explicit without confusing patient identity confirmation, SMS confirmation, or attendance status.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
