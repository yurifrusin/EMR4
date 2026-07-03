# codex-sprint-n7-session-outcome-invariants

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | queued |
| Created | f46cb2f |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-n7-session-outcome-invariants --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-n7-session-outcome-invariants --commit-message "Sprint N7 session outcome invariants" --message "codex-sprint-n7-session-outcome-invariants ready for Codex review"` |

## Mission

Plan adversarial invariant coverage for Bernie server-owned outcome events and session-bound confirmation: stale revision rejection, idempotency, no PHI-heavy browser/server event payloads, and no confirm from mismatched or stale session evidence.

## Scope

### In Scope

Plan first only. tests around app/services/bernie/session_store.py and appointments route outcomes, review/test_diary_smoke.py contract checks if UI changes, and orchestration review notes. This is a Codex worker/invariant lane, not primary implementation.

### Out of Scope

No production code before plan approval, no database migration, no GraphRAG/practice-knowledge wiring, no auto-mode, no broad UI redesign, no duplicate ownership of Claude backend implementation or Antigravity UI implementation.

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

Plan must name focused backend and Diary smoke checks proving fail-closed confirmation, stale-session conflicts, idempotent outcome event handling, no local/session storage PHI, and no raw transcript persistence.

## Merge Criteria

Codex can accept the plan when it gives concrete tests/acceptance gates that prevent N7 from becoming a second client-side state machine or a PHI-heavy transcript store.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
