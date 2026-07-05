# codex-sprint-r25-deepseek-sampling-harness-scaffold

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | queued |
| Created | 25d9ab5 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-r25-deepseek-sampling-harness-scaffold --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-r25-deepseek-sampling-harness-scaffold --commit-message "Sprint R25 DeepSeek sampling harness scaffold" --message "codex-sprint-r25-deepseek-sampling-harness-scaffold ready for Codex review"` |

## Mission

DeepSeek Flash worker replacing capped Claude: implement a default-disabled no-write provider sampling harness scaffold that can feed configured provider-style sample outputs into the R24 gate without making live calls in tests.

## Scope

### In Scope

app/services/ai/evals/manifest_eval.py or a new eval module under app/services/ai/evals, focused tests, orchestration docs if needed

### Out of Scope

Actual live Gemini/Vertex calls in tests, production prompt wiring, frontend/Diary UI, database migrations, real appointment writes, route changes, secrets or service-account setup

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

Run py_compile and focused pytest for the sampling harness tests if possible

## Merge Criteria

Ariadne can integrate a deterministic scaffold proving default-disabled/no-write/no-live-call behavior and sample evaluation through the R24 gate

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
