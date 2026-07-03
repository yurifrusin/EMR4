# claude-sprint-n7-bernie-session-outcome-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | superseded |
| Created | f46cb2f |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-n7-bernie-session-outcome-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-n7-bernie-session-outcome-contract --commit-message "Sprint N7 Bernie session outcome contract" --message "claude-sprint-n7-bernie-session-outcome-contract ready for Codex review"` |

## Mission

Plan a narrow backend/session contract slice that binds Bernie interpreter, supervised-booking proposal, candidate selection, and confirmation outcomes into server-owned Bernie session events/revisions without adding a database table or PHI-heavy transcript persistence.

## Scope

### In Scope

Plan first only. app/routers/appointments.py, app/schemas/appointments.py, app/services/bernie/session.py, app/services/bernie/session_store.py, focused Bernie session/evidence/confirm tests. Identify minimal additive event types/payload refs, revision semantics, and confirmation-evidence/session binding.

### Out of Scope

No implementation before plan approval, no persisted DB table/migration, no raw transcript/PHI event storage, no GraphRAG/practice-knowledge wiring, no auto-mode, no Diary UI implementation in Claude lane, no broad API-spine rewrite.

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

Plan must specify focused backend route/store/evidence tests for outcome event appends, stale revisions, idempotency, PHI guardrails, and session-bound confirmation evidence.

## Merge Criteria

Codex can accept the plan when server session authority is advanced without raw PHI persistence, signed confirmation evidence remains fail-closed, and the UI can continue to render safely while server outcome events mature.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- None by Claude.
- Verification run:
- Claude headless plan attempt returned 429 session limit, resetting 1am Australia/Brisbane, before a plan packet was submitted.
- Ariadne replaced this lane with local backend/session implementation and focused verification.
- Remaining risks:
- Retry Claude on a later sprint after quota reset if deeper backend review is needed.
