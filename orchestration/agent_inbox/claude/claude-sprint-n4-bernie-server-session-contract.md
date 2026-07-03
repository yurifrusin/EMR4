# claude-sprint-n4-bernie-server-session-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 7fdfd75 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-n4-bernie-server-session-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-n4-bernie-server-session-contract --commit-message "Sprint N4 Bernie server session contract" --message "claude-sprint-n4-bernie-server-session-contract ready for Codex review"` |

## Mission

Plan Sprint N4 backend/domain work for server-side Bernie session and event persistence: retention/privacy posture, concurrency/staleness controls, migration-shaped schema, and endpoint/service boundaries that build on app/services/bernie/session.py without implementing production code before plan approval.

## Scope

### In Scope

Plan first only. app/services/bernie/session.py, possible future models/schemas/router/service/test boundaries, PHI-minimised session/event fields, retention classification options, optimistic concurrency/versioning, stale event rejection, signed confirmation evidence linkage, migration strategy, focused tests.

### Out of Scope

No production code before plan gate, no broad API-spine rewrite, no GraphRAG wiring, no auto-mode, no UI implementation, no live PHI, no weakening staff confirmation, no storing full transcript unless explicitly justified.

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

Plan must specify focused backend tests, migration checks if a later implementation adds tables, privacy/retention assertions, concurrency/staleness tests, and compatibility checks with existing Bernie turn/signed evidence suites.

## Merge Criteria

Codex can accept the plan when it gives a concrete minimal persistence path, names exact files/schemas/tests, preserves PHI/privacy boundaries, handles concurrent tabs/stale events, and keeps diary writes evidence-gated.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
