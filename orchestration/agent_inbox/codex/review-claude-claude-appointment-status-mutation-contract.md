# review-claude-claude-appointment-status-mutation-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-appointment-status-mutation-contract` |
| Status | integrated |

## Review Request

Appointment status mutation contract ready for Codex review

## Worker Completion Notes

- **Files changed:** `tests/test_appointment_status_mutations.py` (new, 22 tests). No production code changed — endpoint is correct as-is.

- **What is tested:** auth gate (401); non-existent appointment (404); cross-practice mutation (404 — `_get_appointment` filters by both id and practice_id); all 8 valid statuses accepted (200 + updated status, parametrized); invalid status value (422); response embeds patient + practitioner AHPRA + appointment_type + end_time; mutation to each active status → appears in waiting room (4 parametrized); mutation to each terminal status → disappears from waiting room (4 parametrized).

- **Verification run:**
  ```
  python -m pytest tests/test_appointment_status_mutations.py -v  → 22 passed in 54.92s
  python -m pytest tests/test_appointment_conflicts.py::test_non_blocking_status_frees_slot[DNA] tests/test_slots.py -v  → 6 passed in 23.03s (isolated)
  python -m pytest tests/test_waiting_room.py tests/test_appointment_conflicts.py tests/test_slots.py -q  → 29 passed, 1 failed, 1 error in 180.99s (full combined run)
  ```
  The 1 failure (`test_non_blocking_status_frees_slot[DNA]`) and 1 error (`test_slots.py::test_15min_booking_blocks_only_its_slot`) both pass in isolation — pre-existing ordering flap when tests run in combined session; not caused by these changes.

- **Remaining risks:** The endpoint accepts any status transition without a state-machine guard (e.g. Completed → Booked is allowed). Intentional for now — receptionists need flexibility to correct mistakes. When lifecycle action buttons are added to the diary UI, a transition guard may be worth adding. No safety issue for the current read-only diary slice.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-appointment-status-mutation-contract.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result: Accepted and integrated. The branch was test-only; Codex added
  one role-gate regression for status PATCH during integration.
- Follow-up required: Keep the no-state-machine transition policy explicit. It
  is intentionally flexible for receptionist correction at this stage.
