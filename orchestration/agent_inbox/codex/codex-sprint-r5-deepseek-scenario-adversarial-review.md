# codex-sprint-r5-deepseek-scenario-adversarial-review

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/sprint-r5-scenario-review` |
| Status | integrated |
| Created | 2687ef6 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-r5-deepseek-scenario-adversarial-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-r5-deepseek-scenario-adversarial-review --commit-message "Sprint R5 DeepSeek scenario adversarial review" --message "codex-sprint-r5-deepseek-scenario-adversarial-review ready for Codex review"` |

## Mission

Use a second DeepSeek Flash worker in place of recuperating Claude to adversarially review scenario-promotion boundaries: identify which R3/R4 fixtures should stay natural-language memory, which can become executable now, and add or propose narrow validator/replay tests without overlapping the implementation lane's production edits.

## Scope

### In Scope

Read tests/fixtures/bernie_scenarios, tests/bernie_scenarios loader/replay, R3/R4 docs, and submit a review artifact or focused tests under a distinct filename if useful.

### Out of Scope

No production app code; no diary UI; no broad harness rewrite; no direct raw mutation endpoint policy changes.

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

py_compile any changed tests/harness; pytest scenario integrity/replay subsets if tests change; git diff --check; or explicit review artifact if no code changes.

## Merge Criteria

Provides independent evidence that promoted scenarios match real harness capabilities and flags any fixture that should remain corpus memory until a later sprint.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:

## Integration Outcome

Integrated by Ariadne as `docs/receptionist_review_r5_adversarial.md`. The review classified R3/R4 fixtures into executable-now, corpus-memory, and future-harness-work buckets, and confirmed that absolute past-date normalization is the only clean R5 executable promotion under the current harness.
