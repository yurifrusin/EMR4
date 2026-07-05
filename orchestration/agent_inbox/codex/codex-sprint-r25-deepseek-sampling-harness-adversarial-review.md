# codex-sprint-r25-deepseek-sampling-harness-adversarial-review

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | integrated |
| Created | 25d9ab5 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-r25-deepseek-sampling-harness-adversarial-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-r25-deepseek-sampling-harness-adversarial-review --commit-message "Sprint R25 DeepSeek sampling harness adversarial review" --message "codex-sprint-r25-deepseek-sampling-harness-adversarial-review ready for Codex review"` |

## Mission

Second DeepSeek Flash lane: independently review the R25 sampling harness scaffold for accidental live-call, write-authority, PHI logging, provider metadata spoofing, and sample-evaluation bypass risks.

## Scope

### In Scope

adversarial review artifact or non-overlapping tests around default-disabled sampling harness and provider metadata

### Out of Scope

Actual live AI calls, production prompt wiring, frontend UI, DB/migrations, mutation routes, secrets or service-account setup

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

Return focused pytest or precise review artifact; run py_compile/pytest if files are changed

## Merge Criteria

Ariadne receives independent adversarial review of the no-write sampling scaffold without overlapping implementation unnecessarily

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `docs/adversarial/sampling_harness_adversarial_review_r25.md`, `tests/test_sampling_harness_adversarial_review.py`, and `app/services/ai/evals/manifest_eval.py` hardening for provider-style `allow_write=True`.
- Verification run: focused R25/R24 pytest passed (73 tests), broader manifest regression passed (109 tests), `py_compile` passed, and `git diff --check` passed.
- Remaining risks: frameless safe-looking dicts still pass generic safety checks; consider making absent `frame_kind` malformed in a future hardening sprint if provider-output risk increases.
