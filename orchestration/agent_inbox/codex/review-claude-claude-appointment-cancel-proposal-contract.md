# review-claude-claude-appointment-cancel-proposal-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-appointment-cancel-proposal-contract` |
| Status | queued |

## Review Request

claude-appointment-cancel-proposal-contract ready for Codex review

## Worker Completion Notes

- Files changed:
  - `app/schemas/appointments.py` — added `AppointmentDeleteCommand` and `AppointmentDeleteProposalOut` schemas.
  - `app/routers/appointments.py` — added import of both new schemas; fixed `cancel_appointment` (`DELETE /{id}`) to clear `waiting_area_id = None` before commit (was missing, causing stranded waiting-area display); added `POST /proposals/delete/{appointment_id}` endpoint with `already_in_status` BLOCK for already-Cancelled appointments and `waiting_area_cleared` WARNING when the appointment has a waiting area assigned.
  - `tests/test_appointment_status_mutations.py` — updated module docstring and top-level imports; added `_make_area` helper, `_delete` helper, `DELETE_PROPOSAL_URL` constant, and 7 new tests: `test_delete_requires_auth`, `test_delete_soft_cancels_appointment`, `test_delete_clears_waiting_area_on_cancel`, `test_delete_cross_practice_returns_404`, `test_delete_proposal_requires_auth`, `test_delete_proposal_warns_waiting_area_cleared`, `test_delete_proposal_blocked_already_cancelled`.

- Verification run:
  - `py_compile app/routers/appointments.py app/schemas/appointments.py` — OK.
  - `pytest tests/test_appointment_status_mutations.py -q --tb=short -p no:randomly` — **30 passed, 0 failed** (23 pre-Sprint-28 + 7 new).
  - `git diff --check` — OK (no trailing whitespace).

- Remaining risks:
  - No schema migration required — all changes are code-only.
  - The `waiting_area_id = None` fix in `cancel_appointment` is a one-line behavioural change; the 3 existing terminal-status waiting-room tests plus the new `test_delete_clears_waiting_area_on_cancel` together cover it.
  - `autonomy_tier` on `propose_delete_appointment` is always `"proposal"` (never `"execute_with_report"`), consistent with the task packet's intent that destructive/irreversible actions always require confirmation.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-appointment-cancel-proposal-contract.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
