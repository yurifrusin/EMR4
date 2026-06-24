# claude-appointment-move-resize-proposal-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | submitted |
| Created | 2839fab |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-appointment-move-resize-proposal-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-appointment-move-resize-proposal-contract --commit-message "Appointment Move/Resize Proposal Contract" --message "claude-appointment-move-resize-proposal-contract ready for Codex review"` |

## Mission

Plan and then harden the backend proposal contract needed for future diary move/resize interactions: moving an appointment date/time/resource and resizing duration must be preflighted through the non-mutating update proposal layer before any write.

## Scope

### In Scope

app/routers/appointments.py, app/schemas/appointments.py if needed, and focused tests around POST /appointments/proposals/update/{appointment_id} for drag/drop-like date/time/practitioner changes, resize/duration changes, conflict blocks, break warnings, terminal-status blocks, practice isolation, and proof the appointment row is unchanged.

### Out of Scope

Diary frontend implementation, drag/drop/resize UI, taskpane, Command Centre, Gemini, migrations unless the plan proves a schema issue, broad appointment redesign, master/handoff changes.

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

Plan packet first; after approval run focused appointment update proposal pytest checks, py_compile/check_backend as needed, and assertions that proposal calls do not mutate appointments.

## Merge Criteria

Codex can integrate when the plan is accepted, implementation stays in backend proposal/test boundaries, focused tests pass, and the response contract is compatible with existing create/edit/status/waiting-area proposal flows.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

- Files changed:
  - `tests/test_appointment_update_proposal.py` — 4 new tests in a new "Diary move/resize scenario tests" section. No production code changes.

- Verification run:
  - `pytest tests/test_appointment_update_proposal.py -v --tb=short -p no:randomly` — **31 passed, 0 failed** (27 pre-Sprint-26 + 4 new)
  - All new tests assert the appointment row is unchanged after the proposal call (non-mutating invariant held).
  - Covers: resize-extend blocked by next booking; cross-practitioner drag blocked by target column conflict; adjacent-slot boundary is safe (open-interval semantics); resize-shrink clears an otherwise-overlapping conflict.

- Remaining risks:
  - No implementation changes — zero blast radius on existing endpoints or schemas.
  - The adjacent-slot test encodes the `_overlaps` half-open interval contract as an assertion. If `_overlaps` is ever changed to closed-interval semantics, this test will catch the regression before it reaches production.
