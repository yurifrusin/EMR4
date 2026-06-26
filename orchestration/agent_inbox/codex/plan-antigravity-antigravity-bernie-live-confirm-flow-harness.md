# plan-antigravity-antigravity-bernie-live-confirm-flow-harness

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-bernie-live-confirm-flow-harness` |
| Status | integrated |
| Created | 2026-06-27 03:54 +1000 |
| Source HEAD | `dc0e023` |

## Plan Summary

Add Playwright smoke-mode review harness proving Bernie live adapter and explicit confirm submit adapter end-to-end integration.

## My Understanding

Add tests in review/test_diary_smoke.py that route-intercept supervised-booking and confirm-bernie, loading diary.html with bernie_review=live and bernie_confirm_adapter=true to prove they work together end-to-end under route interception without enabling ordinary live diary mode. Assert that blocked/candidate/error paths do not write.

## Intended Surface / Boundary

Only review/test_diary_smoke.py. Nearby diary.html/js/css must not change.

## Out Of Scope

Backend route/schema/model changes, database migrations, normal non-smoke live diary enablement, autonomous Bernie actions, Gemini/LLM calls, taskpane, Command Centre, billing/SMS/security console, patient demographics, resource admin, and any un-intercepted real confirm-Bernie write during tests.

## Files I Expect To Edit

review/test_diary_smoke.py

## Implementation Steps

1. Add test_bernie_live_confirm_flow_harness_success. 2. Add test_bernie_live_confirm_flow_harness_blocked. 3. Add test_bernie_live_confirm_flow_harness_candidate_selection. 4. Add test_bernie_live_confirm_flow_harness_api_error. 5. Run and verify tests using venv python pytest.

## Visual / Behavioural Acceptance Checks

Verify that live-review confirmation ready correctly POSTs confirmed: true with the expected payload to /confirm-bernie on user click. Verify that blocked, candidate selection, and HTTP error states do not show confirmation or attempt any writes.

## Risks / Ambiguities

Playwright test runner timing/race conditions on slower CPU. Mitigation: use wait_for_selector.

## Codex Plan Review

- Review result: Accepted. Plan was narrow, test-only, and limited to the deterministic Playwright harness.
- Required changes before implementation: None. Antigravity did not complete implementation after release; Ariadne completed the same approved test-only scope directly.
- Approved to proceed: yes
