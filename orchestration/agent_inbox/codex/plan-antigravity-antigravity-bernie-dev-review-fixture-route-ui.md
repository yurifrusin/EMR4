# plan-antigravity-antigravity-bernie-dev-review-fixture-route-ui

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-bernie-dev-review-fixture-route-ui` |
| Status | pending_plan_review |
| Created | 2026-06-27 05:29 +1000 |
| Source HEAD | `e9af07f` |

## Plan Summary

Fetch backend dev fixtures instead of frontend mocks when bernie_dev_review=true

## My Understanding

Expose backend-defined deterministic review fixtures by calling GET /api/v1/appointments/dev/bernie-review-fixtures when in dev review mode (bernie_dev_review=true). Fall back to in-browser mocks if bernie_dev_review is not true but smoke=true is set to support offline smoke checks.

## Intended Surface / Boundary

docs/diary/diary.js (initBernieReview) and docs/diary/diary.html (version bump). Visual panels like the diary grid, waiting room, and modals are unaffected.

## Out Of Scope

Backend changes, live writes, live autonomous booking, taskpane, migrations, resource admin, and unrelated refactors.

## Files I Expect To Edit

docs/diary/diary.js, docs/diary/diary.html, review/test_diary_smoke.py

## Implementation Steps

1. Update initBernieReview in docs/diary/diary.js to fetch GET /api/v1/appointments/dev/bernie-review-fixtures?state=<state> when devReviewParam === 'true'. 2. Maintain local mock fallback when smoke=true but devReviewParam !== 'true'. 3. Bump asset version in docs/diary/diary.html to diary.js?v=110. 4. Implement Playwright test coverage in review/test_diary_smoke.py with route interception.

## Visual / Behavioural Acceptance Checks

1. Loading ?bernie_dev_review=true without bernie_review makes no backend calls on load. 2. Loading ?bernie_dev_review=true&bernie_review=blocked fetches GET /api/v1/appointments/dev/bernie-review-fixtures?state=blocked and renders Blocked headline. 3. Clicking Confirm Booking triggers confirm POST only after explicit checkbox approval and is route-intercepted.

## Risks / Ambiguities

Backend connection failures are mitigated by falling back to frontend mocks when the dev flag is absent. We must ensure the API response structure is correctly parsed.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
