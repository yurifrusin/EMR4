# claude-sprint-n3-unified-evidence-gated-confirm-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 3c751c8 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-n3-unified-evidence-gated-confirm-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-n3-unified-evidence-gated-confirm-contract --commit-message "Sprint N3 unified evidence gated confirm contract" --message "claude-sprint-n3-unified-evidence-gated-confirm-contract ready for Codex review"` |

## Mission

Plan Sprint N3 backend/domain work for a unified evidence-gated confirm/review affordance contract. Define the diary-domain conditions under which a booking proposal may expose confirm-grade UI, preserving that stale, advisory-only, model-only, no-slot, or schedule-blocked state cannot show confirm/review affordances.

## Scope

### In Scope

Plan only first. app/services/diary and app/services/bernie domain contracts, reception policy evidence fields, tests for confirm-grade vs advisory-only state, and compatibility facades as needed. Keep route/UI changes scoped as future integration unless explicitly approved after plan review.

### Out of Scope

No implementation before plan gate, no GraphRAG/K1, no persisted server-side sessions, no auto-mode, no booking write-path changes, no broad API review, no migration, no UI redesign.

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

Plan packet first. Later implementation should run focused diary/bernie domain tests, compileall for app/services/diary app/services/bernie, review smoke checks if any UI contract is touched, and git diff --check.

## Merge Criteria

A precise implementation plan that defines one backend-owned evidence gate for confirm-grade booking UI and prevents stale/advisory/model-only state from authorizing confirmation.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
