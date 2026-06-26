# codex-bernie-slot-flow-review-harness

| Item | Value |
|---|---|
| To | codex |
| Role | codex-worker |
| Worker Name | Cicero |
| Worker Branch | `codex/bernie-slot-flow-review-harness` |
| Branch | `codex/bernie-slot-flow-review-harness` |
| Status | submitted |
| Created | 442f81f |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-bernie-slot-flow-review-harness --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-bernie-slot-flow-review-harness --commit-message "Dispatch Sprint 43 Bernie slot flow harness" --message "Sprint 43 dispatched to Codex worker"` |

## Mission

Create a deterministic, cost-conscious review harness for the backend Bernie command-normalize-search-select chain before adding the final appointment write bridge.

## Scope

### In Scope

Plan first. After approval, add focused backend test/review harness coverage, likely in tests/test_bernie_slot_flow_review_harness.py or adjacent test helpers, exercising normalize endpoint, normalized search endpoint, slot-selection proposal endpoint, conflict/no-match paths, no appointment/audit writes, and no LLM/provider calls. Small testability-only helper extraction is allowed only if justified.

### Out of Scope

Diary UI, taskpane, Command Centre, Gemini/LLM parsing, autonomous Bernie runtime, final appointment write/confirmation bridge, audit mutation, migrations, billing, SMS, resource admin, broad refactors, and unrelated test hygiene.

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

py_compile any touched Python; focused pytest for the new harness; adjacent Bernie slot endpoint tests if production code is touched; source/runtime proof of no appointment/audit writes and no LLM/provider calls; git diff --check.

## Merge Criteria

Plan packet includes Role codex-worker, Worker Name Cicero, and Worker Branch codex/bernie-slot-flow-review-harness; implementation is backend/test-harness only, deterministic, non-mutating, non-LLM, and keeps product behavior unchanged unless explicitly justified.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `orchestration/agent_inbox/codex/plan-codex-codex-bernie-slot-flow-review-harness.md`; `orchestration/agent_inbox/codex/codex-bernie-slot-flow-review-harness.md`.
- Verification run: Plan-gate only; no production code or tests touched. Ran packet intake via `python scripts\agent_worktrees.py handin --agent codex` and inspected required coordination files.
- Remaining risks: Implementation not started; awaiting explicit `complete sprint task` approval. Future implementation must prove no appointment/audit writes and no LLM/provider calls.
