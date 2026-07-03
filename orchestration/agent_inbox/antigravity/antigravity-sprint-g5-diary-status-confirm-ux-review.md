# antigravity-sprint-g5-diary-status-confirm-ux-review

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | 40a0e33 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-g5-diary-status-confirm-ux-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-g5-diary-status-confirm-ux-review --commit-message "Sprint G5 Diary status confirm UX review" --message "antigravity-sprint-g5-diary-status-confirm-ux-review ready for Codex review"` |

## Mission

Plan the visible Diary UX review for routing human status-only changes through signed status-confirm while preserving current status affordances, waiting-room/check-in behaviour, and modal status-after-create/update separation.

## Scope

### In Scope

docs/diary status-only controls and deterministic review smoke suggestions; user-visible status proposal/confirm wording and failure handling; no production code during plan gate.

### Out of Scope

Backend implementation; create/edit detail confirm routes; cancel/delete; diary grid geometry; waiting-room redesign; taskpane; Command Centre; broad Bernie grammar; GraphRAG.

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

Plan packet only during plan gate. Later implementation should run node --check and focused review/test_diary_smoke.py status-only route-intercept checks if Diary assets change.

## Merge Criteria

Ariadne accepts the plan only if it preserves existing visible status workflows, proves no raw status PATCH from signed-capable status-only controls, and does not change create/edit/cancel/delete UX.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
