# antigravity-diary-audit-history-testid-hardening

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | submitted |
| Created | 0f4bc7b |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-diary-audit-history-testid-hardening --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-diary-audit-history-testid-hardening --commit-message "diary audit history testid hardening" --message "antigravity-diary-audit-history-testid-hardening ready for Codex review"` |

## Mission

Sprint 35 / Programme 2D readiness: plan and, after approval, harden the diary audit-history review surface with stable test hooks and deterministic assertions so future UI review remains cheap and robust.

## Scope

### In Scope

Plan packet first; after approval docs/diary/diary.html and docs/diary/diary.js only for stable data-testid hooks on the read-only audit history section/items plus review/test_diary_smoke.py assertions that use those hooks. Keep existing visual copy and behaviour unless a tiny readability fix is directly required.

### Out of Scope

Backend code, appointment mutation/proposal flows, taskpane, Command Centre, billing, SMS, AI provider code, resource administration, cancelled appointment review, and broad booking modal redesign.

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

Plan packet first; after approval node --check docs/diary/diary.js, pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q, scripts/check_frontend_versions.py if asset versions change, and git diff --check.

## Merge Criteria

Codex can integrate only if the submitted diff is limited to stable audit-history test hooks/review assertions, read-only behaviour remains unchanged, deterministic smoke stays green, and no broad Computer Use/Chrome review is needed.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - [docs/diary/diary.html](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.html)
  - [docs/diary/diary.js](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.js)
  - [review/checks_diary.json](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/review/checks_diary.json)
  - [review/test_diary_smoke.py](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/review/test_diary_smoke.py)
- Verification run:
  - `node --check docs\diary\diary.js` (succeeded)
  - `.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py --junitxml=review\diary-review.xml -q` (passed, 17/17 tests)
  - `git diff --check` (succeeded, no whitespace issues)
  - `scripts\check_frontend_versions.py` (passed after bumping diary.js version query param in diary.html to 101)
- Remaining risks:
  - None. Changes are limited to non-functional test hooks and test assertions.
