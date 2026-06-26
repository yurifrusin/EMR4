# plan-antigravity-antigravity-bernie-supervised-review-ui-harness

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-bernie-supervised-review-ui-harness` |
| Status | pending_plan_review |
| Created | 2026-06-27 03:03 +1000 |
| Source HEAD | `b2c6bee` |

## Plan Summary

Add deterministic UI review harness for Bernie supervised review panel

## My Understanding

Implement a deterministic client-side smoke-gated Bernie Booking Review panel and a corresponding pytest/Playwright UI review harness. This panel will display the result of the Bernie supervised booking proposal (staff_review payload) returned by the backend in Sprint 48. The three statuses to render are: blocked (displays headline, status, action required, lists block issues; confirmation is hidden); candidate_selection_required (displays headline, status, action required, lists slot candidates; confirmation is hidden); and confirmation_ready (displays selected slot details, status, action required, checkbox for explicit approval, and confirm button. Confirm button is disabled until checkbox is checked. Clicking confirm simulates booking with no live writes). Playwright tests in review/test_diary_smoke.py will load different query parameters (bernie_review=blocked, etc.) and assert DOM state using stable data-testid selectors.

## Intended Surface / Boundary

The UI surface is #bernie-review-panel, a right-sidebar panel alongside the main diary body. It is toggled visible when the bernie_review query parameter is present in smoke mode. Visually adjacent surfaces that must remain completely unchanged are: the diary header, date navigator, diary grid column slots, waiting room flow panel, and appointment creation/edit modals.

## Out Of Scope

Backend schema/models/routes, actual natural-language processing or LLM logic, real confirm-bernie database mutations/writes, billing/payment integration, SMS notifications, waiting-room flow logic, and any modifications to the core booking modal flow itself.

## Files I Expect To Edit

docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js, review/checks_diary.json, review/test_diary_smoke.py

## Implementation Steps

1. Add structural markup for #bernie-review-panel inside docs/diary/diary.html with stable data-testid attributes. 2. Add style rules for the review panel in docs/diary/diary.css adhering to existing CSS variables. 3. Define mock fixtures in docs/diary/diary.js matching the Sprint 48 staff_review payload for blocked, candidate_selection_required, and confirmation_ready. 4. Implement initialization and rendering logic in docs/diary/diary.js checking for bernie_review query parameter, rendering layout, binding checkbox listener to enable/disable button, and intercepting confirm click. 5. Add check in review/checks_diary.json to verify the panel remains hidden in default smoke mode. 6. Add three Playwright-driven test cases for blocked, candidate_selection_required, and confirmation_ready to review/test_diary_smoke.py. 7. Run test suite to verify correctness.

## Visual / Behavioural Acceptance Checks

1. Normal smoke mode: panel remains hidden. 2. bernie_review=blocked: panel displays blocked status, headline, action required, lists block issues, and hides confirmation. 3. bernie_review=candidate_selection_required: panel displays selection status, lists candidate slot summaries, and hides confirmation. 4. bernie_review=confirmation_ready: panel displays selected slot summary, unchecked checkbox, disabled confirm button. Checking checkbox enables button, unchecking disables it. Clicking enabled button shows simulated confirmation and makes zero backend writes. 5. All Playwright tests pass cleanly and emit valid JUnit XML.

## Risks / Ambiguities

Selector drift mitigated by using stable data-testid attributes for all assertions. Preventing live side effects is verified by branching on smoke mode in the event handler.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
