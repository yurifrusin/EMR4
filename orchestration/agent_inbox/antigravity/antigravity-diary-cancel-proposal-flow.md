# antigravity-diary-cancel-proposal-flow

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | submitted |
| Created | 1f26087 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-diary-cancel-proposal-flow --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-diary-cancel-proposal-flow --commit-message "diary-cancel-proposal-flow" --message "antigravity-diary-cancel-proposal-flow ready for Codex review"` |

## Mission

Plan first, then route the diary Cancel Appointment action through proposal-first safety semantics before any destructive write, matching the existing create/edit/status/move/resize proposal dialog pattern.

## Scope

### In Scope

docs/diary/diary.html; docs/diary/diary.css; docs/diary/diary.js; smoke-mode cancellation proposal simulation; asset cache-bust; minimal UI copy needed for cancellation confirmation

### Out of Scope

Backend routes/models/tests/migrations; taskpane; Command Centre; patient search/linking; Waiting Room layout; Resource Administration; recurrence; broad visual redesign; direct delete before proposal confirmation

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

Plan packet first. After complete sprint task: node --check docs/diary/diary.js, npm run validate-all, smoke/browser checks for cancel proposal safe/warning/blocked/cancel-confirm/revert paths, git diff --check

## Merge Criteria

Codex can verify cancellation no longer bypasses proposal preflight, blocked/warning/safe paths are clear, cancellation remains scoped to the selected appointment, asset versions are bumped, and existing create/edit/status/move/resize flows are not regressed

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
