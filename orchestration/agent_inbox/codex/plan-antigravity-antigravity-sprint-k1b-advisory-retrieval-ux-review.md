# plan-antigravity-antigravity-sprint-k1b-advisory-retrieval-ux-review

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint-k1b-advisory-retrieval-ux-review` |
| Status | integrated |
| Created | 2026-07-04 05:30 +1000 |
| Source HEAD | `db65373` |

## Plan Summary

Plan visible Diary/Bernie UX for practice knowledge advisory retrieval facts with professional copy, provenance boundaries, and strict non-authority constraints.

## My Understanding

EMR4 Sprint K1b coordinates the UI layer for the typed practice knowledge substrate built in Sprint K1. The goal is to safely expose retrieved practice facts (roster, policy, contact, opening hours, reception guidance) in the Diary's Bernie review and chat panels. The UI must present these facts professionally with complete provenance, while keeping them strictly advisory-only: retrieval results cannot create mock slots, change policy blocks, or grant confirmation/candidate/no-slot authority.

## Intended Surface / Boundary

The affected surface is exclusively the Bernie panel in the Diary UI: docs/diary/diary.js (for parsing and rendering), docs/diary/diary.css (for professional fact card styles), and review/test_diary_smoke.py (for mocking and asserting behavior). Surrounding surfaces (the main diary grid, booking modals, and the write confirm flow) must remain unaffected.

## Out Of Scope

Backend GraphRAG/vector search implementation, DB schema changes or migrations, any auto-booking or mutation without human staff approval, and any change to the Command Centre / Word Taskpane.

## Files I Expect To Edit

docs/diary/diary.js, docs/diary/diary.css, review/test_diary_smoke.py

## Implementation Steps

1. Parse advisory_warning frames with basis='practice_knowledge_retrieval' from backend response reception_context in both interpret-booking-instruction and supervised-booking. 2. Render retrieved facts inside a dedicated container in the Bernie Review Panel with cool teal borders and professional copy. 3. Include collapsible provenance detail blocks showing source, status, and author. 4. Expose fact references inside Bernie chat bubbles when associated with the latest conversation turns. 5. Add custom CSS styles for fact cards and details layout. 6. Write automated smoke checks in pytest validating that facts display correctly and that they do not influence availability or confirm button state.

## Visual / Behavioural Acceptance Checks

1. Matched facts render in a left-bordered teal card with professional header 'Practice Reference'. 2. Provenance block is visible and correctly formatted. 3. Confirm button status and available times lists are completely unaffected by retrieval frames. 4. Rerun all pytest smoke tests clean.

## Risks / Ambiguities

None. The scope is narrow and strictly presentational. Ensuring details drawer is responsive in a narrow sidebar is the main design check.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: yes - integrated by Ariadne in Sprint K1b
