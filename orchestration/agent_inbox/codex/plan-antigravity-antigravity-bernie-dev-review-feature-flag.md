# plan-antigravity-antigravity-bernie-dev-review-feature-flag

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-bernie-dev-review-feature-flag` |
| Status | pending_plan_review |
| Created | 2026-06-27 04:14 +1000 |
| Source HEAD | `a40cf97` |

## Plan Summary

Dev-mode query flag for Bernie supervised booking review

## My Understanding

Expose the supervised Bernie review/confirm workflow in the ordinary (non-smoke) diary dev mode, controlled by a query parameter/feature flag bernie_review=live in the URL. In this mode, the panel will call the live backend endpoint to retrieve and confirm booking proposals, while in automated tests these calls will be route-intercepted to prevent live writes. Default non-smoke mode without the flag will remain hidden with no calls made, and existing smoke behaviour will be preserved.

## Intended Surface / Boundary

The Bernie review sidebar panel (#bernie-review-panel) inside the diary taskpane. Nearby surfaces like the diary grid, booking slots, cards, and modal windows must remain unchanged.

## Out Of Scope

Backend routes/schemas, live autonomous booking, production default exposure, real API writes in tests, taskpane, Command Centre, migrations, patient/resource admin, billing, SMS, broad diary redesign, and unrelated style refactors.

## Files I Expect To Edit

docs/diary/diary.js, docs/diary/diary.html, review/test_diary_smoke.py

## Implementation Steps

1. In docs/diary/diary.js, update initBernieReview() guard to allow reviewParam === 'live' when isSmoke is false. 2. Update isConfirmAdapter to be true when in non-smoke dev mode (isSmoke is false and reviewParam is 'live'), enabling live POST calls on confirm. 3. Update load/init listener at the bottom to call initBernieReview() when isSmoke is true or reviewParam is 'live'. 4. In docs/diary/diary.html, increment diary.js version to v=108. 5. In review/test_diary_smoke.py, update the test_bernie_live_confirm_flow_harness_no_normal_mode_exposure test to load the page without any query parameter to prove default non-exposure and no calls. 6. Add test_bernie_dev_mode_review_feature_flag_success in review/test_diary_smoke.py to verify that bernie_review=live shows the panel and executes intercepted confirm call.

## Visual / Behavioural Acceptance Checks

1. Default ordinary mode (no query flags) has the Bernie panel hidden and makes no supervised-booking calls. 2. Passing bernie_review=live in ordinary dev mode displays the panel and triggers the supervised-booking API call. 3. The confirmation approval checkbox/button gating works, and clicking confirm triggers the confirm-bernie API call. 4. Intercepting these requests in tests ensures no live writes occur, and all existing smoke test cases remain fully functional.

## Risks / Ambiguities

Playwright tests require accurate route interception to ensure no live backend calls leak. We mitigate this by using strict Playwright page routing patterns.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
