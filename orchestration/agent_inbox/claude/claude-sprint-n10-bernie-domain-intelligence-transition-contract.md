# claude-sprint-n10-bernie-domain-intelligence-transition-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | integrated |
| Created | 9baa1ae |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-n10-bernie-domain-intelligence-transition-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-n10-bernie-domain-intelligence-transition-contract --commit-message "Sprint N10 Bernie domain intelligence transition contract" --message "claude-sprint-n10-bernie-domain-intelligence-transition-contract ready for Codex review"` |

## Mission

Plan the backend/domain contract for Bernie to distinguish no matching times, schedule/roster unavailability, clarification/review blocks, and advisory warnings as first-class state/route outcomes rather than scripted UI guesses.

## Scope

### In Scope

Plan first. app/services/bernie domain modules, app/routers/appointments.py supervised/interpret response envelopes, app/schemas/appointments.py typed outcome fields, relevant backend tests. Preserve N9 server_session snapshot loop.

### Out of Scope

No production code before plan approval. No persisted session table, GraphRAG route wiring, auto-mode, taskpane, Command Centre, broad API rewrite, or UI redesign.

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

Plan must specify focused backend tests for outcome classification, stale/session compatibility, and no-write/confirm authority boundaries.

## Merge Criteria

Plan gives concrete typed outcomes and transition boundaries that let Bernie speak naturally while state machine guardrails determine affordances and blocking.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: app/services/diary/outcomes.py, app/services/bernie/outcomes.py, app/schemas/appointments.py, app/routers/appointments.py, tests/test_bernie_booking_outcomes.py
- Verification run: Ariadne recovered the timed-out Claude backend work by checkpointing the dirty Claude worktree, cherry-picking it to master, repairing outcome/state precedence and interpret-route assertion behaviour, then running focused and adjacent Bernie backend suites listed in orchestration/sprint_closeout.md.
- Remaining risks: Claude did not complete the formal submit path before the worker timeout; Ariadne reviewed and integrated the recovered backend patch directly.
