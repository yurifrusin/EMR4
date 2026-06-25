# plan-claude-claude-cancelled-appointment-review-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-cancelled-appointment-review-contract` |
| Status | integrated |
| Created | 2026-06-25 13:29 +1000 |
| Source HEAD | `63f427b` |

## Plan Summary

No new route or schema needed. Add tests/test_cancelled_appointment_review.py with 5 tests proving GET /appointments?status=Cancelled exposes cancellation_reason correctly.

## My Understanding

GET /appointments?status=Cancelled is already practice-scoped, authenticated, and returns AppointmentOut. Sprint 29 added cancellation_reason to AppointmentOut and persists it on the row. No new route or schema is required. Gap is test coverage proving the review path exposes the reason, is practice-isolated, and requires auth.

## Intended Surface / Boundary

Backend tests only: new tests/test_cancelled_appointment_review.py. No route, schema, model, or migration changes. No frontend touched.

## Out Of Scope

New routes; schema changes; migrations; diary frontend; taskpane; Command Centre; restore/reactivation; audit-history; billing; SMS; multi-status filter

## Files I Expect To Edit

tests/test_cancelled_appointment_review.py (new, 5 tests)

## Implementation Steps

1. Create tests/test_cancelled_appointment_review.py with helpers _cancel_with_reason and _list_cancelled. 2. test_cancelled_list_requires_auth: 401 without token. 3. test_cancelled_list_includes_cancellation_reason: DELETE with reason then GET?status=Cancelled, assert reason in response. 4. test_cancelled_list_reason_null_when_not_given: DELETE without body then GET, assert cancellation_reason is null. 5. test_cancelled_status_filter_excludes_active: cancel one of two appts, GET?status=Cancelled returns only the cancelled one. 6. test_cancelled_cross_practice_isolation: cancel appt in practice_b, GET as practice_a user sees nothing. 7. py_compile; pytest; git diff --check.

## Visual / Behavioural Acceptance Checks

GET /appointments?status=Cancelled returns cancelled rows with cancellation_reason populated or null. Active appointments excluded. Cross-practice rows excluded. 401 without auth. All 5 tests pass; pre-existing tests unaffected.

## Risks / Ambiguities

Zero blast radius: no production code changes. Test isolation is handled by the existing conftest transaction rollback per test.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: yes
