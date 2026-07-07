# antigravity-sprint134-bernie-create-confirm-idempotency-acceptance

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | c3593d09 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint134-bernie-create-confirm-idempotency-acceptance --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint134-bernie-create-confirm-idempotency-acceptance --commit-message "Review Bernie create-confirm idempotency acceptance" --message "Sprint 134 Antigravity acceptance review ready for Codex review"` |

## Mission

Plan-gated Antigravity/Gemini lane for Sprint 134. Review the planned Bernie create-confirm idempotency route-test contract from a receptionist/domain acceptance perspective.

## Scope

### In Scope

Read Sprint 133 preflight, confirm-bernie route behavior, Bernie route outcome/session tests, and staff create-confirm idempotency boundary. Produce a review or test-design artifact covering staff confirmation, calm failure/replay behavior, session-event duplicate risks, and which UI/user-facing semantics must not change.

### Out of Scope

Do not implement route wiring. Do not change diary UI unless Codex explicitly approves a later implementation packet. Do not open providers, GraphQL mutations, H15/H-series, memory/RAG/GraphRAG, update/status/delete/raw/proposal-only routes, or live smoke gates.

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

Plan/review artifact only unless implementation is separately approved; if files are changed, run markdown/static tests requested by Codex.

## Merge Criteria

Review artifact clearly identifies acceptance risks and confirms Sprint 134 can remain a backend/test contract without user-facing behavior changes.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
