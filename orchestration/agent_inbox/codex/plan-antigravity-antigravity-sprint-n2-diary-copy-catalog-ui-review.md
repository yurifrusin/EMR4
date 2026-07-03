# plan-antigravity-antigravity-sprint-n2-diary-copy-catalog-ui-review

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint-n2-diary-copy-catalog-ui-review` |
| Status | integrated |
| Created | 2026-07-03 20:08 +1000 |
| Source HEAD | `0d112ef` |

## Plan Summary

UI lane plan to consume typed backend schedule explanation reason codes and copy catalog without fragile message inference.

## My Understanding

Currently, docs/diary/diary.js infers detailed copy for schedule issues (like roster unavailable vs outside clinic hours) by scanning blocks/warnings lists for hardcoded warning codes (e.g. no_practitioner_schedule). With Sprint N2, the backend diary domain will expose structured reason_codes and a copy catalog. The UI needs to consume these typed outputs cleanly via a copy catalog lookup dictionary mapping (state, reason_code) to status/headline/action copy, with robust backend-provided and legacy default fallbacks.

## Intended Surface / Boundary

Bernie review panel in docs/diary/diary.js (functions: bernieReviewTransition, bernieStatusCopyForPayload, bernieHeadlineCopyForPayload, bernieReviewActionCopy, renderBernieReviewPanel). Nearby surfaces like the diary grid and waiting room must not change. Mock/tests in review/test_diary_smoke.py.

## Out Of Scope

No backend code edits, no write-path changes, no visual layout changes, no persisted sessions, no auto-mode.

## Files I Expect To Edit

docs/diary/diary.js, review/test_diary_smoke.py

## Implementation Steps

1. Define DIARY_COPY_CATALOG dictionary in diary.js mapping (state, reason_code) combinations to custom status, headline, and action text. 2. Update bernieReviewTransition to extract reason_codes or primary reason_code from reception_policy/explanation. 3. Update copy extraction functions (status, headline, action copy) to resolve via the catalog, falling back to backend-provided values or legacy state defaults. 4. Refactor renderBernieReviewPanel empty state logic to use the resolved copy. 5. Update smoke test fixtures/mocks in test_diary_smoke.py. 6. Add smoke test assertions for each reason code.

## Visual / Behavioural Acceptance Checks

1. Roster unavailable/no slots states render specific friendly copy for all reason codes (practitioner_day_off, fully_booked, breaks_only, outside_hours, elapsed_same_day, searched_no_candidates). 2. No logically false copy (like stale warnings) is shown. 3. Pytest review/test_diary_smoke.py passes cleanly.

## Risks / Ambiguities

1. Exact backend JSON property naming from Claude's task (e.g. reception_policy.reason_codes vs explanation) must match. Mitigated by defense-in-depth fallbacks: backend copy -> local catalog lookup -> legacy defaults. 2. Deployment synchronization. Mitigated by mock-based offline verification.

## Codex Plan Review

- Review result: Accepted by Ariadne as the N2 UI/copy-catalog consumption
  lane, now that the backend schedule reason-code contract exists.
- Required changes before implementation: Consume typed reason codes/copy in
  the Bernie review panel only; avoid visual redesign, route/write changes, and
  fragile message sniffing. Preserve legacy fallbacks.
- Approved to proceed: completed and integrated in Sprint N2.
