# claude-sprint134-bernie-create-confirm-idempotency-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | c3593d09 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint134-bernie-create-confirm-idempotency-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint134-bernie-create-confirm-idempotency-contract --commit-message "Add Bernie create-confirm idempotency contract" --message "Sprint 134 Claude backend/test contract ready for Codex review"` |

## Mission

Plan-gated backend/test contract lane for Sprint 134. Review the Sprint 133 preflight and propose/implement only the guarded Bernie create-confirm idempotency route-test contract before any route wiring.

## Scope

### In Scope

Read Sprint 133 preflight, confirm_bernie_create_proposal, Bernie route outcome/session tests, and staff create-confirm idempotency tests. Add or plan guarded/static tests and orchestration doc coverage for confirm-bernie idempotency route-test contract, especially no-double-session-event replay cases.

### Out of Scope

Do not wire Idempotency-Key to confirm-bernie. Do not modify provider, GraphQL, H15/H-series, memory/RAG/GraphRAG, update/status/delete/raw/proposal-only routes, or live provider behavior.

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

Run focused py_compile and pytest for the new contract tests plus existing Bernie confirm/session route outcome tests if implementation is approved.

## Merge Criteria

Contract names the confirm-bernie route, keeps route unwired, records replay/session-event cases, and passes focused tests without opening closed gates.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
