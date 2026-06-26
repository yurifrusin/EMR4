# antigravity-diary-noshow-dna-flow

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | 90ef76b |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-diary-noshow-dna-flow --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-diary-noshow-dna-flow --commit-message "Diary no-show/DNA flow" --message "antigravity-diary-noshow-dna-flow ready for Codex review"` |

## Mission

Plan, then after approval make the diary no-show/DNA user flow clear and reviewable: proposal-first confirmation, terminal attendance labels, no active waiting-room/grid confusion, and deterministic cheap review checks where possible.

## Scope

### In Scope

Plan packet first. After approval: docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js only if needed, review/checks_diary.json, review/harness.py, review/test_diary_smoke.py, review/README.md, smoke-mode fixtures/test hooks, and asset cache-bust if diary assets change.

### Out of Scope

Backend routes/models/tests/migrations, taskpane, Command Centre, resource administration, cancellation reason/note capture, cancelled appointment review redesign, recurrence, broad visual restyle, direct mutation before proposal confirmation.

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

Plan packet first. After approval: node --check docs/diary/diary.js if touched, pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q, python scripts/check_frontend_versions.py if assets change, targeted Playwright/DOM assertions where useful, and git diff --check.

## Merge Criteria

Codex can merge when the plan is approved, NoShow/DNA diary behavior is unambiguous and proposal-first, deterministic review checks cover the important UI state where practical, no backend/out-of-scope changes are present, and verification passes or any limitation is clearly justified.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
