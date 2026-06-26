# plan-antigravity-antigravity-diary-audit-history-testid-hardening

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-diary-audit-history-testid-hardening` |
| Status | pending_plan_review |
| Created | 2026-06-26 18:29 +1000 |
| Source HEAD | `49cc096` |

## Plan Summary

Harden the diary audit history section with stable data-testid attributes in HTML and JS, and update pytest smoke tests to assert using these data-testid hooks.

## My Understanding

Currently, review/test_diary_smoke.py relies on general selectors like .booking-audit-item and searches for text content. By introducing stable data-testid hooks on the audit elements, we make frontend testing deterministic and resilient.

## Intended Surface / Boundary

Booking audit history section in docs/diary/diary.html inside the appointment edit modal.

## Out Of Scope

Backend schema or API mutations, write operations from the audit history panel.

## Files I Expect To Edit

docs/diary/diary.html, docs/diary/diary.js, review/test_diary_smoke.py

## Implementation Steps

1. Add data-testid attributes to audit elements. 2. Update test assertions in review/test_diary_smoke.py to use data-testid locators. 3. Verify tests pass.

## Visual / Behavioural Acceptance Checks

Verify pytest review/test_diary_smoke.py passes successfully.

## Risks / Ambiguities

None expected.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
