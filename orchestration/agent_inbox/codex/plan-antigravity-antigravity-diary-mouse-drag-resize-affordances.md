# plan-antigravity-antigravity-diary-mouse-drag-resize-affordances

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-diary-mouse-drag-resize-affordances` |
| Status | pending_plan_review |
| Created | 2026-06-25 10:54 +1000 |
| Source HEAD | `90d0d15` |

## Plan Summary

Add mouse drag and resize affordances on diary appointment cards, using snapping, ghost previews, and routing drops through the proposal preflight checks.

## My Understanding

Implement visible and discoverable mouse-based interactions on EMR4 diary appointment cards:
- **Rescheduling (Move)**: Dragging cards vertically (shifts start time in 15-minute intervals) and horizontally (shifts to a different bookable practitioner column).
- **Duration (Resize)**: Dragging top or bottom edges vertically to change the duration in 15-minute increments (with a floor of 15 minutes).
- **Validation**: On mouseup (drop), the new time/practitioner state is validated against the proposals update endpoint. If blocked (conflict), the action is reverted and blocked modal is shown; if warnings (break overlap), a confirmation dialog is shown; if safe, the update is saved and the grid is reloaded.
- **Ghost Preview**: Display a semi-transparent dashed ghost element that snaps to the grid lines (30px = 15 mins) during drag/resize.

## Intended Surface / Boundary

- `docs/diary/diary.js`, `docs/diary/diary.css`, and `docs/diary/diary.html`.
- Main diary grid columns, empty slot slots, break areas, and appointment cards.
- Rest of EMR4 taskpane, database models, and Resource Administration views are completely unaffected.

## Out Of Scope

- Direct mutations without proposal preflight check.
- Custom drag-and-drop libraries (vanilla JS pointer/mouse event tracking only).
- Recurring appointments, patient search, and patient link modifications.

## Files I Expect To Edit

- [docs/diary/diary.js](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.js)
- [docs/diary/diary.css](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.css)
- [docs/diary/diary.html](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.html)

## Implementation Steps

1. **CSS Stylings (`diary.css`)**:
   - Define `.appt-resize-handle` absolute positions at top/bottom of cards. Show subtle backgrounds on card hover to indicate clickability.
   - Define `.appt-ghost-preview` with dashed border and transparent indigo background.
   - Add `cursor: move` / `cursor: grab` styles to the `.appt` cards.

2. **Column Body Data Attributes (`diary.js`)**:
   - Add `columnBody.dataset.practitionerAhpra = col.practitioner_ahpra || ""` and `columnBody.dataset.colIdx = colIdx` during grid construction.

3. **Append Handles & Events to Card Spans**:
   - Inside `renderGrid`, append top and bottom resize handle elements to each card.
   - Bind `mousedown` to card spans. Check if click targets handles or card body (ignoring select elements, buttons, inputs, etc.).
   - Launch pointer tracking using global `mousemove` and `mouseup` document listeners.

4. **Pointer tracking & Snapping (`mousemove`)**:
   - Calculate vertical displacement delta `dy`, and horizontal displacement `dx`.
   - Snap `dy` to slot increments (`SLOT_HEIGHT_PX` = 30px represents `intervalMins`).
   - If dragging, detect hover columns using `document.elementFromPoint(clientX, clientY)`. If hovering a valid practitioner column, attach the ghost preview to that column.
   - Reposition and resize the ghost preview card to reflect snapped start minutes and duration.

5. **Drop Validation & Save (`mouseup`)**:
   - Clean up listeners and remove the ghost element.
   - Check if changes occurred. If so, call `handleMoveResize(appt, deltaStart, deltaDuration, targetCol)` (which we'll extend to handle new columns/practitioners).
   - If aborted or blocked, the card resets to its initial grid position automatically.

6. **Cache-Buster Bump (`diary.html`)**:
   - Bump script/css version parameters to `v=88`.

## Visual / Behavioural Acceptance Checks

- **Visual Affordances**: Gripper style cursor changes on card hover. Resize handles show cursors (`ns-resize`) on top/bottom card borders.
- **Dashed Ghost Snapping**: Dragging a card displays a dashed preview card that snaps smoothly in 15-minute steps.
- **Cross-Column Move**: Dragging card horizontally to another practitioner's column correctly updates target practitioner in preview and validates against their scheduling breaks and overlaps.
- **Duration Floor check**: Shrinking duration from top or bottom clamp at 15 minutes.
- **Proposal Reuse**: Conflicting drops show the standard warning/block overlays. Reverted cards jump back to their original slots.

## Risks / Ambiguities

- **Click vs Drag Ambiguity**: Small mouse movements might trigger drag.
  - *Mitigation*: We will require a minimum displacement threshold (e.g. 3px) before initiating the ghost preview drag state, so clicks are not registered as drags.
- **Scroll Offset Calculations**: If grid is scrolled, clientY offset calculations can shift.
  - *Mitigation*: Track offsets relative to parent grid container scroll state, or use relative coordinate tracking.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
