# plan-codex-codex-sprint-r13-deepseek-diary-smoke-focused-fix

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/sprint-r13-diary-smoke-focused-fix` |
| Source Task | `codex-sprint-r13-deepseek-diary-smoke-focused-fix` |
| Status | integrated |
| Created | 2026-07-05 19:58 +1000 |
| Source HEAD | `b49407b` |

## Plan Summary

Fix 12 pre-existing Bernie session/pilot full-smoke test failures: Group A race condition async waits, Groups B/C API fixture diagnosis and minimal repair

## My Understanding

Three failure groups identified from diary-review.xml. Group A (3 tests) is a race condition: loadBernieLiveReview calls ensureServerSession() without await (diary.js:5862), test asserts async request lists before they populate. Groups B/C (9 tests) navigate without ?smoke=true and use route interception; diary grid stays hidden, likely from unhandled API response paths falling through to catch-all. All failures pre-exist R12 reason-code changes. Fix preserves all assertions.

## Intended Surface / Boundary

review/test_diary_smoke.py primary; docs/diary/diary.js narrow guard only if proven necessary

## Out Of Scope

R12 reason-code tests, checks_diary.json, backend schema/routes, assertion weakening, broad refactors

## Files I Expect To Edit

review/test_diary_smoke.py, docs/diary/diary.js (conditional)

## Implementation Steps

1. Add wait_for_function for async request lists in 3 Group A tests 2. Diagnose Groups B/C with targeted test run and console log capture 3. Fix missing API fixture handlers or narrow diary.js guard 4. Verify all 12 tests pass, R12 tests unbroken, diff clean

## Visual / Behavioural Acceptance Checks

All 12 previously-failing tests pass; zero R12 reason-code regressions; no assertion weakened; narrow diff

## Risks / Ambiguities

Groups B/C diagnosis ambiguous until console logs captured; fallback is diary.js guard for non-smoke loadDiary error handling; Group A race-intermittent risk handled by wait_for_function polling

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no


## Completion Notes

- Ariadne implemented the accepted minimal fix directly after DeepSeek diagnosis: central `REVIEW_AUTH_TOKEN` in `review/test_diary_smoke.py` and replaced invalid fake token setup calls.
- Verification: focused 12-failure R13 cluster passed; full Diary smoke passed; R12 reason-code guard passed; `git diff --check` passed.
- No production code changed; no assertions were weakened.
