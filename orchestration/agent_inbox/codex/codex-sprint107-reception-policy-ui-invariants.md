# codex-sprint107-reception-policy-ui-invariants

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | queued |
| Created | 0beddab |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint107-reception-policy-ui-invariants --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint107-reception-policy-ui-invariants --commit-message "sprint107 reception policy ui invariants" --message "codex-sprint107-reception-policy-ui-invariants ready for Codex review"` |

## Mission

Plan-gated Sprint 107 Codex worker lane: review and specify invariant/harness changes needed for Diary consumption of Bernie reception_policy/reception_context. Focus on preventing logically false UI copy while preserving existing booking state-machine behavior.

## Scope

### In Scope

review/test_diary_smoke.py, tests or small harness helpers if needed, orchestration plan/review artifacts; read-only analysis of docs/diary/diary.js and app route contracts

### Out of Scope

Production backend changes, database migrations, broad UI redesign, implementation in Antigravity-owned docs/diary runtime files unless Ariadne explicitly reassigns after plan approval

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

Submit a plan first. Proposed checks should cover candidate search with advisory future booking, roster_unavailable/no_practitioner_schedule, true search_ran_no_candidates, stale/older conversation display stability, and backward-compatible responses without reception_policy.

## Merge Criteria

Plan must name exact assertions and fixtures/intercepts, avoid duplicating Antigravity UI implementation, and give Ariadne clear acceptance gates before implementation.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
