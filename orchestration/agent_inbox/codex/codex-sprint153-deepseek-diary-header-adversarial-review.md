# codex-sprint153-deepseek-diary-header-adversarial-review

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/sprint153-deepseek-diary-header-adversarial-review` |
| Status | queued |
| Created | c09f3132 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint153-deepseek-diary-header-adversarial-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint153-deepseek-diary-header-adversarial-review --commit-message "Sprint 153 DeepSeek diary header adversarial review" --message "codex-sprint153-deepseek-diary-header-adversarial-review ready for Codex review"` |

## Mission

DeepSeek Flash adversarial lane: challenge the plan to add Idempotency-Key emission to diary create-proposal. Look for retry semantics, key stability, test gaps, and any accidental runtime minLength or replay-authority creep.

## Scope

### In Scope

Read AGENTS.md, protocol alerts, Sprint 152 decision docs/tests, docs/diary/diary.js create-proposal flow, app/routers/appointments.py create-proposal normalizer, and relevant tests. Produce a review artifact under orchestration/agent_inbox/codex/review-deepseek-sprint153-diary-create-proposal-header-readiness.md.

### Out of Scope

Do not change app route behavior, OpenAPI schema, migrations, diary layout, taskpane, providers, GraphQL, H15/H-series, memory/RAG/GraphRAG, local_data, or raw trove material.

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

Run rg/static checks and git diff --check if editing only a review artifact. Recommend exact tests Ariadne should run.

## Merge Criteria

Review artifact names blockers or says no blockers, with specific guidance on key generation/retry semantics and readiness tests.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
