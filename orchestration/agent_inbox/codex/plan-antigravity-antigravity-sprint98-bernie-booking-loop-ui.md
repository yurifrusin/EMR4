# plan-antigravity-antigravity-sprint98-bernie-booking-loop-ui

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint98-bernie-booking-loop-ui` |
| Status | pending_plan_review |
| Created | 2026-07-01 12:14 +1000 |
| Source HEAD | `ca8b293` |

## Plan Summary

Add Choose Different Time flow and hide raw missing_practitioner_id for ordinary users.

## My Understanding

Provide a 'Choose different time' button when in confirmation_ready state to allow users to go back to candidate_selection_required. Ensure ordinary receptionists do not see the raw code 'Missing Practitioner Id' block when the practitioner name has been resolved. Show detailed error codes on confirmation failure only for Dev/Debug mode; ordinary users should see a calm, friendly message.

## Intended Surface / Boundary

Affected: Diary/Bernie side panel (docs/diary/diary.js). Specifically: renderBernieReview, stageBernieCandidateForReview, and confirmation error handling. No change to nearby surfaces (the main diary grid, break modal, or appointment create/edit modal).

## Out Of Scope

No backend modifications, database changes, new API routes, or updates to other side panels/taskpanes.

## Files I Expect To Edit

docs/diary/diary.js (UI logic, buttons, block-list rendering, error messages), docs/diary/diary.css (Optional styling), review/test_diary_smoke.py (Route-intercepted tests for back button, friendly error, and dev diagnostics)

## Implementation Steps

1. Add helper to resolve practitioner name. 2. For block code missing_practitioner_id, if name is resolved, display friendly message and hide raw code prefix. 3. In confirmation_ready, append a 'Choose different time' button. 4. Reset index/preview, load diary and reload review on back button click. 5. Show calm error on confirm failure unless dev mode is active. 6. Add route-intercepted tests in review/test_diary_smoke.py.

## Visual / Behavioural Acceptance Checks

Back button click resets staged card preview and returns to candidates list. Ordinary users see calm error message and no raw Missing Practitioner Id prefix. Developers see full setup diagnostics on error.

## Risks / Ambiguities

No significant risks. Resetting candidate index/staged preview on back-click is localized to the frontend and fully deterministic.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
