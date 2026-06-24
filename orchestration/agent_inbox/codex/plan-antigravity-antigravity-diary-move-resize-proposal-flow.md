# plan-antigravity-antigravity-diary-move-resize-proposal-flow

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-diary-move-resize-proposal-flow` |
| Status | integrated |
| Created | 2026-06-25 09:03 +1000 |
| Source HEAD | `8729ebe` |

## Plan Summary

Route appointment move/resize updates through the proposals update endpoint, using lightweight keyboard shortcuts (Alt + Arrow keys) on active/focused appointment cards.

## My Understanding

Provide keyboard-based rescheduling (Alt+ArrowUp/Down to shift start times by +/- 15 mins) and resizing (Alt+ArrowLeft/Right to adjust durations by +/- 15 mins, minimum 15 mins) for diary appointments. The flow must preflight mutations using the proposal system (`POST /appointments/proposals/update/{appointment_id}` or `simulateProposal` in smoke mode).
- Blocks (such as appointment conflicts) will display the blocked dialog.
- Warnings (such as break overlaps) will display a confirmation dialog before proceeding.
- Approved/Safe proposals will mutate the appointment directly.
- Ensure the selected/active status of the card is restored after the diary reloads.

## Intended Surface / Boundary

- Appointment card elements (`span.appt` elements with `.appt` class) within the main diary grid columns.
- Nearby visual surfaces such as booking gaps, the time ruler, and other practitioners' columns will not be changed.
- No visual drag handles or layout grid modifications.

## Out Of Scope

- Visual drag-and-drop handles.
- Backend routing, schema modifications, database migrations.
- Recurring appointment logic, taskpane, Command Centre, or Resource Admin views.

## Files I Expect To Edit

- [docs/diary/diary.js](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.js)
- [docs/diary/diary.html](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.html)

## Implementation Steps

1. **Implement `handleMoveResize(appt, deltaStart, deltaDuration)` helper**:
   - Calculate new start time in `HH:MM` by converting current start time to minutes, adding `deltaStart` (clamped to practice hours if needed, typically multiples of 15), and formatting back.
   - Calculate new duration by adding `deltaDuration` (ensuring a minimum of 15 minutes).
   - In **Smoke Mode** (query parameter `smoke=true`):
     - Temporarily set `editingAppointmentId = appt.id` so that `simulateProposal` does not raise a self-conflict.
     - Call `simulateProposal(payload)`.
     - Restore `editingAppointmentId`.
   - In **Live Mode**:
     - POST payload to `/appointments/proposals/update/${appt.id}`.
   - Handle response:
     - If `proposal.blocks` has entries, show the action blocked dialog using `showStatusProposalDialog(proposal)` (which is already built).
     - If `proposal.warnings` has entries, show the confirm dialog using `showStatusProposalDialog(proposal)`.
     - If safe/confirmed:
       - In smoke mode: update `mockAppointmentsCache` matching item and reload the diary.
       - In live mode: PUT to `/appointments/${appt.id}` and reload the diary.
       - After reload, restore focus/active status to the card with `data-id="${appt.id}"`.

2. **Add Keydown Interception in `renderGrid`**:
   - Within `renderGrid` where keydown listeners are bound to `span`, capture:
     - `Alt + ArrowUp`: `handleMoveResize(a, -15, 0)`
     - `Alt + ArrowDown`: `handleMoveResize(a, 15, 0)`
     - `Alt + ArrowLeft`: `handleMoveResize(a, 0, -15)`
     - `Alt + ArrowRight`: `handleMoveResize(a, 0, 15)`
   - Call `e.preventDefault()` and `e.stopPropagation()` to prevent browser defaults.

3. **Cache Buster Version Bump**:
   - Increment `v=86` to `v=87` in `docs/diary/diary.html` for both `diary.css` and `diary.js`.

## Visual / Behavioural Acceptance Checks

- **Conflict Check**: Move an appointment via Alt+Down into an occupied slot. Verification: Blocking modal "Action Blocked - This appointment overlaps an existing booking" appears and mutation is prevented.
- **Break Warning**: Move an appointment via Alt+Up into a Break block. Verification: Warning modal "Confirm Status Change - This appointment overlaps with a scheduled break block" appears. Cancelling does not move it; confirming saves it.
- **Duration Resize**: Select a card and press Alt+Right. Verification: The card height expands by one 15-minute slot.
- **Duration Floor**: Press Alt+Left repeatedly. Verification: The duration is blocked from going below 15 minutes.
- **Card State Retention**: Card remains highlighted (`.appt-active`) after reloading.

## Risks / Ambiguities

- **Browser Navigation Hijack**: In some browsers/OSs, `Alt + ArrowLeft` and `Alt + ArrowRight` trigger back/forward history navigation.
  - *Mitigation*: We must call `e.preventDefault()` and `e.stopPropagation()` immediately on matching key events to block this default browser navigation behavior.
- **Self-Conflict in Simulation**: `simulateProposal` checks conflicts against all cached appointments.
  - *Mitigation*: Dynamically bind `editingAppointmentId` to the active appointment ID before simulating proposal checks to ignore self-overlapping.

## Codex Plan Review

- Review result: Accepted; keyboard move/resize slice matched the requested minimal diary surface.
- Required changes before implementation: None.
- Approved to proceed: yes; implementation released with `complete sprint task`.
