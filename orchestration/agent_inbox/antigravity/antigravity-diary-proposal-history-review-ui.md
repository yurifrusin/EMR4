# antigravity-diary-proposal-history-review-ui

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | pending_plan_review |
| Created | 4aaf8e7 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-diary-proposal-history-review-ui --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-diary-proposal-history-review-ui --commit-message "Diary proposal history review UI" --message "antigravity-diary-proposal-history-review-ui ready for Codex review"` |

## Mission

Sprint 33 / Programme 2D readiness: plan a lightweight diary-side read-only review surface for appointment proposal/audit history once the backend contract exists, keeping the active diary workflow uncluttered and non-mutating.

## Scope

### In Scope

Diary frontend planning and, after approval, a narrow read-only UI surface or smoke-mode scaffold for viewing proposal/audit history for a selected appointment if the backend contract is available. Likely docs/diary/diary.html, docs/diary/diary.js, docs/diary/diary.css, and review smoke checks if a scriptable invariant can be harvested.

### Out of Scope

Backend schema/API implementation, taskpane, Command Centre, Gemini/AI provider code, write actions from the history surface, restore/reactivation, broad supervisor dashboard, billing/SMS, and visual redesign of unrelated diary panels.

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

Static JS check, existing diary review smoke, any new cheap Playwright/review assertion for the read-only history affordance, and live/browser checks only if structural checks cannot verify the behaviour.

## Merge Criteria

Plan packet first with Role convention. Implementation merge only if UI is read-only, scoped to selected appointment/history, does not disturb existing Waiting Room/Cancelled/Finished flows, and degrades gracefully when no backend history exists.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
