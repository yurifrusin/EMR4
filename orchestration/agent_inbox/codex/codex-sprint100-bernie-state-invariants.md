# codex-sprint100-bernie-state-invariants

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/sprint100-bernie-state-invariants` |
| Status | queued |
| Created | 00f54e6 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint100-bernie-state-invariants --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint100-bernie-state-invariants --commit-message "Sprint 100 Bernie state invariant review" --message "codex-sprint100-bernie-state-invariants ready for Codex review"` |

## Mission

Independently plan the acceptance and invariant harness for the Bernie state machine using Yuri's live screenshots as failure fixtures.

## Scope

### In Scope

Read-only plan/review packet first only; inspect current Bernie backend, diary UI, smoke harness, release gates, and Sprint 99 closeout; propose model-based or transition-table tests; define invariants for reference-date immutability, candidate snapshot reuse, UI state cleanup, confirmation gating, and after-hours temporal logic.

### Out of Scope

Production code edits before explicit plan approval; integration; live provider/browser manual testing; broad API-spine implementation beyond noting reusable modelling lessons.

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

Plan must include concrete acceptance gates, transition table, failure fixtures, required backend/UI test names, and resubmission criteria for Claude and Antigravity plans.

## Merge Criteria

Ariadne can accept the plan only if it would have failed the current shipped behaviour and can be automated cheaply through backend tests and deterministic diary review tests.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
