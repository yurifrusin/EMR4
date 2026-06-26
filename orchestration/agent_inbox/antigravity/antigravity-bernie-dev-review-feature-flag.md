# antigravity-bernie-dev-review-feature-flag

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | submitted |
| Created | 47de4c4 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-bernie-dev-review-feature-flag --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-bernie-dev-review-feature-flag --commit-message "Dispatch Sprint 53 Bernie dev review feature flag" --message "Sprint 53 dispatched: Bernie dev-mode review feature flag"` |

## Mission

Plan first, then after approval expose the supervised Bernie review/confirm path in ordinary diary dev mode behind an explicit feature flag/query gate, preserving smoke behaviour, explicit staff approval, and no live writes in deterministic tests.

## Scope

### In Scope

Plan packet first; after approval docs/diary UI JS/CSS/HTML only if needed and review harness tests; feature flag/query gate for non-smoke dev review mode; route-intercepted supervised-booking and confirm-Bernie checks; proof default non-smoke mode remains hidden/no endpoint calls; proof confirm-Bernie is not posted before explicit staff approval; asset version bump if runtime assets change.

### Out of Scope

Backend schema/routes, live autonomous booking, natural-language LLM parsing, production default exposure, real API writes in tests, taskpane, Command Centre, migrations, patient/resource admin, billing, SMS, broad diary redesign, and unrelated style refactors.

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

Plan packet first; after approval node syntax for touched JS, deterministic Playwright review checks with route interception, default-mode no-exposure/no-call proof, explicit approval gating proof, frontend version integrity if assets change, existing diary review harness where relevant, and git diff hygiene.

## Merge Criteria

Ariadne can verify the feature is opt-in only, no normal diary exposure or endpoint calls occur without the flag, the review/confirm path is deterministic and route-intercepted in tests, explicit staff approval remains required, no live writes occur during tests, and all changed assets/packets are cleanly submitted.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - [diary.html](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.html): Bumped `diary.js` version cache-buster query parameter to `v=108`.
  - [diary.js](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.js): Added feature flag query parameter gating (`bernie_dev_review=true`) to expose the supervised Bernie review/confirm path in ordinary diary mode. Checked query params at load time and conditionally loaded the diary/review panel.
  - [test_diary_smoke.py](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/review/test_diary_smoke.py): Updated existing live review/confirm tests to include the new dev review query parameter, added checks to verify that ordinary mode hides the panel and makes no endpoint calls when the flag is absent, and added a success verification check for the flag-enabled path.
- Verification run:
  - Run Playwright test suite locally via `.venv\Scripts\python.exe -m pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q`.
- Remaining risks:
  - None identified. Standard query parameter checking is highly robust and fully isolated behind development-only flags (`bernie_dev_review=true`).
