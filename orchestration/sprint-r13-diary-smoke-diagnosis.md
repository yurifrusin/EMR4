# Sprint R13-A DeepSeek Diary Smoke Failure Diagnosis

| Item | Value |
|---|---|
| Author | DeepSeek Flash via Codex worker |
| Branch | codex/sprint-r13-diary-smoke-diagnosis |
| Status | Plan gate - diagnosis complete, awaiting implementation approval |
| Test run | 2026-07-05 at 19:52 (pytest --tb=short --junitxml=review/diary-review.xml) |

## Summary

**Root cause: single stale harness assumption.** All 12 failures share one
root cause: the test harness sets
`localStorage.setItem("emr4_token", "ordinary-staff-token")`, which is NOT
a valid JWT. The diary JS function `isTokenExpired()` returns `true` because
`"ordinary-staff-token".split(".")` yields length 1, not 3, triggering
`clearExpiredAuthToken()` which sets `token = null`.

This was introduced when `isTokenExpired` was added to `diary.js`
(at `docs/diary/diary.js:2460-2472`) but the harness token was never
updated to match.

Two downstream failure modes:

### Failure Mode A - Session append capture (3 tests)

Navigate with `?smoke=true` and `bernie_session=true`. Because token = null:
- `shouldUseBernieServerSession()` returns false
- Server session init never runs
- `/api/v1/appointments/bernie/sessions/active` never called
- `assert active_requests` fails on empty list

### Failure Mode B - Grid/pilot not visible on non-smoke URLs (9 tests)

Navigate to bare `/diary/diary.html` (no `?smoke=true`). Because token = null:
- `loadDiary()` returns early - grid never renders
- `checkBerniePilotEligibility()` returns early
- Tests waiting for `#diary-grid` or pilot button time out

## Failing Test Details

### Group A - Session append empty (3)

| # | Test name | Assertion |
|---|---|---|
| 1 | test_bernie_session_endpoint_active_load_and_phi_minimized_append | assert active_requests |
| 2 | test_bernie_session_stale_conflict_disables_confirm_until_refresh | assert append_requests |
| 3 | test_bernie_route_calls_carry_server_session_coordinates_and_binding | assert append_requests |

### Group B - Grid/pilot not visible (9)

| # | Test name | Timeout selector | URL |
|---|---|---|---|
| 4 | test_bernie_pilot_ordinary_mode_requires_real_context | pilot-launch-button | /diary/diary.html |
| 5 | test_bernie_pilot_ordinary_mode_explicit_context_posts_and_confirm_gated | #diary-grid | /diary/diary.html |
| 6 | test_bernie_pilot_imported_context_stales_when_selection_changes | pilot-launch-button | /diary/diary.html |
| 7 | test_bernie_pilot_selected_appointment_instruction_affordances | #diary-grid | /diary/diary.html |
| 8 | test_bernie_pilot_blocks_interpreted_practitioner_mismatch_before_supervised_call | #diary-grid | /diary/diary.html |
| 9 | test_bernie_pilot_instruction_first_without_selected_appointment | instruction-input | /diary/diary.html |
| 10 | test_bernie_candidate_click_stages_provisional_diary_preview | #diary-grid | ?bernie_auto_preview=false |
| 11 | test_bernie_route_intercepted_selected_slot_can_return_to_candidates | cascade (no grid) | ?bernie_auto_preview=false |
| 12 | test_bernie_pilot_selected_appointment_instruction_readiness_and_resets | #diary-grid | /diary/diary.html |

## Classification

| Category | Count | Detail |
|---|---|---|
| Stale harness assumption | 12 of 12 | ordinary-staff-token is not a valid JWT; never updated when isTokenExpired was added |
| Real regression | 0 | No production behaviour changed |
| Fixture state issue | 12 of 12 | The harness token value is the sole problem |
| Environment issue | 0 | Not infrastructure or network-related |

## Recommended Repair

**Single-point fix in `review/test_diary_smoke.py`:**
Replace `"ordinary-staff-token"` with a valid dummy JWT that passes `isTokenExpired()`.

Recommended value: `eyJhbGciOiJIUzI1NiJ9.e30.c2ln`

Decoded: header=`{"alg":"HS256"}`, payload=`{}` (no `exp` -> returns false).

**13 occurrences** to update (all `setItem("emr4_token", ...)` calls).

## Before-and-after diff

```diff
- localStorage.setItem("emr4_token", "ordinary-staff-token")
+ localStorage.setItem("emr4_token", "eyJhbGciOiJIUzI1NiJ9.e30.c2ln")
```

Zero production code changes. Zero test deletions. Zero selector changes.

## Verification Commands

Full diary smoke (expect 58 passed, 0 failed):
```
.venv\Scripts\pytest.exe review\test_diary_smoke.py -q --tb=short
```
R12 reason-code focused (expect 7 passed):
```
.venv\Scripts\pytest.exe review\test_diary_smoke.py -q --tb=short -k reason_code
```
JS syntax and whitespace:
```
node --check docs\diary\diary.js
git diff --check
```

## Risks

- 14th coincidental user (`test_bernie_ordinary_mode_readiness_and_diagnostics`)
  also uses the fake token but passes via `?smoke=true` without session features.
  Fix it for consistency (no pass/fail impact).
- If `isTokenExpired` logic changes to require `exp`, harness needs updating.
  Unlikely but noted.
- No `Authorization` header sent to real backends (diary runs offline via
  Playwright route interception).
