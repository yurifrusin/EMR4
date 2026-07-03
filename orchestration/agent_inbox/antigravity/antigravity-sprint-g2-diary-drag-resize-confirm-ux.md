# antigravity-sprint-g2-diary-drag-resize-confirm-ux

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | superseded |
| Created | 37ed8b2 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-g2-diary-drag-resize-confirm-ux --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-g2-diary-drag-resize-confirm-ux --commit-message "Sprint G2 diary drag resize confirm UX" --message "antigravity-sprint-g2-diary-drag-resize-confirm-ux ready for Codex review"` |

## Mission

Plan the visible Diary UX migration for drag/drop/resize appointment updates to use the G1 update-confirm endpoint behind the scenes without making normal safe edits feel slower or modal-heavy.

## Scope

### In Scope

docs/diary/diary.js handleMoveResize, proposal dialog/identity confirmation plumbing, optimistic/snapback behaviour, error/stale/conflict copy, deterministic review smoke coverage.

### Out of Scope

Backend implementation beyond consuming returned confirm_endpoint/confirm_payload; broad UI redesign; status/cancel/delete; Bernie panel changes except shared helpers if necessary; taskpane/Command Centre.

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

node --check docs/diary/diary.js; review/test_diary_smoke.py focused human move/resize confirm tests and full smoke if touched; frontend version check if assets change.

## Merge Criteria

Safe edits still feel direct; warning/block/stale cases are legible; confirm endpoint is used for human update writes; raw PUT fallback is not silently used for confirm-grade UI.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: none by Antigravity; Ariadne implemented the scoped UI migration directly after Antigravity produced exploration output but no submitted plan artifact.
- Verification run: Ariadne ran `node --check docs\diary\diary.js`, `scripts\check_frontend_versions.py`, focused backend update-confirm suites, the new human drag/resize signed-confirm smoke assertion, full `review\test_diary_smoke.py -q`, and `git diff --check`.
- Remaining risks: edit-form Save remains on the bounded raw PUT compatibility path; a later sprint should migrate it separately.
