# codex-sprint105-bernie-turn-invariants

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/sprint105-bernie-turn-invariants` |
| Status | queued |
| Created | 50b28c8 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint105-bernie-turn-invariants --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint105-bernie-turn-invariants --commit-message "Dispatch Sprint 105 turn invariant plan" --message "codex-sprint105-bernie-turn-invariants ready for Codex review"` |

## Mission

Plan Sprint 105 independent invariant/review harness for Bernie typed turns, proposal freshness evidence, and confirmation staleness. Treat this as the acceptance model for backend and UI plans before implementation release.

## Scope

### In Scope

Plan packet first only. In scope for eventual implementation planning: tests/test_bernie_sprint104_state_memory.py or a new tests/test_bernie_sprint105_turn_contract.py, review/test_diary_smoke.py, and orchestration notes if needed. Define invariants for turn id uniqueness/order, event kind transitions, immutable reference date, no-slot typed suggestions, candidate/proposal snapshot freshness, confirmation evidence matching current proposal, stale navigation/refresh blocking confirm, and no mutation before authorized confirmation.

### Out of Scope

No production code before plan approval. Do not duplicate Claude backend implementation or Antigravity UI implementation, launch broad API-spine review, introduce a statechart runtime dependency, or implement auto-mode/voice/Caller ID/Medicare verification.

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

Plan must propose concrete backend and UI harness tests, fixture names, expected failure modes from Sprint 104 live testing, and acceptance gates that Ariadne can use to review Claude and Antigravity submissions.

## Merge Criteria

Plan is mergeable when it provides a transition/event table, test matrix, stale-confirmation failure fixtures, merge/rejection criteria for worker submissions, and clear boundaries that avoid changing production code during the plan gate.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
