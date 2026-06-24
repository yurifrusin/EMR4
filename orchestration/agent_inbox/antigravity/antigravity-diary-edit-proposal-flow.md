# antigravity-diary-edit-proposal-flow

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | 511eff0 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-diary-edit-proposal-flow --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-diary-edit-proposal-flow --commit-message "Dispatch Sprint 24 diary edit proposal flow" --message "Diary edit proposal flow ready for Codex review"` |

## Mission

Plan, then after approval route diary appointment edit/reschedule saves through the existing non-mutating update proposal endpoint before performing the actual PUT, mirroring the create-proposal Confirm & Save pattern.

## Scope

### In Scope

docs/diary/diary.{html,css,js}; booking edit modal proposal call to /appointments/proposals/update/{id}; safe/warning/blocked UI copy; Confirm & Save state reset on relevant field changes; smoke-mode simulation; cache-bust if assets change.

### Out of Scope

Backend route/schema changes, create-booking proposal behaviour except shared helper reuse, taskpane/Command Centre, Waiting Room panel layout, Resource Administration, drag/drop/resize, Bernie runtime.

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

Plan packet first; after approval run 
ode --check docs/diary/diary.js, 
pm run validate-all, smoke/browser notes for edit safe/warning/blocked flows where feasible, and git diff --check.

## Merge Criteria

Editing/rescheduling an appointment no longer writes until the update proposal is safe or user-confirms warnings; blocked proposals prevent writes; existing create booking proposal and ordinary diary rendering continue to work.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - [docs/diary/diary.js](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.js)
  - [docs/diary/diary.html](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.html)
- Verification run:
  - Syntax check: `node --check docs/diary/diary.js` (Passed)
  - Layout & Integrity validations: `npm run validate-all` (Passed manifest, 0 vulnerabilities audit, check-assets version bump `v=85` verification)
  - Diff formatting: `git diff --check` (Passed)
  - Tested proposal warning rendering, save buttons, and self-conflict exclusions in Smoke Mode.
- Remaining risks:
  - None. Changes are fully covered by smoke mode logic and run cleanly.
