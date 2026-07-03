# claude-sprint-v2-bernie-tool-intent-ui-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 50b9936 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-v2-bernie-tool-intent-ui-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-v2-bernie-tool-intent-ui-contract --commit-message "Sprint V2 Bernie tool intent UI contract" --message "claude-sprint-v2-bernie-tool-intent-ui-contract ready for Codex review"` |

## Mission

Plan the backend/domain contract for wiring the V1 Bernie tool-intent route into the Diary Ask Bernie flow, preserving non-mutating proposal semantics and staff-confirmed write authority.

## Scope

### In Scope

Diary Ask Bernie request routing to /appointments/proposals/bernie/tool-intent for explicit appointment extension/edit intents; typed response handling; proposal/confirm boundary; source attribution; focused backend/UI contract tests.

### Out of Scope

Auto-mode or direct writes; new persisted PHI/session tables; GraphRAG changes; taskpane/Command Centre; broad API rewrite; unsupported diary edit intents beyond extension unless explicitly planned as future-safe stubs.

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

Plan first. Later implementation should run py_compile, node --check, frontend version check if assets change, focused Bernie tool-intent/update/confirm tests, and deterministic Diary smoke tests for visible UX.

## Merge Criteria

Plan identifies the exact route/UI contract, files touched, no-write/no-confirm-bypass invariants, and how visible copy remains friendly without becoming authoritative.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
