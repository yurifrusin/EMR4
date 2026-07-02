# claude-sprint104-bernie-patient-context-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 12fb780 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint104-bernie-patient-context-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint104-bernie-patient-context-contract --commit-message "Sprint 104 Bernie Patient Context Contract" --message "claude-sprint104-bernie-patient-context-contract ready for Codex review"` |

## Mission

Plan the backend/API side of Sprint 104: explicit Bernie conversational state memory fields, deterministic patient_booking_context after patient recognition, no-slot suggestion response contracts, and focused regression coverage. This is a plan-gated packet only; write and submit the implementation plan, then stop.

## Scope

### In Scope

Plan packet first only. Likely surfaces: app/schemas/appointments.py, app/routers/appointments.py, app/services/bernie_booking_interpreter.py, app/services/bernie_transition_table.py or a new small service for patient_booking_context, seed.py/dev fixtures, and focused tests under tests/. Preserve the split between patient recognition and patient details verification. Define compact recent/future booking context and derived signals without broad diary dumps.

### Out of Scope

Production code before plan approval; Diary UI implementation; broad root-to-branch API rewrite; XState/runtime dependency; voice/headset/Caller ID; Medicare/HI/IHI/PVM/OPV; limited Bernie auto-mode; privileged agent-only write paths; clinical interpretation of appointment notes.

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

Plan must name exact files, tests, and API/schema contracts. Include tests for recognized-patient context fetch, recent/future booking summaries, existing future follow-up warning signal, no-slot response with typed suggestions, stale-context/freshness fields, no mutation before staff confirmation, and no live Gemini dependency.

## Merge Criteria

Ariadne can accept the plan if it keeps backend ownership narrow, keeps availability deterministic, fetches patient context only after recognition, avoids broad diary prompt context, preserves existing booking confirmation gates, and gives concrete test names/acceptance gates for implementation release.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
