# plan-antigravity-antigravity-diary-cancellation-reason-flow

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-diary-cancellation-reason-flow` |
| Status | integrated |
| Created | 2026-06-25 12:31 +1000 |
| Source HEAD | `7c9c7f5` |

## Plan Summary

Introduce a dynamic cancellation reason text input inside the booking modal when the user initiates cancellation, and pass this reason in preflight check payloads and the final DELETE mutation JSON body.

## My Understanding

When a receptionist clicks "Cancel Appointment", we want to capture an optional cancellation reason or note.
To preserve a clean layout, we will:
1. Show an optional "Cancellation Reason" text field dynamically inside the booking editor modal once the user clicks "Cancel Appointment" (when the button changes to "Confirm Cancel").
2. Focus the input immediately so the user can easily type.
3. Pass the reason as `cancellation_reason` in the preflight proposal payload:
   - For the dedicated delete proposal endpoint: `POST /appointments/proposals/delete/{id}` with `{ intent: "delete_appointment", cancellation_reason }`.
   - For the fallback status proposal: `POST /appointments/proposals/status/{id}` with `{ status: "Cancelled", waiting_area_id: null }` (we will omit the `cancellation_reason` from this fallback check unless the backend is verified to support it).
4. Pass the reason inside the JSON request body `{ cancellation_reason }` on the final delete mutation `DELETE /appointments/{id}` in live mode (we will NOT append it as a query parameter).
5. In Smoke Mode, log/simulate the proposal and cache the cancellation reason on the mock appointment object.
6. Reset the cancellation reason field (clear value and hide container) when the user aborts, closes, or reopens the modal.

## Intended Surface / Boundary

- `docs/diary/diary.js` and `docs/diary/diary.html`.
- Specifically, the booking edit modal's cancellation workflow and footer actions.
- Nearby surfaces (appointment cards, patient search fields, grids, and waiting area panels) will not be modified.

## Out Of Scope

- Backend database migration, schema, or router logic (these are owned by Claude).
- Altering the "Reason for Visit" field behavior for active appointments.
- Modifications to the taskpane or Command Centre.

## Files I Expect To Edit

- [docs/diary/diary.js](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.js)
- [docs/diary/diary.html](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.html)

## Implementation Steps

1. **Modify `docs/diary/diary.html`**:
   - Insert a hidden form group element `#booking-cancel-reason-container` (containing `#booking-cancel-reason` text input) directly before the `#booking-error` element in the form structure.

2. **Modify `deleteBooking()` in `docs/diary/diary.js`**:
   - On first click (when setting `deleteBtn.dataset.confirming = "true"`):
     - Unhide `#booking-cancel-reason-container`.
     - Call `focus()` on `#booking-cancel-reason` to let the user immediately type the note.
   - On second click ("Confirm Cancel"):
     - Extract `cancellation_reason` from `#booking-cancel-reason`.
     - In **Smoke Mode**, call `simulateStatusProposal(appt, { status: "Cancelled", waiting_area_id: null })` and check.
     - In **Live Mode**, attempt to query the dedicated delete proposal endpoint `POST /appointments/proposals/delete/${editingAppointmentId}` with JSON body `{ intent: "delete_appointment", cancellation_reason }`.
     - Fallback / Compatibility Path: If the dedicated delete proposal endpoint returns a `404`, catch that and call the status proposal endpoint `POST /appointments/proposals/status/${editingAppointmentId}` with JSON body `{ status: "Cancelled", waiting_area_id: null }` (omitting the `cancellation_reason` field).
     - If confirmed/safe, execute `DELETE /appointments/${editingAppointmentId}` with JSON body `{ cancellation_reason }` (or filter cache and store simulated reason in smoke mode).
     - Hide `#booking-cancel-reason-container` and clear `#booking-cancel-reason` input.
   - On abort (user rejects warning overlay):
     - Hide `#booking-cancel-reason-container`, clear its input value, and reset the delete button's confirming state.

3. **Reset Modal States**:
   - Update `closeBookingModal()` and `openBookingModalForEdit()` to clean up the cancellation reason input (set value to `""` and hide container) so that opening another appointment starts from a clean state.

4. **Monotonic Cache-Buster Bump**:
   - Bump asset script and stylesheet query parameters in `diary.html` from `v=95` to `v=96` (preserving monotonic cache-busting above Sprint 28).

## Visual / Behavioural Acceptance Checks

- **Cancellation reason capture**: Clicking "Cancel Appointment" dynamically displays the "Cancellation Reason (Optional)" input field.
- **Reversion on Cancel**: Aborting the confirmation overlay correctly resets the button state and hides the cancellation reason text input.
- **Data Transmission**:
  - Verification that the reason is sent in the JSON body of the delete proposal request.
  - Verification that the reason is sent in the JSON request body of the final DELETE mutation request (no query parameters appended).
- **Asset bump**: Asset versions are validated as `v=96`.
- **Smoke Mode simulation**: Deleting an appointment in smoke mode functions smoothly, reflecting cancellation warning constraints, and resets states cleanly on close/cancel.

## Risks / Ambiguities

- Backend contract updates: Addressed by routing the reason as a JSON body payload in the final DELETE mutation and delete proposal checks, and omitting it on the status-proposal check fallback.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
