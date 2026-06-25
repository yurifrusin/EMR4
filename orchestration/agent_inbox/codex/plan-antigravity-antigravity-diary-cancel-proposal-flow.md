# plan-antigravity-antigravity-diary-cancel-proposal-flow

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-diary-cancel-proposal-flow` |
| Status | integrated |
| Created | 2026-06-25 11:40 +1000 |
| Source HEAD | `e1e0f9e` |

## Plan Summary

Gate diary appointment cancellation behind status proposal preflight check before executing the delete mutation, utilizing the dedicated delete proposal endpoint when present.

## My Understanding

Currently, clicking "Confirm Cancel" inside the booking editor modal directly triggers the delete mutation (`DELETE /appointments/{editingAppointmentId}` or cache filtering) without preflighting safety checks.
The new flow will intercept the cancellation and preflight it:
- **Preflight Check**:
  - Prefer querying the dedicated delete proposal endpoint `POST /appointments/proposals/delete/{appointment_id}` (using `{ intent: "delete_appointment" }` payload) if available.
  - Fallback / Compatibility Path: If the dedicated delete proposal endpoint is not present (e.g., returns `404`), fallback to querying `POST /appointments/proposals/status/{appointment_id}` with `{ status: "Cancelled", waiting_area_id: null }`.
  - In **Smoke Mode**, fall back to simulating a status change via `simulateStatusProposal(appt, { status: "Cancelled", waiting_area_id: null })`.
- **Verification Overlay**:
  - If blocked, display "Action Blocked" and cancel.
  - If warnings (e.g. checkout warnings, clearing waiting area, terminal status transitions), display the confirm dialog.
  - If confirmed or safe, execute the actual delete mutation (`DELETE /appointments/{id}`) and reload the diary.
  - If aborted, reset the delete button's confirming state so they can retry.
- **Preserved Behaviour**:
  - Existing `Alt+Arrow` keyboard move/resize behaviour remains fully supported.
  - All mouse drag/drop and resize actions continue to route through the proposal preflight path before any write.

## Intended Surface / Boundary

- `docs/diary/diary.js` and `docs/diary/diary.html`.
- Booking edit modal delete/cancel button (`#btn-booking-delete`).
- Grid appointment cards, slots, breaks, and nearby elements are unaffected.

## Out Of Scope

- Direct mutations without checking proposal preflight first.
- Backend routing modifications, schema changes, or database migrations (these are owned by Claude).
- Recurrence or waitlist changes.

## Files I Expect To Edit

- [docs/diary/diary.js](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.js)
- [docs/diary/diary.html](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.html)

## Implementation Steps

1. **Modify `deleteBooking()` in `diary.js`**:
   - Locate the target appointment using `editingAppointmentId` from cache.
   - In **Smoke Mode**:
     - Call `simulateStatusProposal(appt, { status: "Cancelled", waiting_area_id: null })`.
   - In **Live Mode**:
     - Attempt to POST to `/appointments/proposals/delete/${editingAppointmentId}` with body `{ intent: "delete_appointment" }`.
     - If the fetch returns a `404` (Not Found) or fails due to endpoint absence, catch the failure and perform a fallback POST to `/appointments/proposals/status/${editingAppointmentId}` with body `{ status: "Cancelled", waiting_area_id: null }`.
   - Evaluate proposal outcome:
     - If `blocks.length > 0` or `warnings.length > 0` or `autonomy_tier === "proposal"`, call the unified confirmation dialog `showStatusProposalDialog(proposal)`.
     - If confirmed (or safe):
       - Proceed with `DELETE` API request (or filter cache in smoke mode) and reload the diary via `loadDiary(true)`.
     - If aborted:
       - Reset `deleteBtn.dataset.confirming = ""` and restore original text "Cancel Appointment".
       - Re-enable the button.

2. **Monotonic Cache-Buster Bump (`diary.html`)**:
   - Bump script/css version query parameters from `v=94` to `v=95` (preserving monotonic ordering above Sprint 27's `v=94`).

## Visual / Behavioural Acceptance Checks

- **Cancel Warning check**: Cancel an arrived patient who has a waiting area assigned. Verification: Modal warns that status change will clear the patient from the waiting room. Clicking "Confirm & Save" cancels it; clicking "Cancel" keeps the booking and resets the cancel button text.
- **Cancel Revert state**: Aborting the confirmation overlay correctly resets the "#btn-booking-delete" state back to "Cancel Appointment".
- **Blocked Check**: Blocking constraints display Action Blocked modal and abort deletion.
- **Asset bump**: validation checks pass for `v=95`.
- **Keyboard/Mouse Drag-drop Preservation**: Alt+Arrow move/resize and mouse drag/drop are fully functional and route proposals correctly.

## Risks / Ambiguities

- Backend endpoint availability: Solved by catching 404/rejection on the dedicated delete proposal endpoint and falling back to the status proposal endpoint.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
