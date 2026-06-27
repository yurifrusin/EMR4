# plan-antigravity-antigravity-bernie-context-readiness-summary

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-bernie-context-readiness-summary` |
| Status | pending_plan_review |
| Created | 2026-06-27 22:45 +1000 |
| Source HEAD | `2e4cd6a` |

## Plan Summary

Improve Bernie pilot panel context readiness and selection summary

## My Understanding

Ensure instruction input is disabled until context is ready, show a compact non-PHI context summary throughout instruction/confirm states, and add a Change action to clear context.

## Intended Surface / Boundary

Bernie Supervised Review Sidebar Panel (#bernie-review-panel). No changes to nearby surfaces like the diary grid, booking slots, or modals.

## Out Of Scope

Backend changes, LLM provider logic, taskpane, persistence of context, SMS/billing.

## Files I Expect To Edit

docs/diary/diary.js, docs/diary/diary.css, review/test_diary_smoke.py

## Implementation Steps

1. Style context summary and disabled textarea in CSS. 2. Implement renderBernieContextSummary in diary.js showing patient/practitioner name/time or fallback IDs and a Change/clear button. 3. Disable instruction input in renderBernieInstructionInput when context not ready. 4. Prepend summary in loadBernieLiveReview, renderBernieReview, renderBernieInterpretOnly. 5. Add/update tests in test_diary_smoke.py.

## Visual / Behavioural Acceptance Checks

Instruction inputs are disabled when context is not ready. Valid selected appointment or manual context enables inputs and displays name/time/practitioner. The summary persists in instruction and confirmation states. Clicking Change clears context and resets state.

## Risks / Ambiguities

Ensure checking context readiness doesn't break smoke/dev default mock values in existing tests.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
