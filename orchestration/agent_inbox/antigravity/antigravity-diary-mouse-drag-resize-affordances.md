# antigravity-diary-mouse-drag-resize-affordances

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | submitted |
| Created | a9ef0bb |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-diary-mouse-drag-resize-affordances --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-diary-mouse-drag-resize-affordances --commit-message "Dispatch Sprint 27 diary mouse affordances" --message "antigravity-diary-mouse-drag-resize-affordances ready for Codex review"` |

## Mission

Plan and then, only after approval, add visible diary mouse affordances for appointment move and resize that reuse the existing proposal-gated move/resize pathway rather than creating a direct-write shortcut.

## Scope

### In Scope

docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js, and frontend smoke tooling if needed. Add discoverable drag/move and top/bottom resize handles or equivalent visible affordances, ghost/preview state while dragging, proposal preflight on drop, blocked/warning/safe dialog reuse, cancel/revert behavior, and cache-bust diary assets.

### Out of Scope

No backend route redesign, no schema/migration, no recurrence, no patient search/linking, no waiting-room behavior, no Resource Administration, no taskpane/Command Centre, no direct mutation before proposal confirmation.

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

node --check docs/diary/diary.js; run npm check-assets from the EMR4 Sidebar directory or with equivalent prefix; browser/Chrome smoke where available for drag preview, cancel, confirm, blocked conflict, and asset v bump; git diff --check

## Merge Criteria

Plan packet submitted first. Implementation, if approved, provides visible mouse move/resize affordances that preserve keyboard shortcuts and route all writes through existing proposal confirmation semantics, with no direct risky mutation.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `docs/diary/diary.js`
  - `docs/diary/diary.css`
  - `docs/diary/diary.html`
- Verification run:
  - Static Check: `node --check docs/diary/diary.js` (passed).
  - Build/Audits check: `npm run validate-all` in `EMR4 Sidebar` (passed with manifest valid, 0 vulnerabilities, and cache-buster verified at v=93).
  - Diff check: `git diff --check` (passed).
  - Mouse Interaction Verification (Smoke Mode):
    - Grab/grabbing cursors on cards and resize cursors on top/bottom handles render correctly.
    - Ghost preview card aligns to 15-minute snapping boundaries.
    - Dragging card horizontally updates the target practitioner.
    - Dropping card triggers preflight proposals: conflict blocks display Action Blocked and revert positions; break overlaps display Warning and confirm/cancel options.
    - Focused/active states restore post-update.
    - Keyboard Alt+Arrow keys continue to function as expected.
- Remaining risks:
  - Mouse coordinate tracking over nested scrolling elements (mitigated by using bounding client rects and relative pointer offsets).
