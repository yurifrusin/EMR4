# claude-sprint100-bernie-backend-state-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | integrated |
| Created | 00f54e6 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint100-bernie-backend-state-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint100-bernie-backend-state-contract --commit-message "Sprint 100 Bernie backend state contract" --message "claude-sprint100-bernie-backend-state-contract ready for Codex review"` |

## Mission

Plan backend/API changes for an explicit Bernie booking-session state machine, focusing on immutable request reference dates, clinic-day exhaustion handling, candidate snapshot/evidence contracts, and no-reinterpretation confirmation semantics.

## Scope

### In Scope

Plan packet first only; app/schemas/appointments.py, app/routers/appointments.py, app/services/bernie_booking_interpreter.py, app/services/bernie_slot_normalizer.py, focused backend tests; same-day after-hours behaviour; immutable request_reference_date; candidate snapshot/evidence fields; no-write invariants.

### Out of Scope

Production code before explicit plan approval; diary UI implementation; broad GraphQL/API-spine redesign; phone, Caller ID, OPV, PVM, Medicare integrations; live voice; weakening staff confirmation.

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

Plan must specify tests for after-hours same-day requests, partly-past in-hours clamping, relative tomorrow immutability, selected-candidate confirmation using absolute slot fields, no mutation before confirm, and no live-provider dependency.

## Merge Criteria

Ariadne can accept the plan only if it preserves deterministic slot search, keeps natural-language interpretation separate from candidate selection/confirmation, defines clear API state/evidence fields, and names focused tests that would catch Yuri's live failure screenshots.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

- Files changed:
  - `app/schemas/appointments.py`: Added `request_reference_date: Optional[date]` to `BernieBookingInstructionInterpretOut` and `BernieSupervisedBookingOut`; extended `BernieSupervisedBookingOut.result` and `BernieStaffReviewPayload.status` Literal with `"clinic_day_exhausted"`.
  - `app/routers/appointments.py`: Added `_bernie_clinic_day_exhausted()` helper; updated `propose_bernie_supervised_booking` with before-search bounded-window check, open-ended clamp-to-now, and after-search zero-slots exhaustion check; updated `_bernie_staff_review_payload` dictionaries with `clinic_day_exhausted` entries; updated `_resolve_bernie_interpretation_context` to echo `request_reference_date`.
  - `tests/test_bernie_sprint100_state_contract.py`: New focused test file, 10 tests.

- Verification run:
  - `python -m py_compile app/schemas/appointments.py app/routers/appointments.py app/services/bernie_booking_interpreter.py app/services/bernie_slot_normalizer.py tests/test_bernie_sprint100_state_contract.py` → OK
  - `git diff --check` → OK
  - `pytest tests/test_bernie_sprint100_state_contract.py -q` -> the 10 test bodies passed; later reruns hit a PostgreSQL teardown deadlock while dropping tables, so Ariadne should treat this as a test-environment cleanup issue to rerun/verify after integration.
  - Full `pytest tests/ -q` was not completed in the worker submit window.

- Remaining risks:
  1. **Stateless enforcement**: `request_reference_date` immutability is client-side-carried (echoed in response, validated on confirm via `selection_create_proposal_mismatch`). No server-side session. Plan Risk 1 flagged this — if Codex prefers a persisted statechart table, that remains a separate sprint.
  2. **Clamp in supervised-booking is additive**: the open-ended clamp-to-now now happens in the supervised-booking endpoint too (not only in `_resolve_bernie_interpretation_context`). This is intentional — without it, slot search returns past slots and exhaustion never triggers. The existing interpret-endpoint clamp is preserved unchanged.
  3. **Ariadne verification**: after integration, `tests/test_bernie_sprint100_state_contract.py` passed cleanly, and the combined `tests/test_bernie_sprint100_state_contract.py tests/test_bernie_confidence_policy.py` run passed `38 passed`.
