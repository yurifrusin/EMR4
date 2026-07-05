# claude-sprint-r3-stale-session-revision-hardening

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | superseded |
| Created | b146f15 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-r3-stale-session-revision-hardening --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-r3-stale-session-revision-hardening --commit-message "Sprint R3: Stale Session Revision Hardening" --message "claude-sprint-r3-stale-session-revision-hardening ready for Codex review"` |

## Mission

Harden Bernie session/clarification append handling so stale client revision coordinates cannot merge, confirm, or resurrect outdated appointment context. Implement server-side fail-closed semantics with focused tests.

## Scope

### In Scope

Backend Bernie interpret/session context handling; stale revision/session append guards; focused tests for clarification replies, intent switches, stale browser/two-receptionist flows where practical; update narrow docs/closeout notes if needed.

### Out of Scope

Diary UI redesign, Word/taskpane changes, GitHub Pages assets, live Gemini/Vertex calls, broad patient collision source hardening unless directly needed for stale-session safety, GraphRAG/MCP/indexer automation, persisted session table redesign.

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

py_compile touched backend/tests; focused pytest for Bernie clarification/session/interpret/scenario integrity surfaces; git diff --check; no browser/Pages checks unless frontend files change.

## Merge Criteria

Stale revision/client context is rejected or safely ignored before merge/confirm; fresh clarification flows from R2 still pass; tests prove no appointment/audit mutation from stale replies; branch submits through protocol with review packet.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Superseded during Sprint R3 because Claude hit the session limit before plan submission. Ariadne used two DeepSeek Flash lanes plus Antigravity/Gemini review instead; no Claude branch changes were integrated.

- Files changed: none
- Verification run: none by Claude
- Remaining risks: retry Claude on a future sprint only if deeper architecture review is needed
