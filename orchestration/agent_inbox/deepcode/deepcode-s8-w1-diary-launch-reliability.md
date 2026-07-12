# S8 W1 - Diary Launch Reliability

Role: implementation owner
Resource: `deepseek-flash-workers` instance 1
Model: `deepseek-v4-flash` / high
Parent plan:
`orchestration/agent_inbox/codex/plan-claude-fable-s8-receptionist-workflow.md`
Result artifact:
`orchestration/agent_inbox/codex/review-deepseek-s8-w1-launch-reliability.md`

Read the parent plan, AGENTS.md, and current source before editing. Implement
only S8 W1 as defined by the Conductor.

## Ownership

- `EMR4 Sidebar/src/taskpane/taskpane.js`
- `EMR4 Sidebar/src/taskpane/taskpane.html`
- `EMR4 Sidebar/src/taskpane/taskpane.css`
- `sync_taskpane.py`
- new `review/test_taskpane_diary_launch.py`
- your result artifact

Do not edit `docs/diary/`, backend code, schemas, migrations, provider code, or
files owned by W2. `docs/taskpane/` generation is reserved for Sol integration.

## Required Outcome

1. Add a pure, testable diary URL resolver for local development, ngrok, Pages,
   and an unrecognized-host safe deployed fallback. Preserve deployed behavior.
2. Give Office dialog failures distinct receptionist-readable handling for
   12007, 12009, 12011, and generic failures. Provide a visible retry action.
3. Retry 12007 once after safely closing the stale dialog; do not loop.
4. Preserve `sync_taskpane.py` patch parity and existing Command Centre behavior.
5. Bump the taskpane cache key.
6. Add focused Playwright/pytest coverage for URL selection, error messaging,
   retry visibility, and bounded 12007 retry.

Use existing UI conventions and avoid explanatory feature text. Do not change
terminal-status policy or any network command payload.

## Verification

Run the focused new tests, relevant existing taskpane/diary launch tests,
`node --check` on the source taskpane JS, and `git diff --check`. Do not claim
tests you did not run. Do not weaken or delete existing tests.

Commit the candidate on your assigned branch. In the result artifact record the
branch, candidate commit, files changed, exact tests/counts, remaining risks,
and boundary compliance. End the artifact with `STATUS: complete`.

Do not merge, push `master`, move `handoff/current`, or grant yourself
integration authority. Permission prompts are transport events, not authority.
