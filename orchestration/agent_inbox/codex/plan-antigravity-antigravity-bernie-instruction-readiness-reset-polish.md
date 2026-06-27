# plan-antigravity-antigravity-bernie-instruction-readiness-reset-polish

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-bernie-instruction-readiness-reset-polish` |
| Status | pending_plan_review |
| Created | 2026-06-28 08:10 +1000 |
| Source HEAD | `9a80bfb` |

## Plan Summary

Bernie selected-appointment instruction readiness and reset polish

## My Understanding

Provide a clear ready-to-submit state display when instructions are entered/selected on the Bernie selected-appointment interface, ensuring staff realize no booking has yet been processed. Reset the input, instruction, and interpreter state dynamically when Change is clicked, current appointment is re-imported, or context becomes stale (different appointment selected or selection cleared).

## Intended Surface / Boundary

Affected boundary: The Bernie Supervised Review Sidebar Panel (#bernie-review-panel), specifically the instruction input container element (#bernie-instruction-container) inside #bernie-review-content, the new status copy element (#bernie-instruction-status-copy), and context buttons (btn-bernie-context-change, btn-bernie-use-selected, and manual submit). Nearby surfaces that must not change: The main diary grid columns/slots, the Waiting Room Sidebar Panel (#diary-flow-panel), the break edit modal, and booking edit modal.

## Out Of Scope

Backend routes/schemas/models, database migrations, LLM/Gemini API calls, autonomous booking actions, browser storage/URL query parameter persistence for instructions (except smoke review fixtures), taskpane, and Command Centre.

## Files I Expect To Edit

docs/diary/diary.js, docs/diary/diary.html, docs/diary/diary.css, review/test_diary_smoke.py

## Implementation Steps

1. Add #bernie-instruction-status-copy element inside renderBernieInstructionInput. 2. Implement updateInstructionStatusCopy helper to show/hide readiness message based on textarea text. 3. Hook updateInstructionStatusCopy to textarea 'input' and suggestion chip click events. 4. Reset bernieInstructionText and bernieInterpretResult in btn-bernie-use-selected click handler (re-import). 5. Reset bernieInstructionText and bernieInterpretResult in manual submit event handler. 6. Detect stale context in resolveBerniePilotLaunchRequest and reset bernieInstructionText/bernieInterpretResult. 7. Add CSS styling for .bernie-instruction-status-copy. 8. Bump diary.js version in diary.html. 9. Update review/test_diary_smoke.py to assert the presence and text of the new readiness copy, and verify the reset behavior. 10. Run check_frontend_versions.py, syntax check, and pytest.

## Visual / Behavioural Acceptance Checks

1. With active appointment, typing or choosing a chip displays: 'Instruction ready for analysis. Submit to generate a booking proposal for staff review. No booking will be confirmed without your explicit approval.' 2. Clicking 'Change' clears context and instruction/readiness copy. 3. Re-importing context clears existing instructions and status copy. 4. Clicking another appointment or clearing selection triggers stale block and resets instructions.

## Risks / Ambiguities

Stale detection resetting instruction text while user is in the middle of typing: mitigated because stale detection only triggers when the active appointment is changed (clicked) or cleared, which is an explicit staff action.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
