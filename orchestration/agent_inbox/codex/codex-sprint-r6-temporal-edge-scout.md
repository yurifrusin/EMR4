# codex-sprint-r6-temporal-edge-scout

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/sprint-r6-temporal-edge-scout` |
| Status | submitted |
| Created | 565b67a |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-r6-temporal-edge-scout --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-r6-temporal-edge-scout --commit-message "Sprint R6 DeepSeek temporal edge-case scout" --message "codex-sprint-r6-temporal-edge-scout ready for Codex review"` |

## Mission

Use an extra DeepSeek Flash worker to scout high-value temporal edge-case tests for R6 without overlapping Claude implementation: find compact cases for same-day fully-past, open-ended clamp, exact-now boundary, stale reference date, and future-date pass-through.

## Scope

### In Scope

Read temporal helpers/routes/tests; create docs/receptionist_review_r6_edge_cases.md or a small non-overlapping proposed test file only if clearly valuable; completion notes for Ariadne.

### Out of Scope

Production code edits, broad harness rewrite, modifying Claude-owned implementation files unless explicitly directed later, Diary UI, taskpane/Word assets, live provider calls, raw mutation date-policy changes.

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

Review artifact inspection, or py_compile/pytest only if a proposed test file is added.

## Merge Criteria

Produces a concise edge-case matrix with expected outcomes and recommends which cases Claude/Ariadne should include now versus defer.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
