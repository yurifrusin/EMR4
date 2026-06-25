# plan-antigravity-antigravity-diary-cancel-proposal-flow

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-diary-cancel-proposal-flow` |
| Status | pending_plan_review |
| Created | 2026-06-25 11:40 +1000 |
| Source HEAD | `e1e0f9e` |

## Plan Summary

Gate diary appointment cancellation behind status proposal preflight check (status: "Cancelled") before executing the delete mutation.

## My Understanding

Currently, clicking "Confirm Cancel" inside the booking editor modal directly triggers the delete mutation (`DELETE /appointments/{editingAppointmentId}` or cache filtering) without preflighting safety checks. 
The new flow will intercept the cancellation and preflight it against the status proposal system:
- **Preflight Check**: Call `/appointments/proposals/status/{id}` (or `simulateStatusProposal` in smoke mode) with `{ status: "Cancelled", waiting_area_id: null }`.
- **Verification Overlay**:
  - If blocked, display "Action Blocked" and cancel.
  - If warnings (e.g. checkout warnings, clearing waiting area, terminal status transitions), display the confirm dialog.
  - If confirmed or safe, execute the actual delete mutation (`DELETE /appointments/{id}`) and reload the diary.
  - If aborted, reset the delete button's confirming state so they can retry.

## Intended Surface / Boundary

- `docs/diary/diary.js` and `docs/diary/diary.html`.
- Booking edit modal delete/cancel button (`#btn-booking-delete`).
- Grid appointment cards, slots, breaks, and nearby elements are unaffected.

## Out Of Scope

- Direct mutations without checking proposal preflight first.
- Backend routing modifications, schema changes, or database migrations.
- Recurrence or waitlist changes.

## Files I Expect To Edit

- [docs/diary/diary.js](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.js)
- [docs/diary/diary.html](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.html)

## Implementation Steps

1. **Modify `deleteBooking()` in `diary.js`**:
   - Locate the target appointment using `editingAppointmentId` from cache.
   - Construct the cancellation status payload: `{ status: "Cancelled", waiting_area_id: null }`.
   - In **Smoke Mode**:
     - Call `simulateStatusProposal(appt, payload)`.
   - In **Live Mode**:
     - POST payload to `/appointments/proposals/status/${editingAppointmentId}`.
   - Evaluate proposal outcome:
     - If `blocks.length > 0` or `warnings.length > 0` or `autonomy_tier === "proposal"`, call the unified confirmation dialog `showStatusProposalDialog(proposal)`.
     - If confirmed (or safe):
       - Proceed with `DELETE` API request (or filter cache in smoke mode) and reload the diary via `loadDiary(true)`.
     - If aborted:
       - Reset `deleteBtn.dataset.confirming = ""` and restore original text "Cancel Appointment".
       - Re-enable the button.

2. **Monotonic Cache-Buster Bump (`diary.html`)**:
   - Bump script/css version query parameters from `v=93` to `v=94` (preserving monotonic ordering above Sprint 27).

## Visual / Behavioural Acceptance Checks

- **Cancel Warning check**: Cancel an arrived patient who has a waiting area assigned. Verification: Modal warns that status change will clear the patient from the waiting room. Clicking "Confirm & Save" cancels it; clicking "Cancel" keeps the booking and resets the cancel button text.
- **Cancel Revert state**: Aborting the confirmation overlay correctly resets the "#btn-booking-delete" state back to "Cancel Appointment".
- **Blocked Check**: Blocking constraints display Action Blocked modal and abort deletion.
- **Asset bump**: validation checks pass for `v=94`.

## Risks / Ambiguities

- None. Uses existing status proposal API contract.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
