# claude-sprint-g3-edit-modal-update-confirm-migration

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | integrated |
| Created | 8cf67ca |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-g3-edit-modal-update-confirm-migration --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-g3-edit-modal-update-confirm-migration --commit-message "Sprint G3 edit modal update confirm migration" --message "claude-sprint-g3-edit-modal-update-confirm-migration ready for Codex review"` |

## Mission

Plan how to migrate the Diary edit modal's appointment-detail Save path from raw PUT to the signed update-confirm route while keeping status PATCH semantics separate and preserving the existing modal UX.

## Scope

### In Scope

docs/diary/diary.js saveBooking edit-mode appointment detail update flow; app/routers/appointments.py/app/schemas/appointments.py only if a small contract adjustment is required; tests proving edit modal update writes through update-confirm and status PATCH remains separate.

### Out of Scope

Drag/drop/resize already covered by G2; status confirm grammar; cancel/delete/create migration; raw PUT removal; visual redesign; persisted PHI/session tables; GraphRAG; taskpane/Command Centre.

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

py_compile touched backend files; node --check docs/diary/diary.js; scripts/check_frontend_versions.py if assets change; focused appointment update/confirm tests; focused edit-modal review smoke and full review/test_diary_smoke.py if docs/diary changes.

## Merge Criteria

Plan preserves edit modal UX, separates appointment detail update from status PATCH, uses signed update-confirm evidence for edit-mode detail writes, keeps raw PUT as bounded compatibility, and adds no broad action grammar.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - Plan-only lane submitted `orchestration/agent_inbox/codex/plan-claude-claude-sprint-g3-edit-modal-update-confirm-migration.md`.
  - Ariadne implemented the accepted plan in `docs/diary/diary.js`, `docs/diary/diary.html`, and `review/test_diary_smoke.py`.
- Verification run:
  - `node --check docs\diary\diary.js`
  - `.\.venv\Scripts\python.exe -m py_compile scripts\agent_worktrees.py`
  - `.\.venv\Scripts\pytest.exe review\test_diary_smoke.py -q -k "edit_modal_uses_signed_update_confirm_before_status_patch or edit_modal_does_not_patch_status_when_signed_update_confirm_fails or human_drag_resize_uses_signed_update_confirm_route"`
  - `.\.venv\Scripts\pytest.exe review\test_diary_smoke.py --junitxml=review\diary-review.xml -q`
- Remaining risks:
  - Raw `PUT /appointments/{id}` remains as a bounded compatibility fallback when no signed confirm envelope is present. The edit modal now uses signed confirm when the backend provides it.
