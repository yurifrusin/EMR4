# claude-sprint153-diary-create-proposal-header-readiness

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | c09f3132 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint153-diary-create-proposal-header-readiness --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint153-diary-create-proposal-header-readiness --commit-message "Sprint 153 diary create-proposal header readiness contract" --message "claude-sprint153-diary-create-proposal-header-readiness ready for Codex review"` |

## Mission

Review and plan the backend/API contract for making the real diary create-proposal caller send an 8+ character Idempotency-Key without changing create-proposal runtime minLength enforcement.

## Scope

### In Scope

Read AGENTS.md, protocol alerts, Sprint 152 decision docs/tests/closeout, docs/diary/diary.js create-proposal caller, app/routers/appointments.py create-proposal normalizer, and relevant API-spine tests. Produce a plan/review packet identifying exact client/header behavior, tests, and no-route-change boundaries.

### Out of Scope

Do not enforce runtime minLength, do not change OpenAPI schema, do not alter confirmation ledger semantics, do not touch raw compatibility routes, providers, GraphQL, H15/H-series, memory/RAG/GraphRAG, or historical diary trove material.

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

Plan gate only: list exact tests for Ariadne/implementation, likely node --check docs/diary/diary.js plus focused API-spine/create-proposal tests and review harness if relevant.

## Merge Criteria

Ariadne can implement or release implementation with clear acceptance: diary create-proposal sends an 8+ char key, backend runtime remains non-blank-only, and tests prove no write/replay authority change.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
