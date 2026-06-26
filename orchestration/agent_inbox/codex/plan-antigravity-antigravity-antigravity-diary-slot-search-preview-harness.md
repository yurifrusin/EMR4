# plan-antigravity-antigravity-antigravity-diary-slot-search-preview-harness

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-antigravity-diary-slot-search-preview-harness` |
| Status | pending_plan_review |
| Created | 2026-06-26 20:46 +1000 |
| Source HEAD | `e1ec8a4` |

## Plan Summary

Plan for deterministic read-only slot-search proposal preview harness

## My Understanding

Add a read-only slot-search proposal preview to the diary grid to lay the foundation for future Bernie scheduling features, using smoke mode mocks and Playwright check assertions.

## Intended Surface / Boundary

EMR4 Diary grid interface and review tests; nearby surfaces (booking modal, actual appointments) remain unchanged.

## Out Of Scope

Live backend APIs, DB writes, appointment mutations, LLM/voice integration.

## Files I Expect To Edit

docs/diary/diary.js, docs/diary/diary.css, review/checks_diary.json, review/test_diary_smoke.py

## Implementation Steps

1. Define mock slot-search proposal candidates in diary.js. 2. Render these candidate slots on the columns in smoke mode. 3. Style them as dashed/semi-transparent and non-interactive. 4. Add Playwright tests to checks_diary.json or test_diary_smoke.py to verify rendering and non-interactivity.

## Visual / Behavioural Acceptance Checks

Preview slots render visually on columns, do not open booking modals on click, and pytest runs pass cleanly.

## Risks / Ambiguities

Conflict with existing break/appointment blocks (mitigated by using empty slot times).

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
