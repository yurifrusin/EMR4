# plan-claude-claude-appointment-mouse-drag-proposal-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-appointment-mouse-drag-proposal-contract` |
| Status | pending_plan_review |
| Created | 2026-06-25 10:55 +1000 |
| Source HEAD | `90d0d15` |

## Plan Summary

Tests-only: 4 PUT /{id} conflict tests for drag/resize confirmed update path in test_appointment_conflicts.py — no implementation changes

## My Understanding

Sprint 26 proved the PROPOSAL path (POST /proposals/update/{id}) correctly blocks drag/resize conflicts. The confirmed UPDATE path PUT /{id} (app/routers/appointments.py:964-1036) also has conflict detection: it runs _raise_if_conflict with exclude_id=appointment_id when any of {practitioner_id, start_time, appointment_date, start_time_local, duration_minutes} is in the request body. This covers all three mouse gesture payloads: (1) start-time move = {appointment_date, start_time_local, duration_minutes unchanged}; (2) duration resize = {duration_minutes}; (3) column/resource move = {practitioner_id}. The existing test_appointment_conflicts.py tests POST conflict detection only. No tests exist for the PUT path's conflict enforcement. The implementation is correct; no production code gaps were found. This sprint adds 4 tests to test_appointment_conflicts.py for the PUT confirmed update path.

## Intended Surface / Boundary

tests/test_appointment_conflicts.py only — 4 new tests appended. No changes to app/routers/appointments.py, app/schemas/appointments.py, test_appointment_update_proposal.py, or any other file.

## Out Of Scope

No production code changes. No migrations. No diary frontend. No changes to proposal tests (already covered by Sprint 26). No new schemas.

## Files I Expect To Edit

tests/test_appointment_conflicts.py — 4 new tests in a new PUT conflict section, plus a _put helper function.

## Implementation Steps

1. Add _put helper: PUT /api/v1/appointments/{id} with body and auth token, returns response. 2. Add test_put_drag_move_to_conflicting_time_rejected: create blocking at 10:00 and subject at 9:00; PUT subject to appointment_date+start_time_local that overlaps blocking; assert 409, detail has conflicting_appointment_id. Assert subject row is unchanged (re-fetch). 3. Add test_put_resize_into_next_booking_rejected: create next_booking at 9:15 and subject at 9:00 for 15 min; PUT subject with duration_minutes=30 (would overlap 9:15 booking); assert 409. 4. Add test_put_drag_to_practitioner_with_conflict_rejected: create pr2, give pr2 a booking at 10:00; create subject for practitioner at 10:00; PUT subject with practitioner_id=pr2.id; assert 409 (pr2 is blocked at that time). 5. Add test_put_adjacent_drag_allowed: create A at 9:00 for 15 min and B at 9:15 for 15 min; PUT A to start_time_local=09:00 (same slot, adjacency invariant) — A is excluded by exclude_id, B is adjacent not overlapping; assert 200. Or more clearly: create C at 9:30 for 15 min and D at 9:00 for 30 min; PUT C to start at 9:15 (would end at 9:30, D ends at 9:30 — adjacent at lower boundary); assert 200. 6. Run pytest tests/test_appointment_conflicts.py -q --tb=short -p no:randomly.

## Visual / Behavioural Acceptance Checks

test_put_drag_move_to_conflicting_time_rejected: 409, detail.conflicting_appointment_id present, subject row unchanged. test_put_resize_into_next_booking_rejected: 409, subject duration unchanged. test_put_drag_to_practitioner_with_conflict_rejected: 409, subject still on original practitioner. test_put_adjacent_drag_allowed: 200, appointment updated, no conflict. All pre-Sprint-27 conflict tests still pass.

## Risks / Ambiguities

The PUT endpoint has the conditional conflict check (line 1015 set intersection). If duration_minutes is sent alone, the check runs — confirmed. If practitioner_id is sent alone (column-only drag), the check runs with the existing time — confirmed. No implementation changes means no blast radius. The adjacency test precisely encodes _overlaps open-interval semantics on the write path, consistent with Sprint 26 adjacency test on the proposal path.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
