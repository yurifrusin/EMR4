# claude-waiting-area-checkin-defaults

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 4d8d1c7 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-waiting-area-checkin-defaults --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-waiting-area-checkin-defaults --commit-message "Waiting area check-in defaults" --message "claude-waiting-area-checkin-defaults ready for Codex review"` |

## Mission

Plan, then after approval implement, the backend contract for selecting/defaulting waiting areas during check-in and optionally clearing waiting_area_id on terminal attendance states. Keep identity verification, booking confirmation, attendance, and waiting-area placement separate.

## Scope

### In Scope

app/routers/appointments.py, app/schemas/appointments.py, app/models/diary.py only if required, focused tests around waiting_area_id assignment/defaulting/clearing, practice scoping, inactive/cross-practice guards, and terminal status behaviour.

### Out of Scope

No diary frontend, no taskpane, no room/admin UI, no Bernie runtime, no SMS/email/voice reminder confirmation, no billing/finalisation locking, no drag/drop/resize, no patient demographic edits.

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

Plan packet first. After approval: focused pytest for waiting-area/status/check-in contracts, py_compile for touched backend modules, git diff --check.

## Merge Criteria

Codex accepts the plan before coding; API semantics make default waiting-area assignment explicit and test-covered; terminal-status clearing policy is deliberate and documented; tests pass; no frontend files touched.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
