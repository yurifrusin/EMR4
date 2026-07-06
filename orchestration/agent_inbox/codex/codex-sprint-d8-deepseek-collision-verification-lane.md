# codex-sprint-d8-deepseek-collision-verification-lane

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | integrated |
| Created | 23b93f1 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-d8-deepseek-collision-verification-lane --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-d8-deepseek-collision-verification-lane --commit-message "sprint-d8-deepseek-collision-verification-lane" --message "codex-sprint-d8-deepseek-collision-verification-lane ready for Codex review"` |

## Mission

Independent verification lane for Sprint D8 patient collision source hardening. Write a focused test suite that probes edge cases the D6 closeout flagged: cap overflow (patient with 4+ future bookings where the collision is entry #4, beyond the compact 3-entry cap), self-collision on reschedule, self-collision on extend, and genuine same-day collision with the requested day. Do NOT modify production code.

## Scope

### In Scope

1) Read the existing collision detection in app/services/bernie_patient_context.py and app/routers/appointments.py. 2) Write a new test file tests/test_bernie_d8_collision_source_hardening.py with focused tests for: cap overflow detection, source-appointment self-exclusion, same-day genuine collision. 3) Use the existing test fixtures and patterns from test_bernie_d6_patient_advisory_collision.py. 4) Submit the test file as the deliverable.

### Out of Scope

No production code changes. No changes to app/ directory. No frontend/UI. No schema changes. No existing test file modifications.

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

py_compile on new test file, pytest on new test file, git diff --check

## Merge Criteria

New test file compiles, tests pass or clearly document expected failure modes, no production code modified

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
