# claude-sprint-n9-bernie-session-coordinate-ui-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | superseded |
| Created | 0174ffe |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-n9-bernie-session-coordinate-ui-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-n9-bernie-session-coordinate-ui-contract --commit-message "Sprint N9 Bernie session coordinate UI contract" --message "claude-sprint-n9-bernie-session-coordinate-ui-contract ready for Codex review"` |

## Mission

Plan the UI/API contract for Diary calls to carry N8 server-session coordinates and backend-stamped session_binding through the Bernie flow.

## Scope

### In Scope

Plan only first. docs/diary/diary.js, review/test_diary_smoke.py, and backend request/response contract inspection. Keep recommendations bounded and compatible with N8.

### Out of Scope

No production code before plan approval. No backend migration, GraphRAG, auto-mode, taskpane, Command Centre, broad UI redesign, or persisted session table.

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

Plan should specify focused Diary smoke assertions, node check, and backend regression checks if any backend code is touched.

## Merge Criteria

Plan preserves backend authority over session_binding/freshness and browser presentational role, with clear stale-conflict user behaviour.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: none by Claude; Claude headless returned a session-limit 429 before submitting a plan.
- Verification run: superseded by Ariadne/Codex N9 implementation and verification.
- Remaining risks: none from this lane; retry Claude on a later sprint once quota is available if deeper review is needed.
