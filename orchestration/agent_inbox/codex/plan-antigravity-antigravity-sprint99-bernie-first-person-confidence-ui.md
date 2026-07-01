# plan-antigravity-antigravity-sprint99-bernie-first-person-confidence-ui

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint99-bernie-first-person-confidence-ui` |
| Status | pending_plan_review |
| Created | 2026-07-01 16:56 +1000 |
| Source HEAD | `0ffeb20` |

## Plan Summary

Plan receptionist-facing Bernie UI response layer for confidence-aware booking, using first-person copy, Details disclosure for high confidence evidence, and auto-previewing the most-likely slot on the diary grid with loop suppression.

## My Understanding

We need to update the Bernie receptionist-facing UI to support first-person assistant copy, showing inferred-date alerts, typo-resolved practitioner prompts, and patient candidate clarifications. We will also implement a Details disclosure toggle for high-confidence evidence, auto-preview the most-likely candidate slot on the grid when confidence permits (with loop suppression when the selection is reset), ensure no raw snake_case text is displayed, and verify no writes occur before confirmation.

## Intended Surface / Boundary

The Bernie pilot review panel (docs/diary/diary.html, diary.js, diary.css), staged booking previews on the diary grid columns, and the test review suite (review/test_diary_smoke.py). Adjacent surfaces such as waiting areas or non-Bernie booking modals must not change.

## Out Of Scope

Production code edits (plan-only phase), backend database schema changes, live phone/Caller ID/Medicare integrations, and bypassing explicit staff confirmation.

## Files I Expect To Edit

docs/diary/diary.js, docs/diary/diary.css, docs/diary/diary.html, review/test_diary_smoke.py

## Implementation Steps

1. Refactor copy in diary.js to use first-person copy ('I\\'ve assumed today...', 'Do you mean...', 'I need one more detail...'). 2. Implement details disclosure using the HTML <details> element for high-confidence evidence and expanded view for low-confidence. 3. Implement auto-preview of the first slot candidate when confidence is high, and track a suppression flag when the user explicitly clicks 'Choose another time'. 4. Style the disclosure elements in diary.css. 5. Add route-intercepted smoke tests in test_diary_smoke.py.

## Visual / Behavioural Acceptance Checks

1. Smoke tests in review/test_diary_smoke.py verify inferred today, typo practitioner, ambiguous patient candidates, Details toggle behavior, and no writes before confirmation. 2. Manual/smoke mode check shows the first candidate slot is automatically previewed on the grid when confidence is high, and suppresses auto-preview when 'Choose another time' is clicked. 3. No raw snake_case is visible.

## Risks / Ambiguities

API contract dependency on Workstream FA (Claude Code). If backend contract fields for inferred fields or typo-resolved practitioners differ, the UI parsing will need to align with Claude\\'s contract.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
