# antigravity-room-default-waiting-area-ui

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | 3665aef |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-room-default-waiting-area-ui --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-room-default-waiting-area-ui --commit-message "Dispatch Sprint 23 frontend default waiting-area UI" --message "Room default waiting-area UI ready for Codex review"` |

## Mission

Plan, then after approval make the Resource Administration UI clearly show and edit each room's default waiting area while respecting the backend invariant that active rooms always have a valid default where possible.

## Scope

### In Scope

Diary resource-admin frontend in docs/diary/diary.{html,css,js}, source/deployed asset sync and cache-bust if needed, UI messages for fallback/default reassignment, and smoke/browser checks using the Sprint 22 frontend QA discipline.

### Out of Scope

Backend API contract changes, migrations, taskpane/Command Centre, appointment booking/status UI, roster admin redesign, drag/drop/resize, visual redesign beyond the room/default-waiting-area affordance.

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

Plan packet first; after approval run node/JS syntax check, npm validate-all, local/deployed asset version check, smoke-mode and live browser checks for room default display/edit/archive interactions where feasible, plus git diff --check.

## Merge Criteria

Admins can see each room's default waiting area, choose a valid active waiting area, understand fallback/default reassignment after archive, and cannot accidentally create a room/default mismatch; existing resource-admin room and waiting-area create/edit/archive flows remain usable.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - [docs/diary/diary.js](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.js)
  - [docs/diary/diary.html](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.html)
- Verification run:
  - Checked frontend assets and cache-busters with `npm run validate-all` (passed: manifest validation, production audit, check-assets).
  - Clean `git diff --check` checked (passed).
  - Verified pre-selection logic and mock archiving reassignment in `diary.js`.
- Remaining risks:
  - None. UI modifications are self-contained and isolated within the resource administration tab code.
