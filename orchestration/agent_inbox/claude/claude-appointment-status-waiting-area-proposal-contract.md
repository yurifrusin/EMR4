# claude-appointment-status-waiting-area-proposal-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | submitted |
| Created | 3124a28 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-appointment-status-waiting-area-proposal-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-appointment-status-waiting-area-proposal-contract --commit-message "Appointment Status/Waiting-Area Proposal Contract" --message "claude-appointment-status-waiting-area-proposal-contract ready for Codex review"` |

## Mission

Extend the appointment proposal-first safety layer to status and waiting-area related mutations so receptionist-facing status/check-in/waiting-area changes can be preflighted before any write.

## Scope

### In Scope

Backend appointment proposal schemas/routes/tests for status and waiting-area changes; deterministic block/warning/allow responses; focused pytest coverage for practice scoping, invalid transitions, waiting-area validity, archived resources, and no-write proposal behavior; minimal production fixes required by those tests.

### Out of Scope

Diary frontend implementation, drag/drop/resize, recurrence, taskpane/Command Centre/Gemini, migrations unless absolutely required by the contract, Resource Administration UI, patient duplicate workflow.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Before editing project code, write an implementation plan and stop. The plan
   must be shown in the agent GUI and captured for Codex with the plan command
   above. Do not code until the user/Codex says `complete sprint task`.
5. After plan approval, work only inside the stated scope unless the user or Codex
   expands it.
6. Do not merge to `master`.
7. Do not move `handoff/current`.
8. Run the verification listed below.
9. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
10. Finish with the submit command above.

## Implementation Plan Requirements

Before coding, the implementation plan must include:

- My Understanding
- Intended Surface / Boundary
- Out of Scope
- Files I Expect To Edit
- Implementation Steps
- Visual / Behavioural Acceptance Checks
- Risks / Ambiguities

Pay special attention to visually loaded words such as cards, slots, stacking,
panels, waiting room, diary grid, booking slot, and status. State exactly which
surface is affected and which nearby surfaces must not change.

## Hard Stop Rules

- Do not push to `master` or `handoff/current`.
- Do not manually work around a failed protocol command (`handin`, `sync`, `submit`,
  `realign`, or related orchestration commands).
- Report every protocol-followed command back to Codex/orchestrator, whether it
  succeeds or fails. For success, include the command, working directory, branch,
  and short success result.
- If any protocol command refuses to run or fails, stop and report the exact command,
  working directory, branch, `git status --short --branch`, and error output to the
  orchestrator. On push failure, `submit` will also try to publish a
  `submit-alert/...` branch for Codex to poll.
- If these instructions conflict with remembered prior protocol, trust the current
  `handin` alerts and this task packet.

## Verification

Focused pytest suites for appointment status/waiting-area/proposal behavior plus app import/check_backend if touched; prove proposal calls do not mutate appointments before the follow-up write.

## Merge Criteria

Codex can verify typed proposal responses, no-write preflight semantics, practice/location safety, and compatibility with the existing diary status/check-in UI contract.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

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
