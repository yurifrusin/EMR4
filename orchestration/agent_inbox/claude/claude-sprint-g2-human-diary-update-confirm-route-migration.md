# claude-sprint-g2-human-diary-update-confirm-route-migration

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 37ed8b2 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-g2-human-diary-update-confirm-route-migration --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-g2-human-diary-update-confirm-route-migration --commit-message "Sprint G2 human diary update confirm route migration" --message "claude-sprint-g2-human-diary-update-confirm-route-migration ready for Codex review"` |

## Mission

Plan how to migrate human Diary drag/drop/resize appointment updates from raw PUT to the signed update-confirm route introduced in G1 while preserving the existing fast edit UX and raw PUT compatibility boundary.

## Scope

### In Scope

app/routers/appointments.py update proposal/confirm contracts if small additions are needed; docs/diary/diary.js handleMoveResize/showStatusProposalDialog update flow; focused backend/UI tests proving human updates can use confirm evidence; no-write-before-confirm and stale/conflict handling.

### Out of Scope

Broad status/cancel/delete grammar; Bernie auto-mode; persisted PHI session tables; GraphRAG; taskpane/Command Centre; visual redesign of diary grid/cards; removing raw PUT compatibility endpoint this sprint.

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

py_compile touched backend files; node --check docs/diary/diary.js; scripts/check_frontend_versions.py if Diary assets change; focused appointment update/proposal tests; review/test_diary_smoke.py relevant drag/drop/resize and full smoke if touched.

## Merge Criteria

Plan names exact route/payload changes, preserves fast human edit UX, blocks stale/tampered/mismatched confirm evidence, keeps raw PUT as explicit bounded compatibility, and avoids layout changes.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
