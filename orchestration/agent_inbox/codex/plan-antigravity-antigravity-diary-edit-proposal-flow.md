# plan-antigravity-antigravity-diary-edit-proposal-flow

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-diary-edit-proposal-flow` |
| Status | integrated |
| Created | 2026-06-24 22:55 +1000 |
| Source HEAD | `bb006db` |

## Plan Summary

Route diary appointment edit/reschedule saves through the update proposal endpoint before PUTting, mirroring the create-proposal Confirm & Save warning pattern.

## My Understanding

Route diary appointment edit/reschedule saves through the update proposal endpoint `POST /appointments/proposals/update/{editingAppointmentId}` before doing the actual `PUT`, mirroring the create-proposal Confirm & Save warning pattern.

## Intended Surface / Boundary

The booking edit modal within the EMR4 Diary (`docs/diary/diary.js` and `docs/diary/diary.html`).

## Out Of Scope

Backend route/schema changes, create-booking proposal behaviour except shared helper reuse, taskpane/Command Centre, Waiting Room panel layout, Resource Administration, drag/drop/resize.

## Files I Expect To Edit

- `docs/diary/diary.js`
- `docs/diary/diary.html`

## Implementation Steps

1. In `simulateProposal(payload)` inside `docs/diary/diary.js`, exclude the appointment being edited (`editingAppointmentId`) from the double-booking conflict check so it does not trigger self-conflict blocks.
2. Call `resetProposalConfirmation()` at the beginning of `openBookingModalForEdit(appt)`.
3. In `saveBooking()`, unify create and edit proposal checks by removing the `if (!editingAppointmentId)` check around the proposal call. Call `POST /appointments/proposals/update/${editingAppointmentId}` for updates and `POST /appointments/proposals/create` for creations.
4. Render errors (if proposal contains blocks) or warnings (changing the button text/class to `Confirm & Save` / `btn-warning-action` and setting `dataset.confirmed = "true"`).
5. Ensure `skipLocalWarnings` checks `saveBtn.dataset.confirmed === "true"`.
6. Update cache-buster version suffix in `docs/diary/diary.html` for `diary.js` and `diary.css` from `v=84` to `v=85`.

## Visual / Behavioural Acceptance Checks

1. Try to edit an appointment to overlap another booking. Confirm it is blocked with the message "This appointment overlaps an existing booking (Mock)."
2. Try to edit an appointment to cause a warning (e.g., break overlap). Confirm warnings are shown and the save button changes to "Confirm & Save". Confirm editing fields resets the button to "Save Booking".
3. Save an appointment without any conflicts or after confirming warnings. Confirm the PUT request is sent and the diary is reloaded.
4. Saving an appointment without changing slot does not trigger a self-conflict overlap.

## Risks / Ambiguities

None. The proposal format is identical to create proposals.

## Codex Plan Review

- Review result: Accepted after amendment. Scope stayed within diary edit-proposal UI flow and preserved create-proposal behaviour.
- Required changes before implementation: None after the amended plan clarified update-proposal endpoint use, warning confirmation reset, smoke-mode self-conflict handling, and cache-bust.
- Approved to proceed: yes; implementation was later reviewed and integrated by Ariadne.
