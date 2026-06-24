# review-claude-claude-appointment-status-waiting-area-proposal-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-appointment-status-waiting-area-proposal-contract` |
| Status | queued |

## Review Request

claude-appointment-status-waiting-area-proposal-contract ready for Codex review

## Worker Completion Notes

- Files changed:
  - `app/schemas/appointments.py` — added `AppointmentWaitingAreaProposalIn`, `AppointmentWaitingAreaCommand`, `AppointmentWaitingAreaProposalOut` schemas
  - `app/routers/appointments.py` — added `waiting_area_assigned_on_terminal` warning to `propose_status_update`; added new import for three new schemas; added `POST /proposals/waiting-area/{appointment_id}` endpoint (`propose_waiting_area_update`) with `already_in_area` block, `waiting_area_cleared` warning, and `execute_with_report`/`proposal`/`blocked` tier logic
  - `tests/test_appointment_update_proposal.py` — added `WAITING_AREA_URL` constant and 8 new tests: 2 isolation tests for status proposal (cross-practice 404, non-existent 404), 1 new warning test (`waiting_area_assigned_on_terminal`), and 5 tests for the new waiting-area proposal endpoint (assign, clear, already_in_area block, cross-practice 404, non-existent 404)

- Verification run:
  - `python -m py_compile app/routers/appointments.py app/schemas/appointments.py` — clean
  - `pytest tests/test_appointment_update_proposal.py -q --tb=short -p no:randomly` — **27 passed, 0 failed** (19 pre-Sprint-25 + 8 new)
  - All new tests assert appointment rows are unchanged after each proposal call (non-mutating invariant held)

- Remaining risks:
  - `waiting_area_assigned_on_terminal` warning fires when terminal status AND non-null waiting_area_id are both present. The PATCH /{id}/status handler will still apply both (set terminal status AND set waiting_area_id) if the caller proceeds after the warning — this is intentional (the proposal surfaces the contradiction; the write endpoint enforces whatever the caller sends). No behavioral change to PATCH /{id}/status in this sprint.
  - The new waiting-area proposal endpoint does not block terminal-status appointments from being moved between areas (that is a future policy question for Bernie tooling); it only surfaces `waiting_area_cleared` if explicitly set to null.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-appointment-status-waiting-area-proposal-contract.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
