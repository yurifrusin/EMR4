# plan-antigravity-antigravity-sprint97-bernie-ui-readiness

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint97-bernie-ui-readiness` |
| Status | pending_plan_review |
| Created | 2026-07-01 09:43 +1000 |
| Source HEAD | `028e2a0` |

## Plan Summary

Sprint 97 Bernie UI readiness and honest failure UX

## My Understanding

Plan the diary UI adjustments needed so Bernie feels like a calm and helpful receptionist assistant while honestly handling interpreter readiness, deterministic fallback, candidate selection, and confirm-only booking. The UI must avoid exposing scary internal terminology (such as 'candidate slots', 'uuid', 'supervised booking') to ordinary practice staff.

## Intended Surface / Boundary

Diary UI Bernie Sidebar Panel (#bernie-review-panel, #bernie-review-content), Proposed Appointment Card on the Diary Grid (.bernie-staged-booking-card), and related styles in diary.css. Nearby surfaces (such as the main waiting-room sidebar, existing booked appointment cards, break modals, and header/location controls) must remain unchanged.

## Out Of Scope

Any production code modifications to docs/diary/diary.js, docs/diary/diary.css, docs/diary/diary.html, or review/test_diary_smoke.py during this planning phase. Backend route changes, database migrations, phone integrations, Medicare integrations, taskpane, or direct database booking writes without staff confirmation.

## Files I Expect To Edit

docs/diary/diary.js (to implement copy mapping, status copy, and debug-conditional error messages); docs/diary/diary.css (to implement styling for loading, preview cards, error fallbacks, and developer-only diagnostics); docs/diary/diary.html (if needed); review/test_diary_smoke.py (to add test cases for fallback states, developer-only error indicators, and keyboard confirmation behaviors)

## Implementation Steps

1. Draft and map the exact user-facing copy strings for BERNIE_STATUS_COPY, BERNIE_HEADLINE_COPY, and bernieReviewActionCopy. 2. Update loading indicator rendering to disable input field during search execution. 3. Update error rendering functions to display a receptionist-friendly message: 'Bernie is temporarily unavailable. Please book this appointment manually on the diary grid.' 4. Map detailed technical info inside a developer-only diagnostic container visible only when bernie_debug=true or bernie_dev_review=true is active. 5. Write tests in review/test_diary_smoke.py to verify fallback states, developer-only error indicators, and keyboard confirmation constraints.

## Visual / Behavioural Acceptance Checks

- Receptionist panel does not show snake_case codes, raw UUIDs, or tech stack traces in ordinary mode. - When bernie_debug=true or bernie_dev_review=true is active, developer diagnostics are visible. - Staged proposed appointment card gently pulses and displays patient, duration, and practitioner names without raw IDs. - Available times list displays 'Show on diary' buttons. - Pytest passes with new assertions.

## Risks / Ambiguities

- Identifying all possible backend failure code combinations to ensure none leak as raw strings. - Keyboard event listening for Control+Alt+Enter must not conflict with standard input fields or other browser shortcuts.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
