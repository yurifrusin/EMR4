# plan-antigravity-antigravity-antigravity-diary-slot-search-preview-harness

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-antigravity-diary-slot-search-preview-harness` |
| Status | integrated |
| Created | 2026-06-26 20:46 +1000 |
| Source HEAD | `e1ec8a4` |

## Plan Summary

Plan for deterministic read-only slot-search proposal preview harness, gated strictly to smoke/review mode.

## My Understanding

Add a read-only, deterministic slot-search proposal preview to the diary grid, gated strictly to `?smoke=true` or a review fixture, to support automated verification. The live diary grid, appointment cards, booking modals, and edit/create booking flows must remain completely unaltered.

## Intended Surface / Boundary

- **Inside Scope**:
  - Gated rendering in [diary.js](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.js) only activated if `?smoke=true` AND `slot_preview=true` (or deterministic fixture flag) is present.
  - Read-only slots matching candidate intervals styled via [diary.css](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.css) (distinct, dashed, semi-transparent, non-interactive visual styling).
  - Validation test checks in [checks_diary.json](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/review/checks_diary.json) and a specific test case in [test_diary_smoke.py](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/review/test_diary_smoke.py).
- **Visually Adjacent Surfaces (Must NOT change)**:
  - Live diary grid rendering when `?smoke=true` is false (inert code path).
  - Actual appointment cards on the live page or in normal smoke mode.
  - Booking modal behavior (no new dialog triggers, no modifications to existing fields/audit history).
  - Click-to-create/edit flows (no changes to slot click behavior; preview slots must not respond to clicks and must not trigger any modals).

## Out Of Scope

- Any changes to actual appointment creation, status mutations, cancellations, or database commits.
- Interactive slot-search preview slots (no hover actions, click triggers, or drag/resize actions).
- Real-time/live slot search backend APIs, websockets, or LLM-driven endpoints.
- Integration of actual slot searches into the clinical Command Center or Taskpane UI for live GPs.

## Files I Expect To Edit

- [docs/diary/diary.js](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.js)
- [docs/diary/diary.css](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.css)
- [review/checks_diary.json](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/review/checks_diary.json)
- [review/test_diary_smoke.py](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/review/test_diary_smoke.py)

## Implementation Steps

1. **Mock Fixture Setup**: In [diary.js](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.js), define mock slot-search candidates under a conditional check: only active if the URL query parameter `smoke` is `true` AND `slot_preview` is `true`.
2. **Conditional Rendering**: In [diary.js](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.js), inside the column/grid cell rendering logic, if smoke mode + slot preview data is active, inject DOM elements for the preview slots. If not, bypass entirely. The live path must remain inert.
3. **Visual Styling**: Add styling in [diary.css](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.css) under a CSS class `.slot-preview-candidate`. Use `pointer-events: none` and visual styling (e.g., dashed borders, `opacity: 0.6`, background color that doesn't conflict with existing statuses) to ensure the previews are read-only, non-interactive, and visually distinct.
4. **Harness Integration**: Update [checks_diary.json](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/review/checks_diary.json) to include assertions confirming that when loaded with `?smoke=true&slot_preview=true`, the count of preview slots matches the expected mock count.
5. **Verify Non-Interactivity**: In [test_diary_smoke.py](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/review/test_diary_smoke.py), add a Playwright test that clicks on a slot-preview block and asserts that the booking modal does not open (remains hidden), verifying that click-to-create/edit flows are unaffected.

## Visual / Behavioural Acceptance Checks

- Loading `diary.html` normally or with `?smoke=true` (without slot-preview trigger) must show zero slot previews.
- Loading `diary.html?smoke=true&slot_preview=true` renders distinct, semi-transparent dashed slot-preview cards.
- Clicking on a slot-preview card does nothing (modal does not open).
- `pytest review/test_diary_smoke.py` passes successfully with all checks green.

## Risks / Ambiguities

- Potential overlap with existing appointments or breaks.
  - *Mitigation*: Ensure mock preview slots are scheduled in vacant hours or rooms specifically set up for preview test scenarios in smoke mode, and use absolute positioning with high z-index but with pointer-events disabled.
- Accidental impact on live booking paths.
  - *Mitigation*: Explicit guard clauses: the logic that generates the slot-preview DOM elements must be wrapped inside `if (isSmokeMode && hasSlotPreviewParam)`. No modifications to the standard grid cell click handler (`handleGridCellClick`) or appointment click handler.

## Codex Plan Review

- Review result: Accepted for Sprint 38 implementation.
- Required changes before implementation: None after scope guardrails were confirmed.
- Approved to proceed: yes
