# antigravity-sprint-g1-diary-update-confirm-ux-review

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | a1ba67c |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-g1-diary-update-confirm-ux-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-g1-diary-update-confirm-ux-review --commit-message "Sprint G1 Diary update confirm UX review" --message "antigravity-sprint-g1-diary-update-confirm-ux-review ready for Codex review"` |

## Mission

Plan the visible Diary UX implications of moving appointment update/extension confirmation toward one evidence-gated action grammar shared by human UI and Bernie.

## Scope

### In Scope

docs/diary/diary.js/css smoke-review implications only; update/resize/drag confirmation dialog wording; Bernie extension confirm wording; preserving familiar UI while evidence-gated backend contract changes underneath.

### Out of Scope

Backend implementation; broad redesign; taskpane/Command Centre; auto-mode; GraphRAG; new appointment action types beyond update/extend.

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

Plan first. Later implementation should run node --check, frontend version check if assets change, route-intercepted Diary smoke checks, and full review/test_diary_smoke.py if UI touched.

## Merge Criteria

Plan identifies whether V1/V2 UI can remain mostly unchanged, what copy or selector changes are needed, and how no-confirm-without-evidence remains visible and testable.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
