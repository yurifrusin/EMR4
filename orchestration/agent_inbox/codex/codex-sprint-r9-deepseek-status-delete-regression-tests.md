# codex-sprint-r9-deepseek-status-delete-regression-tests

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/sprint-r9-status-delete-regression-tests` |
| Status | queued |
| Created | b01ccc0 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-r9-deepseek-status-delete-regression-tests --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-r9-deepseek-status-delete-regression-tests --commit-message "Sprint R9 DeepSeek Status/Delete Regression Tests" --message "codex-sprint-r9-deepseek-status-delete-regression-tests ready for Codex review"` |

## Mission

DeepSeek Flash designs or implements focused tests for status/delete retrospective governance boundaries.

## Scope

### In Scope

Focused pytest additions or artifact if sandbox blocks Python/git; prove past appointment status/delete confirmations remain allowed while freshness/signed-evidence/state guards still block stale or tampered confirms.

### Out of Scope

Production route implementation unless a failing test proves an existing governance guard is missing; UI/assets, migrations, temporal slot-write blocks.

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

py_compile touched tests; focused pytest for new status/delete confirm tests; git diff --check.

## Merge Criteria

Tests demonstrate retrospective status/delete exemption and existing safety gates without changing create/update temporal semantics.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
