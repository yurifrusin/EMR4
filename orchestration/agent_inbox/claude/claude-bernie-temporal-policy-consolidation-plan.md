# claude-bernie-temporal-policy-consolidation-plan

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 76908b0 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-bernie-temporal-policy-consolidation-plan --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-bernie-temporal-policy-consolidation-plan --commit-message "Bernie temporal policy consolidation plan" --message "claude-bernie-temporal-policy-consolidation-plan ready for Codex review"` |

## Mission

Plan Sprint 106B: consolidate Bernie temporal/date/time/clinic-day policy behind the bounded app/services/bernie temporal domain without implementation yet.

## Scope

### In Scope

Read current Bernie temporal policy in app/services/bernie/temporal.py, app/services/bernie_booking_interpreter.py, app/routers/appointments.py, slot-search/proposal schemas, and focused Bernie temporal/slot tests. Produce a plan for a no-public-behaviour-change implementation that creates a single bounded temporal policy contract, removes duplicated same-day clamp/exhaustion/week-relative handling over later implementation, and preserves public JSON/API behaviour.

### Out of Scope

Do not edit production code during the plan phase. No persisted Bernie session table, no Alembic migration, no diary UI changes, no broad appointments.py rewrite, no LLM provider changes, no autonomous booking, no root-to-branch API review, no test deletion.

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

Plan must list exact files expected to change, behavioural acceptance checks, focused tests to run, and risks around current local test DB lifecycle fragility. Implementation must remain blocked until Ariadne/Yuri explicitly approve complete sprint task.

## Merge Criteria

Ariadne can review a narrow plan for temporal policy consolidation with clear preserved behaviours, no public contract break, and a bounded verification strategy.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
