# antigravity-diary-review-harness-hardening

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | pending_plan_review |
| Created | b22a794 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-diary-review-harness-hardening --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-diary-review-harness-hardening --commit-message "Diary review harness hardening" --message "antigravity-diary-review-harness-hardening ready for Codex review"` |

## Mission

Plan, then after approval extend the deterministic diary review harness so more user-review checks run through cheap Playwright/pytest assertions rather than Computer Use or Chrome screenshots.

## Scope

### In Scope

Plan first. After approval: review harness and diary smoke-mode testability only, likely review/checks_diary.json, review/harness.py, review/test_diary_smoke.py, review/README.md, and minimal docs/diary data-testid or smoke-mode hooks if justified. Target cancelled/review-panel or appointment-card assertions that are stable and cheap.

### Out of Scope

No backend API changes, no migrations, no production diary behaviour redesign, no appointment mutation semantics, no taskpane/Command Centre, no Bernie runtime, no broad visual restyle, no Computer Use dependency. Do not edit production code before the plan gate is approved.

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

Plan packet first. After approval: pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q, node --check docs/diary/diary.js if touched, npm run validate-all if relevant, git diff --check. Capture screenshots/traces only on failure if the harness supports it.

## Merge Criteria

Codex can run a deterministic review command and get compact pass/fail output for new checks; any selectors/hooks are stable, minimal, and do not change user-visible diary behaviour; documentation explains how future checks should be added.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
