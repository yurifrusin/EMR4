# plan-antigravity-antigravity-sprint-v1-diary-bernie-voice-and-intent-ux-review

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint-v1-diary-bernie-voice-and-intent-ux-review` |
| Status | integrated |
| Created | 2026-07-04 05:54 +1000 |
| Source HEAD | `98d3143` |

## Plan Summary

Plan for friendly professional Bernie voice and typed tool-intent UX including appointment extensions

## My Understanding

The goal is to design a friendly, professional voice for Bernie's UI chat and proposal reviews, while handling non-booking intents like extending an appointment. We must keep the proposal, review, and confirmation states clear and ensure audit/write boundaries are visible to the receptionist (i.e. writes are never autonomous).

## Intended Surface / Boundary

Docs/diary/diary.js (rendering logic, copy mapping, intent detection, mock fixtures), docs/diary/diary.css (styling for proposal cards, badges, and extensions), review/test_diary_smoke.py (smoke tests for the new UX states).

## Out Of Scope

Backend router/schema changes; GraphRAG retrieval changes; Taskpane/Command Centre; direct database writes from the frontend without human confirmation.

## Files I Expect To Edit

docs/diary/diary.js, docs/diary/diary.css, review/test_diary_smoke.py

## Implementation Steps

1. Introduce a refined BERNIE_VOICE_CATALOG mapping for outcome/intent friendly messages. 2. Implement intent parsing in renderBernieReview, detecting extend_appointment. 3. Adjust headline, cards, detail rows, and confirm button based on intent. 4. Visual styling for proposals (clear 'Proposed Action' banner). 5. Define mock fixture for extension proposal. 6. Write Playwright tests for the new UX paths.

## Visual / Behavioural Acceptance Checks

Visual verification of the proposal status badge showing 'Proposed Action' with warm border. Confirmation text changing dynamically. Extension card correctly rendering the current, extended, and new total durations. Automated Playwright test passing.

## Risks / Ambiguities

Slight drift in backend payload keys for intents. Mitigation: use robust optional key chaining and fallback to generic display-friendly labels.

## Codex Plan Review

- Review result: Accepted as the V2 visible Diary UX direction after V1 first landed the backend typed-intent proposal route.
- Required changes before implementation: Consume the V1 backend contract instead of inventing frontend-only intent authority.
- Approved to proceed: deferred to Sprint V2
