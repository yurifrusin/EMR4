# claude-sprint-g5-status-confirm-route-migration

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | superseded |
| Created | 40a0e33 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-g5-status-confirm-route-migration --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-g5-status-confirm-route-migration --commit-message "Sprint G5 status confirm route migration" --message "claude-sprint-g5-status-confirm-route-migration ready for Codex review"` |

## Mission

Plan a narrow migration for human Diary status-only transitions from direct PATCH /appointments/{id}/status to a signed status-confirm route, preserving existing status proposal semantics and waiting-area behaviour.

## Scope

### In Scope

app/schemas/appointments.py status proposal/confirm schemas; app/routers/appointments.py status proposal/confirm route and helpers; tests for status confirm evidence, stale/tampered evidence, warning/audit boundaries; no production code during plan gate.

### Out of Scope

Create/edit detail confirms already handled in G1-G4; cancel/delete; broad Bernie grammar; persisted sessions; GraphRAG; visual redesign; taskpane; Command Centre; raw PATCH endpoint removal.

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

Plan packet only during plan gate. Later implementation should run py_compile, focused appointment status/audit/waiting-area tests, node --check if Diary changes, and deterministic diary smoke for status-only controls.

## Merge Criteria

Ariadne accepts the plan only if status confirm is typed, signed, revalidated, no-write on stale/tampered evidence, keeps waiting-area semantics explicit, and does not affect create/edit/cancel/delete flows.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
