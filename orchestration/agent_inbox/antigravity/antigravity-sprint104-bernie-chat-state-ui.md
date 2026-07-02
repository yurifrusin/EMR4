# antigravity-sprint104-bernie-chat-state-ui

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | 12fb780 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint104-bernie-chat-state-ui --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint104-bernie-chat-state-ui --commit-message "Sprint 104 Bernie Chat State UI" --message "antigravity-sprint104-bernie-chat-state-ui ready for Codex review"` |

## Mission

Plan the Diary UI side of Sprint 104: turn Bernie prompt entry into a chat/clarification turn surface with explicit session state transitions, stale-state clearing for diary navigation/refresh, no-slot copy with clickable next actions, and a visible boundary for ordinary best-candidate auto-preview. This is a plan-gated packet only; write and submit the implementation plan, then stop.

## Scope

### In Scope

Plan packet first only. Likely surfaces: docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js, review/test_diary_smoke.py, and asset version checks. Model prompt submission, Bernie response, clarification turns, Today/Prev/Next/date picker/Refresh, candidate selection, Choose another time, proposal preview, cancellation, and confirmation as explicit UI state transitions. Keep compact receptionist copy with Details/See more for technical evidence.

### Out of Scope

Production code before plan approval; backend implementation except consuming planned contract fields; broad diary redesign; root-to-branch API rewrite; XState/runtime dependency; voice/headset/Caller ID; Medicare/HI/IHI/PVM/OPV; limited auto-confirm/auto-mode; removing staff confirmation; exposing sensitive identifiers by default.

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

Plan must specify deterministic smoke tests for fresh chat turns after a response, clarification text applying to current session memory, stale candidate/proposal clearing on Today/Prev/Next/date picker/Refresh, no-slot direct copy plus clickable suggestion actions, retained manual candidate path, ordinary auto-preview behaviour, and asset version bump checks.

## Merge Criteria

Ariadne can accept the plan if it keeps Diary UI ownership narrow, treats navigation and confirmation as transitions rather than prompt mutation, preserves sensitive details disclosure, leaves backend facts deterministic, and provides concrete route-intercepted review-harness cases for implementation release.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
