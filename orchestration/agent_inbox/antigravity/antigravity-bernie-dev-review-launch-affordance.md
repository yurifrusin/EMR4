# antigravity-bernie-dev-review-launch-affordance

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | e473bfb |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-bernie-dev-review-launch-affordance --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-bernie-dev-review-launch-affordance --commit-message "Dispatch Sprint 54 Bernie dev review launch affordance" --message "Sprint 54 dispatched: Bernie dev review launch affordance"` |

## Mission

Plan first, then after approval add a tiny dev-only affordance for launching the Bernie supervised review panel without hand-crafting the full live-review query URL, preserving default hidden/no-call behaviour and explicit staff approval.

## Scope

### In Scope

Plan packet first; after approval docs/diary UI JS/CSS/HTML and review harness tests as needed; affordance appears only when an explicit dev flag such as bernie_dev_review=true is present; user action can opt into/load the existing bernie_review=live path; route-intercepted checks for default hidden/no-call, dev-flag-only no automatic endpoint calls if applicable, launch action showing the panel/calling supervised-booking, and confirm-Bernie still gated behind approval; asset version bump if runtime assets change.

### Out of Scope

Backend routes/schemas, live autonomous booking, production default exposure, natural-language LLM parsing, real API writes in tests, taskpane, Command Centre, migrations, patient/resource admin, billing, SMS, broad diary redesign, resource selector redesign, and unrelated styling/refactors.

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

Plan packet first; after approval node syntax for touched JS, deterministic Playwright route-intercepted checks for launcher visibility/calls/gating, default-mode no-exposure/no-call proof, frontend version integrity if assets change, existing diary review harness where relevant, and git diff hygiene.

## Merge Criteria

Ariadne can verify the launcher is dev-flag-only, default diary mode remains hidden/no-call, no supervised-booking call happens until the explicit launcher path if designed that way, confirm-Bernie still requires staff approval, tests intercept endpoints and perform no live writes, and the submitted diff stays within docs/diary plus review harness scope.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - [docs/diary/diary.html](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.html)
  - [docs/diary/diary.css](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.css)
  - [docs/diary/diary.js](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/docs/diary/diary.js)
  - [review/test_diary_smoke.py](file:///C:/Users/YuriFrusin/Documents/EMR4-worktrees/antigravity/review/test_diary_smoke.py)
- Verification run:
  - Ran full Playwright test suite using `.venv\Scripts\pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q` (all tests passed, including the new `test_bernie_dev_review_launcher_and_gating` test verifying launcher button visibility/behavior, default/dev-flag-only page load calls, and checkbox confirmation gating).
  - Validated syntax of modified JavaScript via `node --check docs/diary/diary.js`.
  - Ran `git diff --check` and ensured clean output.
  - Verified version bumps for css and js assets via `.venv\Scripts\python scripts\check_frontend_versions.py`.
- Remaining risks: None. The button and logic are strictly hidden and disabled behind explicit feature flags (`bernie_dev_review=true`), preserving default non-call and non-smoke behavior. The confirm action remains locked until the checkbox is checked, and endpoint calls in tests are route-intercepted.
