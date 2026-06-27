# plan-antigravity-antigravity-bernie-pilot-review-ergonomics

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-bernie-pilot-review-ergonomics` |
| Status | integrated |
| Created | 2026-06-27 21:14 +1000 |
| Source HEAD | `1a1601d` |

## Plan Summary

Refine wording and ergonomics of the Bernie pilot panel to read clearly as supervised staff actions.

## My Understanding

Refining the labels, placeholders, titles, badges, confirmation checkbox, and status messages in the Bernie review panel to explicitly reflect staff supervision and action.

## Intended Surface / Boundary

The Bernie review panel (#bernie-review-panel). Grid, modals, and other panels remain unchanged.

## Out Of Scope

Backend changes, DB schemas, persistent state, billing, SMS, autonomous booking, taskpane, or other features.

## Files I Expect To Edit

docs/diary/diary.js, docs/diary/diary.css, docs/diary/diary.html, review/test_diary_smoke.py

## Implementation Steps

1. Update renderBerniePilotContextForm labels and statuses in diary.js. 2. Update renderBernieInstructionInput text in diary.js. 3. Refine badges and headlines in renderBernieReview in diary.js. 4. Refine checkbox, confirm button, and success/error messages in diary.js. 5. Adjust css if needed. 6. Update test assertions in test_diary_smoke.py. 7. Bump version suffix in diary.html.

## Visual / Behavioural Acceptance Checks

Correct headers, badges, button texts, checkboxes display cleanly; test suite passes.

## Risks / Ambiguities

Text wrapping in 320px panel; test selector / assertion breakage.

## Codex Plan Review

- Review result: accepted; implementation released to Antigravity.
- Required changes before implementation: keep copy supervised/staff-confirmed, avoid implying autonomous booking, and preserve selectors unless tests are updated.
- Approved to proceed: yes
