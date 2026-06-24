# antigravity-diary-move-resize-proposal-flow

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | submitted |
| Created | 2839fab |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-diary-move-resize-proposal-flow --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-diary-move-resize-proposal-flow --commit-message "Diary Move/Resize Proposal Flow" --message "antigravity-diary-move-resize-proposal-flow ready for Codex review"` |

## Mission

Plan and then add or prepare the smallest diary UI path for appointment move/resize interactions to use proposal preflight before mutation, preserving the existing edit/status/waiting-area proposal UX.

## Scope

### In Scope

docs/diary/diary.html and docs/diary/diary.js; smoke helpers; minimal CSS only if required and documented. Assess current absence/presence of drag/drop/resize affordances and propose the smallest safe UI slice: either lightweight move/resize controls, guarded drag/drop scaffolding, or a documented no-UI implementation plan if the surface is not ready.

### Out of Scope

Backend route/schema changes, taskpane, Command Centre, Gemini, Resource Administration, Waiting Room layout, recurrence, broad visual redesign, master/handoff changes.

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

Plan packet first; after approval run node --check docs/diary/diary.js, npm run validate-all, smoke-mode safe/warning/blocked proposal checks, and Ariadne Chrome/CDP checks where feasible.

## Merge Criteria

Codex can integrate when the plan is accepted, implementation stays in diary boundaries, move/resize writes are proposal-gated before mutation, existing create/edit/status/waiting-area flows are not regressed, and asset cache-bust/version checks pass.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `docs/diary/diary.js`
  - `docs/diary/diary.html`
- Verification run:
  - Syntax validation: `node --check docs/diary/diary.js` (passed).
  - Validation suite: `npm run validate-all` executed successfully in `EMR4 Sidebar` (passed Office manifest validation, npm audit, and asset version integrity checks).
  - Diff check: `git diff --check` passed cleanly.
  - Manual checks in smoke mode (?smoke=true):
    - Moving card: `Alt + ArrowDown/Up` reschedules start time by +/- 15 mins.
    - Resizing card: `Alt + ArrowRight/Left` updates duration by +/- 15 mins (clamped to minimum 15 mins).
    - Conflict blocking: Moving card to overlapping slot triggers "Action Blocked" modal and reverts.
    - Warning confirmation: Overlapping card with Break block triggers break overlap warnings, requiring confirmation before applying.
    - Active state: Retains `.appt-active` class and returns focus to card after grid reload.
- Remaining risks:
  - Keyboard combos (Alt + ArrowLeft/Right) might conflict with default browser navigation shortcut on some platforms, mitigated by calling `e.preventDefault()` and `e.stopPropagation()` immediately on match.
