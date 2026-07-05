# codex-sprint-r12-deepseek-diary-reason-code-ui-implementation

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | accepted |
| Created | 92c3abc |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-r12-deepseek-diary-reason-code-ui-implementation --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-r12-deepseek-diary-reason-code-ui-implementation --commit-message "Sprint R12 DeepSeek diary reason-code UI implementation" --message "codex-sprint-r12-deepseek-diary-reason-code-ui-implementation ready for Codex review"` |

## Mission

Plan then implement first-party Diary reason-code controls for cancel/status flows using the R11 nullable backend substrate.

## Scope

### In Scope

Plan gate first; after approval likely docs/diary/diary.html, docs/diary/diary.js, docs/diary/diary.css, review smoke tests if applicable, and generated/synced docs assets only. Add dropdowns with no preselected default for first-party cancel/status actions, administrative-note privacy copy, and payload status_reason_code threading.

### Out of Scope

Backend migrations/routes, database enum/reference table, making external API reason codes mandatory, changing temporal slot-write guards, Word taskpane patient-file UI.

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

Plan must name exact Diary files and smoke targets; implementation verification should include JS syntax/static checks and focused review/diary smoke where feasible.

## Merge Criteria

First-party Diary cancel/status actions can supply status_reason_code without breaking existing nullable flows; UI copy avoids clinical-detail capture; no unrelated Diary layout churn.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
