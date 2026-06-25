# plan-antigravity-antigravity-diary-cancelled-appointment-review-ui

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-diary-cancelled-appointment-review-ui` |
| Status | pending_plan_review |
| Created | 2026-06-25 13:31 +1000 |
| Source HEAD | `63f427b` |

## Plan Summary

Add a read-only "Cancelled" section to the Patient Flow sidebar to show recently cancelled appointments for the day, along with their captured cancellation reasons.

## My Understanding

Staff need a restrained, read-only interface to review recently cancelled appointments and see cancellation reasons.
To implement this cleanly without obscuring the grid or existing workflows:
1. We will add a fifth section "Cancelled" (`#flow-sec-cancelled`) to the right patient flow panel sidebar.
2. In `updateFlowPanel()`, we will stop discarding cancelled appointments and instead bucket them into a `cancelled` array, sorted by time and filtered by the selected tab.
3. In `renderFlowList()`, we will omit all interaction elements (link buttons, edit buttons, action buttons, status select dropdowns) for cancelled appointments, keeping them completely read-only.
4. We will display the `cancellation_reason` string (if present) as an italicized note inside the card body.
5. In `diary.css`, we will style cancelled cards to be slightly transparent with a line-through name text decoration.
6. In Smoke Mode, we will add a mock cancelled appointment to the cache to make interactive testing immediately available.

## Intended Surface / Boundary

- `docs/diary/diary.js`, `docs/diary/diary.html`, and `docs/diary/diary.css`.
- Specifically, the bottom of the patient flow sidebar content.
- Nearby surfaces (grid slot columns, appointment card drags, dialog overlays) remain untouched.

## Out Of Scope

- Backend endpoints, database changes, or route updates (owned by Claude).
- Re-activation / restore status mutations (cancellation is strictly read-only in this stream).
- Grid rendering changes (cancelled bookings remain hidden on the grid itself).

## Files I Expect To Edit

- [docs/diary/diary.js](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.js)
- [docs/diary/diary.html](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.html)
- [docs/diary/diary.css](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.css)

## Implementation Steps

1. **Modify `docs/diary/diary.html`**:
   - Append the `#flow-sec-cancelled` section structure directly after the `#flow-sec-finished` block.
   - Bump script/css query parameter versions to `v=97` (monotonic bump).

2. **Modify `docs/diary/diary.css`**:
   - Define `.flow-card-cancelled` styles (opacity `0.85`, grey left border).
   - Define `.flow-card-cancelled .flow-card-name` styles (line-through, muted grey).
   - Add `.flow-card-cancellation-reason` styles (muted grey, italic, margin-top `5px`, font-size `11px`).

3. **Modify `docs/diary/diary.js`**:
   - In `updateFlowPanel()`, categorize `status === "Cancelled"` appointments into a `cancelled` array instead of returning early.
   - Sort and filter `cancelled` by active waiting area tabs.
   - Render them via `renderFlowList("flow-list-cancelled", filteredCancelled, null, null)`.
   - Update the section count element `#flow-sec-cancelled .flow-sec-count`.
   - In `renderFlowList()`, check `a.status === "Cancelled"` to skip rendering edit/link buttons.
   - If `a.status === "Cancelled" && a.cancellation_reason`, append a new `.flow-card-cancellation-reason` element displaying the reason text.
   - Insert a mock cancelled appointment with a simulated reason into the smoke mode cache to enable immediate visual testing.

## Visual / Behavioural Acceptance Checks

- **Section visibility**: A "Cancelled" section is rendered in the flow panel, displaying the count of cancelled appointments.
- **Read-Only layout**: Cancelled cards do not show link buttons, edit buttons, or check-in buttons.
- **Cancellation reason visibility**: The captured cancellation reason is clearly displayed on the card in italic, muted styling.
- **Visual Distinction**: Cancelled cards show a grey left border, line-through names, and are slightly transparent.
- **Asset bump**: Asset query parameter values are validated as `v=97`.
- **Smoke Mode simulation**: Coherent smoke mode listing of pre-cancelled bookings.

## Risks / Ambiguities

- None. Uses existing queried data in `todayAppointments`.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
