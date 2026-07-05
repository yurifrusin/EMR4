# codex-sprint-r3-deepseek-backend-hardening

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/sprint-r3-deepseek-backend-hardening` |
| Status | queued |
| Created | f8bc6c8 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-r3-deepseek-backend-hardening --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-r3-deepseek-backend-hardening --commit-message "Sprint R3: DeepSeek Backend Stale Session Hardening" --message "codex-sprint-r3-deepseek-backend-hardening ready for Codex review"` |

## Mission

Use DeepSeek Flash as a temporary backend implementation worker while Claude quota recovers. Implement the core fail-closed stale Bernie session/revision guard only if tests show a production gap; otherwise add focused backend regression coverage and report no-code-needed.

## Scope

### In Scope

app/services/bernie/session_store.py, app/routers/appointments.py session/confirm stale-coordinate seams, focused tests for stale revision/context handling, clarification fresh-flow preservation, and no appointment/audit mutation on stale replies.

### Out of Scope

Diary UI/taskpane/Word changes, live provider calls, broad patient collision source hardening, GraphRAG/MCP/indexer automation, global config/model switching, master/handoff updates, overlapping Antigravity docs/fixtures unless Ariadne reconciles.

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

py_compile touched backend/tests; focused pytest for Bernie session store/routes/clarification merge/context frames/scenario integrity; git diff --check; Ariadne reruns all tests if bridge sandbox cannot.

## Merge Criteria

Either a minimal production fix plus tests proves stale coordinates fail closed before merge/confirm, or worker demonstrates existing code is sufficient with stronger tests; no overlap conflict with the existing DeepSeek regression branch or Antigravity domain artifacts.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
