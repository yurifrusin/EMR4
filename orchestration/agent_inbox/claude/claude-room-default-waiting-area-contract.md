# claude-room-default-waiting-area-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 3665aef |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-room-default-waiting-area-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-room-default-waiting-area-contract --commit-message "Dispatch Sprint 23 backend default waiting-area contract" --message "Room default waiting-area backend contract ready for Codex review"` |

## Mission

Plan, then after approval enforce a safe backend invariant that every active room has a valid active default waiting area for its practice/location, defaulting to the active waiting area with display_order 0 when no explicit default is supplied.

## Scope

### In Scope

Backend Room/WaitingArea models, schemas, resource-admin routes/services, seed/dev-data repair path, migrations only if required, and focused pytest coverage for create/edit/archive/default fallback behavior.

### Out of Scope

Diary frontend UI, taskpane/Command Centre, appointment booking/status semantics beyond preserving existing consumers, broad roster redesign, production data migration outside a minimal invariant-preserving migration if required.

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

Plan packet first; after approval run focused diary resource-admin/default-waiting-area pytest coverage, backend Tier-1 check, full pytest if invariant touches shared fixtures, and git diff --check.

## Merge Criteria

Active rooms cannot persist with no valid active default waiting area when an active waiting area exists; default fallback is deterministic by display_order then stable id/name; archiving a default area safely reassigns affected rooms or blocks with a clear contract; cross-practice/location defaults remain impossible.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
