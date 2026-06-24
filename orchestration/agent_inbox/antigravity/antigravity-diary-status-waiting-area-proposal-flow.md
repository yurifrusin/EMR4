# antigravity-diary-status-waiting-area-proposal-flow

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | 3124a28 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-diary-status-waiting-area-proposal-flow --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-diary-status-waiting-area-proposal-flow --commit-message "Diary Status/Waiting-Area Proposal Flow" --message "antigravity-diary-status-waiting-area-proposal-flow ready for Codex review"` |

## Mission

Route diary status/check-in/waiting-area changes through the proposal-first flow before mutation, with clear block/warning/confirm UI that matches the Sprint 24 create/edit proposal pattern.

## Scope

### In Scope

docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js only; status controls, waiting-room/check-in affordances, proposal handling, smoke/live-test helpers, cache-busting.

### Out of Scope

Backend routes/models/tests/migrations, taskpane/Command Centre/Gemini, drag/drop/resize, recurrence, Resource Administration, patient duplicate review, broad visual redesign.

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

node --check docs/diary/diary.js plus smoke-mode checks for allowed, blocked, warning/confirm, reset-on-field-change, and API-failure paths; describe any live-browser checks Ariadne should run after integration.

## Merge Criteria

Codex can verify diary mutations do not write until a successful proposal/confirmation path, UI copy is readable, existing create/edit proposal behavior is not regressed, and assets are cache-busted.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
