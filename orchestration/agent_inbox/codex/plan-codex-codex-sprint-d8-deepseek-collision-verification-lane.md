# plan-codex-codex-sprint-d8-deepseek-collision-verification-lane

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `master` |
| Source Task | `codex-sprint-d8-deepseek-collision-verification-lane` |
| Status | pending_plan_review |
| Created | 2026-07-04 22:09 +1000 |
| Source HEAD | `23b93f1` |

## Plan Summary

D8 test file for collision cap-overflow, self-exclusion, and genuine-collision verification

## My Understanding

The has_existing_booking_on_requested_day function checks only context.future_bookings, capped at 3 entries (FUTURE_CAP=3). Cap overflow: patients with 4+ future bookings where the collision is entry #4+ won't trigger the warning. Self-collision: reschedule/extend flows include the source appointment in future_bookings, causing false-positive collision warnings. Genuine collision: the warning still correctly fires for a different booking on the requested day.

## Intended Surface / Boundary

tests/test_bernie_d8_collision_source_hardening.py

## Out Of Scope

No changes to app/ directory, no existing test file modifications, no production code, no frontend/UI, no schema changes

## Files I Expect To Edit

NEW: tests/test_bernie_d8_collision_source_hardening.py

## Implementation Steps

1. Read source code and existing D6 tests. 2. Write cap-overflow route-level test (4+ future bookings, entry #4 missed). 3. Write self-collision pure-unit test (date match returns True). 4. Write self-collision route-level test (reschedule on same date triggers false-positive warning). 5. Write genuine same-day collision route-level confirmatory test. 6. Run py_compile. 7. Run pytest -q --tb=short. 8. Run git diff --check.

## Visual / Behavioural Acceptance Checks

py_compile succeeds; pytest passes all tests; git diff --check returns clean

## Risks / Ambiguities

Route-level cap-overflow test depends on test DB being available (postgres on 5434). If pytest infrastructure is down, pure-unit tests still validate independently.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
