# codex-sprint-r24-deepseek-provider-dry-run-gate-implementation

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | queued |
| Created | 4185731 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-r24-deepseek-provider-dry-run-gate-implementation --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-r24-deepseek-provider-dry-run-gate-implementation --commit-message "Sprint R24 DeepSeek provider dry-run gate implementation" --message "codex-sprint-r24-deepseek-provider-dry-run-gate-implementation ready for Codex review"` |

## Mission

DeepSeek Flash worker replacing capped Claude: implement a no-live-provider, no-write provider-readiness dry-run gate that evaluates model-style sample outputs against the manifest, scenario, and frame-shape validators.

## Scope

### In Scope

app/services/ai/evals/manifest_eval.py, tests/test_bernie_manifest_receptionist_scenarios.py or a new focused test module, orchestration docs if needed

### Out of Scope

Live Gemini/Vertex calls, production prompt wiring, frontend/Diary UI, database migrations, real appointment writes, route changes

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

Run py_compile and focused pytest for manifest eval/dry-run tests if possible

## Merge Criteria

Ariadne can integrate deterministic provider-style dry-run coverage that proves sampled outputs remain non-authoritative and cannot mutate state

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
