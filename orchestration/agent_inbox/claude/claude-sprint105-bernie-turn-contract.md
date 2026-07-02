# claude-sprint105-bernie-turn-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | submitted |
| Created | 50b28c8 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint105-bernie-turn-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint105-bernie-turn-contract --commit-message "Dispatch Sprint 105 backend turn contract plan" --message "claude-sprint105-bernie-turn-contract ready for Codex review"` |

## Mission

Plan Sprint 105 backend/API work for Bernie typed turn contract and confirmation evidence. Close the gap between UI-tolerated session metadata and backend-owned evidence: explicit turn ids, typed turn/event schemas, candidate/proposal freshness ids or hashes, and confirmation staleness checks before write.

## Scope

### In Scope

Plan packet first only. In scope for the eventual implementation plan: app/schemas/appointments.py, app/routers/appointments.py, app/services/bernie_booking_interpreter.py, app/services/bernie_slot_normalizer.py or a new narrow Bernie session/evidence helper if justified, and focused backend tests. Define typed inputs for session_id/turns, stable turn ids, event kind vocabulary for staff instruction, Bernie clarification, no-slot suggestion selection, candidate selection, proposal preview, and confirmation. Preserve patient recognition separate from patient details verification, immutable request_reference_date, deterministic slot search, and no privileged agent write path.

### Out of Scope

No production code before plan approval. Do not implement limited Bernie auto-mode, voice/headset, Caller ID, Medicare/HI/PVM/OPV verification, broad root-to-branch API redesign, GraphQL/context-graph migration, or a statechart runtime dependency. Do not weaken staff confirmation or add agent-only writes.

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

Plan must name backend tests for accepted turn payloads, rejected stale/malformed turn ids, typed no-slot suggestion event handling, candidate/proposal freshness mismatch blocking confirmation, immutable reference date across turns, no mutation before confirm, and no live-provider dependency.

## Merge Criteria

Plan is mergeable when it states the exact API/schema boundary, migration/backcompat strategy for existing Diary calls, risks/dissent, focused tests, and how confirmation evidence blocks stale proposals without breaking current Sprint 104 live flow.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
