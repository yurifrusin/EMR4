# plan-antigravity-antigravity-diary-create-proposal-flow

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-diary-create-proposal-flow` |
| Status | pending_plan_review |
| Created | 2026-06-23 01:25 +1000 |
| Source HEAD | `9fb853d` |

## Plan Summary

Diary create proposal flow integration

## My Understanding

Integrate EMR4 Diary booking modal with the appointment creation proposal flow, showing conflict blocks, break warnings, and provisional warnings, and requiring confirmation.

## Intended Surface / Boundary

docs/diary/diary.{html,css,js}

## Out Of Scope

Backend changes, taskpane, Command Centre, main diary grid positioning, drag/drop/resize.

## Files I Expect To Edit

docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js

## Implementation Steps

Add #booking-warnings container in diary.html. Add .form-warning and .btn-warning-action styles in diary.css. Implement resetProposalConfirmation helper and input change listeners in diary.js. Update saveBooking to POST to proposals/create and handle blocks, warnings, and confirmations before normal booking creation.

## Visual / Behavioural Acceptance Checks

Verify block errors block write; warnings trigger Confirm & Save step; form edits reset confirmation; normal creations work.

## Risks / Ambiguities

Simulating proposal checking in mock/smoke mode requires accurate client-side mapping of mock appointments.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
