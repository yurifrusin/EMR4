# claude-sprint98-bernie-confirm-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | submitted |
| Created | 7c05164 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint98-bernie-confirm-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint98-bernie-confirm-contract --commit-message "Sprint 98 Bernie confirm contract" --message "claude-sprint98-bernie-confirm-contract ready for Codex review"` |

## Mission

Plan the backend/API fix for Sprint 98 so Bernie resolved practitioner names never leak as missing practitioner_id, confirm-ready payloads carry a valid proposal/confirmation token end to end, and Confirm booking cannot fail with generic Not Found for a valid staged proposal.

## Scope

### In Scope

Plan only. Inspect app routers/services/schemas/tests for Bernie supervised booking, slot selection, create-proposal, confirm-Bernie, practitioner/patient resolution, audit, and Sprint 97 interpreter fallback. Propose exact backend contract changes, migrations if any, and focused tests.

### Out of Scope

No frontend edits, no GraphQL/API-spine implementation, no Caller ID, Medicare/OPV/PVM, SMS, billing, taskpane, Command Centre, production GCP changes, or autonomous booking. Do not code before approval.

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

Plan must include focused pytest targets proving resolved practitioner_id is present, valid confirm-ready proposal token confirms, stale/invalid token returns precise non-generic error, no booking write before confirm, and audit remains staff-confirmed.

## Merge Criteria

Ariadne accepts the plan only if it preserves explicit staff confirmation, explains the Not Found root cause hypothesis, names files in/out of scope, and keeps the fix small enough to complete before Sprint 99 API-spine planning.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
