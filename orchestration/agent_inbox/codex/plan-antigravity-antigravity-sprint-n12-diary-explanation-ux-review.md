# plan-antigravity-antigravity-sprint-n12-diary-explanation-ux-review

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint-n12-diary-explanation-ux-review` |
| Status | integrated |
| Created | 2026-07-04 04:59 +1000 |
| Source HEAD | `4d95981` |

## Plan Summary

Plan visible Diary/Bernie UX for roster/schedule explanation payloads and confirm authority evidence gating

## My Understanding

Plan frontend Diary/Bernie UX refinements for consuming typed roster/schedule explanation payloads with friendly professional copy, distinct status/headlines for roster unavailability, requested window, clinic day exhausted, and true empty slots. Ensure chat history/accordion is clean for single/multiple turns. Enforce strict evidence-based confirm button & shortcut gating in the UI.

## Intended Surface / Boundary

docs/diary/diary.js (review status bar, headline, action copy, candidate slots, chat transcript, confirmation box elements). review/test_diary_smoke.py (Playwright test assertions and state/copy mocks). main diary grid is untouched.

## Out Of Scope

Backend router/schema changes, database migrations, GraphRAG retriever logic, phone/Caller ID, voice/headset integration, and persisting PHI in browser storage.

## Files I Expect To Edit

docs/diary/diary.js, review/test_diary_smoke.py

## Implementation Steps

1. Update DIARY_COPY_CATALOG with friendly, professional status/headline/action copy. 2. Refine state mapping in bernieReviewTransition so clinic_day_exhausted, roster_unavailable, and no_slots remain distinct. 3. Lock confirmBtn.disabled and shortcut trigger if confirm_payload is missing or confirm_affordance.confirm_grade_allowed is false. 4. Refine updateBernieChatTranscriptUI to hide details/accordion if there is only 1 turn. 5. Update test_diary_smoke.py tests and assertions to align.

## Visual / Behavioural Acceptance Checks

Verify by running pytest review/test_diary_smoke.py. Validate copy catalog strings are rendered correctly. Verify confirm button is disabled and shortcut blocked when confirm_grade_allowed is false.

## Risks / Ambiguities

Stale mock data: verify test suite overrides doesn't trip on missing outcome or confirm_affordance fields by implementing safe fallback defaults. No confirm bypass on legacy payloads.

## Codex Plan Review

- Review result: Accepted with Ariadne amendments.
- Required changes before implementation: Keep confirm controls evidence-gated;
  allow preview-grade selected-slot rendering without confirm-grade authority.
- Approved to proceed: yes; implemented by Ariadne.
