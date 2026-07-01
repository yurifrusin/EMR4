# antigravity-sprint98-bernie-booking-loop-ui

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | 7c05164 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint98-bernie-booking-loop-ui --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint98-bernie-booking-loop-ui --commit-message "Sprint 98 Bernie booking loop UI" --message "antigravity-sprint98-bernie-booking-loop-ui ready for Codex review"` |

## Mission

Plan the Diary/Bernie UI repair for Sprint 98 so staff can go back from ready-to-book to choose a different proposed slot, ordinary users do not see raw missing practitioner_id once the practitioner name has been resolved, and confirm errors are calm but diagnostically useful for developers.

## Scope

### In Scope

Plan only. Inspect docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js, review/test_diary_smoke.py, and current Sprint 97 closeout/screenshots. Propose UI states, copy, controls, keyboard/accessibility behaviour, asset versioning, and review harness checks.

### Out of Scope

No backend route/schema/model changes, no GraphQL/API-spine implementation, no new agent features, no Caller ID, no Medicare/OPV/PVM, no taskpane/Command Centre, no broad visual redesign, and no production code edits before approval.

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

Plan must include route-intercepted UI tests for choose-different-time/back path, confirm-ready state, confirm generic error suppression, developer diagnostics gating, and no confirm POST before explicit Confirm booking.

## Merge Criteria

Ariadne accepts the plan only if the ordinary receptionist flow is calm and actionable, internal codes remain hidden unless debug/dev flags are set, and the UI can consume a corrected backend contract without manual IDs.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: None (plan submission only)
- Verification run: None (plan submission only)
- Remaining risks: None (plan phase)
