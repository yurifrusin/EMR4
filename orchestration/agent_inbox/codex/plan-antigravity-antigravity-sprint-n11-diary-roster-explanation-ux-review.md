# plan-antigravity-antigravity-sprint-n11-diary-roster-explanation-ux-review

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint-n11-diary-roster-explanation-ux-review` |
| Status | integrated |
| Created | 2026-07-04 04:38 +1000 |
| Source HEAD | `a555434` |

## Plan Summary

Sprint N11 implementation plan for Diary roster explanation UX review

## My Understanding

Consuming backend-derived typed outcome classifications directly in the Bernie review panel to render status, headline, and actions cleanly without client-side copy guessing, avoiding false no-slot copy, preventing advisory warnings from blocking, preserving stale conflicts, and asserting no PHI in storage.

## Intended Surface / Boundary

Bernie review content panel #bernie-review-content in docs/diary/diary.js, leaving surrounding diary grid and controls untouched.

## Out Of Scope

No production code changes during the plan gate; no backend schema edits; no database migrations; no GraphRAG or vector search.

## Files I Expect To Edit

docs/diary/diary.js, review/test_diary_smoke.py

## Implementation Steps

1. Attach data.outcome to payload in fetch blocks. 2. Update getPrimaryScheduleReasonCode to check payload.outcome.reason_codes first. 3. Adjust bernieReviewTransition to prevent coercing advisory_warnings_present to blocked. 4. Clamp isBernieConfirmReady to require selected_slot. 5. Add deterministic smoke tests for outcomes, stale conflict, and storage PHI check.

## Visual / Behavioural Acceptance Checks

Verify pytest review/test_diary_smoke.py runs cleanly and asserts roster copy, warning non-blocking behavior, stale banner presence, and complete lack of PHI in localStorage/sessionStorage.

## Risks / Ambiguities

Minimal risk as fallback checks are fully preserved for legacy backend payloads.

## Codex Plan Review

- Review result: Accepted with Ariadne amendments. Implemented as part of Sprint N11.
- Required changes before implementation: Ensure advisory-only states without selected-slot evidence do not become generic blocked states, and keep confirm visibility evidence-gated.
- Approved to proceed: yes
