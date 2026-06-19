# review-claude-claude-waiting-room-status-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-waiting-room-status-contract` |
| Status | integrated |

## Review Request

Waiting room status contract ready for Codex review

## Worker Completion Notes

- **Files changed:** `tests/test_waiting_room.py` (new, 18 tests). No production code changed — existing endpoint passes all tests without modification.

- **What is tested:** auth gate; empty result; all 4 included statuses (Booked/Confirmed/Arrived/InConsult, parametrized); all 4 excluded statuses (Completed/Cancelled/NoShow/DNA, parametrized); date scoping (past date excluded; mixed-date set returns only today); ordering by `queue_position` then `start_time_local` (nulls last); `?practitioner_id=` filter; practice isolation; embedded `patient`, `practitioner` (with AHPRA), `appointment_type` (with `color_hex`), `end_time`, `start_time_local`, `appointment_date`.

- **Verification run:**
  ```
  python -m pytest tests/test_waiting_room.py -v          → 18 passed in 30.02s
  python -m pytest tests/test_appointment_conflicts.py tests/test_slots.py tests/test_auth_required.py -q  → 19 passed in 26.26s
  ```

- **Remaining risks:** `TODAY = date.today()` is computed at module import time. The endpoint resolves today in practice timezone (Australia/Sydney default). Tests seeding `appointment_date=TODAY` will fail at AEST/AEDT midnight if the date rolls over between import and the request. Known test-infrastructure limitation, not a product bug.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-waiting-room-status-contract.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result: Accepted and integrated. The branch is test-only and validates
  the existing waiting-room contract without production code changes.
- Follow-up required: The test module's import-time `date.today()` can be fragile
  around timezone midnight; fix later if it becomes noisy in CI.
