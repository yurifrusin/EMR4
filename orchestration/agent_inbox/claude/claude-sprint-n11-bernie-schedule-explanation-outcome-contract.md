# claude-sprint-n11-bernie-schedule-explanation-outcome-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | e82a885 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-n11-bernie-schedule-explanation-outcome-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-n11-bernie-schedule-explanation-outcome-contract --commit-message "Sprint N11 Bernie schedule explanation outcome contract" --message "claude-sprint-n11-bernie-schedule-explanation-outcome-contract ready for Codex review"` |

## Mission

Plan the backend/domain contract that makes schedule and roster explanations first-class typed Bernie booking outcomes, so unavailable-practitioner or unavailable-day cases are distinct from no matching slots, clarification, review blocks, and advisory warnings.

## Scope

### In Scope

Plan first. app/services/diary and app/services/bernie domain modules, app/routers/appointments.py supervised/interpret adapters, app/schemas/appointments.py additive outcome/explanation fields if needed, focused backend tests. Preserve N10 outcome semantics, N9 server_session snapshot loop, signed/session-bound confirm authority, and advisory-only practice-knowledge boundary.

### Out of Scope

No production code before plan approval. No persisted session table, GraphRAG route wiring, auto-mode, taskpane, Command Centre, broad API rewrite, or UI redesign. Do not make UI invent roster truth.

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

Plan must specify focused backend tests proving roster_unavailable/schedule_gap is distinct from no_matching_times, existing appointment advisory does not block tomorrow, no-slot only follows real searched zero candidates, clarification/review remains separate, and outcome cannot grant confirm authority.

## Merge Criteria

Concrete typed outcome/explanation contract lets Bernie speak naturally about roster/schedule gaps while the state machine remains authoritative over affordances and writes.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
