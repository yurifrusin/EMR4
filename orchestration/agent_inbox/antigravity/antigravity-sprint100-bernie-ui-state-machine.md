# antigravity-sprint100-bernie-ui-state-machine

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | 00f54e6 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint100-bernie-ui-state-machine --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint100-bernie-ui-state-machine --commit-message "Sprint 100 Bernie UI state machine" --message "antigravity-sprint100-bernie-ui-state-machine ready for Codex review"` |

## Mission

Plan a diary-side Bernie session state machine that keeps instruction, interpretation, candidate snapshot, selected slot, diary preview, choose-another-time, and confirmed states separate.

## Scope

### In Scope

Plan packet first only; docs/diary/diary.js, docs/diary/diary.css, docs/diary/diary.html, review/test_diary_smoke.py; explicit UI state object; immutable session reference date; candidate snapshot reuse; post-confirm panel cleanup; compact Details behaviour; auto-preview toggle boundary.

### Out of Scope

Production code before explicit plan approval; backend schema implementation except requested contract fields; broad diary redesign; phone or voice integrations; bypassing staff confirmation.

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

Plan must specify deterministic UI tests for today-after-3 after clinic hours, tomorrow candidate selection without jumping two days, Choose another time returning to the same candidate snapshot, confirm success cleanup, stale confirm recovery, and asset version checks.

## Merge Criteria

Ariadne can accept the plan only if it prevents diaryDate from becoming semantic input inside an existing Bernie session, treats candidate cards as absolute snapshots, and leaves ordinary receptionist UI compact and calm.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
