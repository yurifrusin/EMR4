# plan-claude-claude-appointment-move-resize-proposal-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-appointment-move-resize-proposal-contract` |
| Status | pending_plan_review |
| Created | 2026-06-25 09:04 +1000 |
| Source HEAD | `8729ebe` |

## Plan Summary

Tests-only: 4 targeted diary move/resize scenario tests against existing propose_update_appointment — no implementation changes needed

## My Understanding

The existing propose_update_appointment endpoint (app/routers/appointments.py:570-716) is correctly implemented: it merges proposed fields over current values, runs _find_conflicting_appointment with exclude_id=appointment_id (preventing self-conflict), blocks on terminal_status, blocks on conflict, warns on break_overlap and provisional_patient. _overlaps uses strict open-interval semantics (end_a > start_b) so adjacent bookings are not conflicts. NON_BLOCKING_STATUSES = (Cancelled, NoShow, DNA) are excluded from conflict checks. For diary move/resize the three untested scenarios are: (1) resize an appointment longer so its new end overlaps the next booking — should block; (2) drag an appointment to a different practitioner (column change) where the target practitioner has an existing booking at that time — should block using the NEW practitioner id; (3) move appointment to start exactly when another ends — should be safe because _overlaps uses strict inequality. A fourth test (resize down, no conflict) rounds out the resize coverage. No implementation gaps found — tests only.

## Intended Surface / Boundary

tests/test_appointment_update_proposal.py only. No changes to app/routers/appointments.py, app/schemas/appointments.py, diary frontend, taskpane, or any other file.

## Out Of Scope

No production code changes. No migrations. No diary frontend. No taskpane or Command Centre. No changes to existing test logic.

## Files I Expect To Edit

tests/test_appointment_update_proposal.py — 4 new tests appended to the update proposal section.

## Implementation Steps

1. Add test_update_proposal_resize_blocked_into_next_booking: create booking A at 9:00 for 15 min, booking B at 9:15 for 15 min (same practitioner, same date); propose resize A to 30 min; assert appointment_conflict block, conflict.appointment_id == B.id, A row unchanged. 2. Add test_update_proposal_drag_to_practitioner_with_conflict: create pr2 in same practice; create booking C at 10:00 for 15 min for pr2; create subject D at 10:00 for 15 min for practitioner (no conflict there); propose update D with practitioner_id=pr2.id (same date/time); assert appointment_conflict block, conflict.appointment_id == C.id, D row unchanged. 3. Add test_update_proposal_adjacent_slot_is_safe: create booking E at 9:15 for 15 min; create subject F at 9:00 for 15 min; propose move F to 9:00 (same date, no actual change in time — already tested by empty_body); actually test moving subject to end at exactly 9:15 (9:00 for 15 min, E starts at 9:15) — assert safe, no conflict. This is already the default from _make_appt, but make it explicit by constructing the exact adjacency scenario with subject at 9:00 for 15 and adjacent at 9:15. 4. Add test_update_proposal_resize_shrink_is_safe: create booking G at 9:00 for 30 min, booking H at 9:20 for 15 min (adjacent after shrink); propose shrink G to 15 min (now ends at 9:15, H at 9:20 is clear); assert safe, no conflict, G row unchanged. 5. Run pytest tests/test_appointment_update_proposal.py -q --tb=short -p no:randomly.

## Visual / Behavioural Acceptance Checks

test_resize_blocked_into_next_booking: status 200, safe=False, autonomy_tier=blocked, blocks[0].code=appointment_conflict, conflict.appointment_id matches the next booking, A row unchanged. test_drag_to_practitioner_with_conflict: status 200, safe=False, blocks[0].code=appointment_conflict, conflict.appointment_id matches C (pr2 existing booking), D row unchanged. test_adjacent_slot_is_safe: status 200, safe=True, blocks=[], E unchanged. test_resize_shrink_is_safe: status 200, safe=True, blocks=[], G unchanged. All 27 pre-Sprint-26 tests still pass (31 total with 4 new).

## Risks / Ambiguities

All scenarios rely on existing _find_conflicting_appointment and _overlaps logic — no implementation changes means no blast radius. The test for adjacent adjacency is the most subtle; the assertion depends on _overlaps half-open interval semantics (start_a < end_b AND end_a > start_b), which is already verified by the existing Sprint 23 regression tests. If the adjacency test fails unexpectedly, it would indicate a regression in _overlaps, not a problem with this plan.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
