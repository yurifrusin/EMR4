# antigravity-sprint153-diary-create-proposal-header-ui

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | c09f3132 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint153-diary-create-proposal-header-ui --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint153-diary-create-proposal-header-ui --commit-message "Sprint 153 diary create-proposal Idempotency-Key UI path" --message "antigravity-sprint153-diary-create-proposal-header-ui ready for Codex review"` |

## Mission

Plan and, after approval, own the diary frontend slice that adds an Idempotency-Key header to the real create-proposal POST using an existing 8+ character client key pattern.

## Scope

### In Scope

Read AGENTS.md, protocol alerts, Sprint 152 closeout/decision docs, docs/diary/diary.js apiFetch/generateEventId/saveBooking create-proposal flow, and review/test_diary_smoke.py if relevant. Produce a plan packet first; implementation should be limited to diary client code/tests only if approved.

### Out of Scope

Do not change backend route behavior, OpenAPI schema, taskpane, booking modal layout, grid geometry, providers, GraphQL, H15/H-series, memory/RAG/GraphRAG, or raw trove material.

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

Plan gate: identify static JS checks and any deterministic UI/review harness checks. Later implementation should run node --check docs/diary/diary.js and focused backend/API tests if client behavior is changed.

## Merge Criteria

Ariadne gets a clear UI/client plan: where the key is generated, why it is 8+ chars, how retries behave, and what tests prove create-proposal calls now satisfy the Sprint 152 readiness precondition.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
