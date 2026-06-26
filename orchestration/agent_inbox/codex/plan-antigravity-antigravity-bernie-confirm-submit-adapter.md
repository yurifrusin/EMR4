# plan-antigravity-antigravity-bernie-confirm-submit-adapter

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-bernie-confirm-submit-adapter` |
| Status | integrated |
| Created | 2026-06-27 03:37 +1000 |
| Source HEAD | `7ae4f07` |

## Plan Summary

Add the next smoke-gated Bernie review UI slice: an explicit staff-approval submit adapter that posts the existing staff_review confirm payload only after deliberate approval, while remaining disabled in normal diary mode.

## My Understanding

Introduce an explicit submit adapter for the Bernie supervised booking review panel that POSTs the confirm_payload (with confirmed = true) to confirm_endpoint via apiFetch. This adapter should be gated behind smoke=true and a new URL query parameter bernie_confirm_adapter=true, remaining completely disabled/inactive in normal diary mode. We must also add route-intercepted smoke tests in Playwright verifying success, error handling, exact payload shape, blocked/candidate states, and proving confirm-bernie is not called before approval or in normal/non-gated mode.

## Intended Surface / Boundary

Affects the Bernie booking review panel (#bernie-review-panel, #bernie-review-content) in docs/diary/diary.js, docs/diary/diary.html, and docs/diary/diary.css. A new .bernie-error-alert block will be added in diary.css for error messages. Nearby surfaces that must not change: the main diary grid, the normal booking create/edit modal (#booking-modal), waiting room panels, and patient search panel.

## Out Of Scope

Backend routes, schema changes, database migrations, LLM parsing, normal non-smoke live diary enablement (must remain gated), and actual unintercepted database writes during testing.

## Files I Expect To Edit

- docs/diary/diary.html
- docs/diary/diary.css
- docs/diary/diary.js
- review/test_diary_smoke.py

## Implementation Steps

1. Add .bernie-error-alert styling to docs/diary/diary.css.
2. Modify docs/diary/diary.js to check if bernie_confirm_adapter=true in query parameters. If yes, clicking the confirm button will perform a POST request using apiFetch to the payload's confirm_endpoint with confirmed = true in the request body. If the request is successful, show the success message. If the request fails, show the error alert (.bernie-error-alert) with detail and allow retry.
3. Increment version numbers in docs/diary/diary.html for cache-busting.
4. Add deterministic route-intercepted tests in review/test_diary_smoke.py verifying successful submission (asserting correct payload structure), error handling (mocking 500 responses and verifying error display and retry capability), and verifying no submission occurs before approval, in blocked/candidate states, or in normal diary mode.

## Visual / Behavioural Acceptance Checks

- Inspect the review panel when confirmation ready: checkbox is present, button is disabled.
- Checking the checkbox enables the button.
- Clicking the button disables the checkbox and button.
- On success, the green success alert box appears.
- On failure, a red error alert box appears with details, and the button/checkbox are re-enabled for retry.

## Risks / Ambiguities

- CORS or network configuration issues with Playwright's route interceptions.
- Ensuring the confirm payload structure perfectly aligns with the backend expectations.
- Making sure the adapter is fully disabled and has zero side effects in normal diary mode.

## Codex Plan Review

- Review result: Accepted. Plan was narrow, smoke/feature-gated, and limited to diary review UI plus deterministic Playwright checks.
- Required changes before implementation: None.
- Approved to proceed: yes
