# plan-antigravity-antigravity-diary-move-resize-proposal-flow

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-diary-move-resize-proposal-flow` |
| Status | pending_plan_review |
| Created | 2026-06-25 09:03 +1000 |
| Source HEAD | `8729ebe` |

## Plan Summary

Route appointment move/resize updates through the proposals update endpoint, using lightweight keyboard shortcuts.

## My Understanding

Integrate preflight checks for appointment move/resize actions (rescheduling time or duration adjustments) using keyboard shortcuts Alt+Arrows. Query the proposals update endpoint before mutating.

## Intended Surface / Boundary

Main diary grid appointment cards keydown event listeners.

## Out Of Scope

Backend changes, visual drag-and-drop handles, taskpane, Gemini, Resource Administration.

## Files I Expect To Edit

docs/diary/diary.js docs/diary/diary.html

## Implementation Steps

1. Add handleMoveResize preflight helper. 2. Bind Alt+ArrowUp/Down to shift start times. 3. Bind Alt+ArrowLeft/Right to adjust durations. 4. Bump version to v=87 in diary.html.

## Visual / Behavioural Acceptance Checks

Verify Alt+Arrows triggers proposal preflight; confirm conflict block alert blocks overlapping shifts; check warning confirm for break overlaps.

## Risks / Ambiguities

None.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
