# plan-codex-codex-sprint-r14-deepseek-auth-bootstrap-guard

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `master` |
| Source Task | `codex-sprint-r14-deepseek-auth-bootstrap-guard` |
| Status | integrated |
| Created | 2026-07-05 20:11 +1000 |
| Source HEAD | `e648405` |

## Plan Summary

Add reusable Diary smoke harness auth bootstrap guard so invalid dummy JWT drift fails with clear assertion instead of selector timeouts

## My Understanding

The smoke harness defines REVIEW_AUTH_TOKEN at module scope but validates nothing about its JWT structure. 13 inline evaluate(setItem) calls string-interpolate it into the browser. If the token drifts (e.g. missing parts, non-base64, unparseable payload), those calls silently set broken localStorage and downstream failures manifest as selector timeouts rather than a clear auth error.

## Intended Surface / Boundary

review/harness.py only for new auth helpers; review/test_diary_smoke.py for helper imports and token-set call replacements. No production code changes.

## Out Of Scope

Backend routes/schemas, diary.js, template fixtures, Office/GitHub Pages/Gemini calls, weakening/removing assertions, CI workflow edits, checks_diary.json schema.

## Files I Expect To Edit

review/harness.py (add assert_valid_review_token, bootstrap_auth, clear_auth), review/test_diary_smoke.py (add module-level validation call, replace inline evaluate calls with helpers)

## Implementation Steps

1. Add assert_valid_review_token(token_str) to harness.py - validates 3 dot-separated parts, valid base64url, parsable JSON payload. 2. Add bootstrap_auth(page, token_str) to harness.py - asserts valid token, then evaluate-set into localStorage. 3. Add clear_auth(page) to harness.py - evaluate-removes from localStorage. 4. Add module-level assert_valid_review_token(REVIEW_AUTH_TOKEN) to test_diary_smoke.py. 5. Replace all 13 evaluate setItem emr4_token calls with bootstrap_auth calls. 6. Replace all evaluate removeItem emr4_token calls with clear_auth calls. 7. Run pytest and git diff --check. 8. Report results.

## Visual / Behavioural Acceptance Checks

Running pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q produces all-green; invalid token change e.g. removing a dot produces a clear Python assertion on import, not browser timeout; git diff --check passes; no production code changes.

## Risks / Ambiguities

The current REVIEW_AUTH_TOKEN has valid JWT structure (3 parts, base64 parses, payload is {}). If a future test needs a deliberately malformed token for negative testing, the module-level assertion would need conditional bypass - out of scope until that arises.

## Codex Plan Review

- Review result: Accepted and implemented by Ariadne in the integration worktree.
- Required changes before implementation: None.
- Approved to proceed: yes; implemented and verified.
