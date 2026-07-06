# codex-r26-deepseek-neutral-scenario-adversarial-review

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | integrated |
| Created | 6a4099f5 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-r26-deepseek-neutral-scenario-adversarial-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-r26-deepseek-neutral-scenario-adversarial-review --commit-message "R26 DeepSeek neutral scenario adversarial review" --message "codex-r26-deepseek-neutral-scenario-adversarial-review ready for Codex review"` |

## Mission

DeepSeek Flash lane: adversarially review the proposed H-series-to-scenarios bridge for privacy leakage, overclaiming semantic meaning from neutral aggregates, fixture schema drift, and weak deterministic acceptance criteria. Add a review artifact or narrow non-overlapping tests only if useful.

## Scope

### In Scope

docs/adversarial/h_series_scenario_bridge_review_r26.md or narrow tests around source-safe H-derived fixtures; committed H-series docs and scenario harness only

### Out of Scope

raw local_data/ignored JSON, semantic labelling, production routes, frontend UI, live provider calls, database writes

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

Review artifact inspection, plus py_compile/pytest if tests are added

## Merge Criteria

Ariadne receives independent DeepSeek Flash challenge of the bridge before integration

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run: DeepSeek produced `docs/adversarial/h_series_scenario_bridge_review_r26.md`; Ariadne inspected the artifact and incorporated its middle-layer recommendation into the R26 implementation.
- Remaining risks: DeepSeek could not run protocol `handin` because local runtime logs were untracked; `.gitignore` now excludes `orchestration/runtime_logs/`.
