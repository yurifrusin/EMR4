# claude-sprint-n5-bernie-session-endpoint-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | superseded |
| Created | 9a38e67 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-n5-bernie-session-endpoint-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-n5-bernie-session-endpoint-contract --commit-message "Sprint N5 Bernie session endpoint contract" --message "claude-sprint-n5-bernie-session-endpoint-contract ready for Codex review"` |

## Mission

Plan Sprint N5 backend work to expose the N4 Bernie session store semantics through a minimal authenticated API contract: active session/new session/event append/refetch, revision conflict responses, and compatibility with existing Bernie booking endpoints.

## Scope

### In Scope

Plan first only. app/services/bernie/session_store.py, app/services/bernie/session.py, app/schemas/appointments.py or new schemas if appropriate, app/routers/appointments.py minimal Bernie session routes, tests for auth/ownership/revision/idempotency/stale events. Build on N4 store; no PHI-heavy table yet unless explicitly justified.

### Out of Scope

No production code before plan gate, no database session table/migration unless Ariadne approves after plan review, no broad API-spine rewrite, no GraphRAG, no auto-mode, no UI implementation in Claude lane, no live PHI.

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

Plan must specify focused backend route/service tests, py_compile, adjacent Bernie session/evidence tests, and how stale revision conflicts are represented to the Diary UI.

## Merge Criteria

Codex can accept the plan when it gives a minimal route contract, preserves signed evidence/write gates, avoids PHI-heavy persistence, and names exact files/tests.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
