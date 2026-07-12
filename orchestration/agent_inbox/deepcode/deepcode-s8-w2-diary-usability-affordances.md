# S8 W2 - Diary Usability Affordances

Role: implementation owner
Resource: `deepseek-flash-workers` instance 2
Model: `deepseek-v4-flash` / high
Parent plan:
`orchestration/agent_inbox/codex/plan-claude-fable-s8-receptionist-workflow.md`
Result artifact:
`orchestration/agent_inbox/codex/review-deepseek-s8-w2-diary-affordances.md`

Read the parent plan, AGENTS.md, and current source before editing. Implement
only S8 W2 as defined by the Conductor.

## Ownership

- `docs/diary/diary.js`
- `docs/diary/diary.html`
- `docs/diary/diary.css`
- new focused tests under `review/` for these four affordances
- your result artifact

Do not edit taskpane sources, `sync_taskpane.py`, backend code, schemas,
migrations, provider code, or files owned by W1.

## Required Outcome

Implement in this order:

1. Immediately reveal, emphasize, and focus inline reason-code validation when
   `Cancelled`, `NoShow`, or `DNA` is selected. Keep save-time validation as a
   backstop and preserve signed proposal/confirm payloads.
2. Feature-detect `showPicker()` and provide an accessible, visible native date
   input fallback when unavailable.
3. Add a same-day client-side appointment search/filter over patient or
   provisional name and reason. Preserve query/focus across silent refresh and
   do not disturb `.appt-active` restoration.
4. Add accessible read-only reason/notes preview without opening the edit modal,
   including keyboard and non-hover access. No mutation controls.

Bump diary.js v183 to v184 and diary.css v135 to v136 if CSS changes. Follow
existing diary visual conventions. Do not change terminal-to-active status
semantics, raw PATCH behavior, GraphQL/REST switching, or write contracts.

## Verification

Add honest focused Playwright/pytest tests. Run them plus
`review/test_diary_smoke.py`,
`review/test_diary_selection_preservation.py`, `node --check
docs/diary/diary.js`, `scripts/check_frontend_versions.py`, and
`git diff --check`. Do not weaken or delete existing tests.

Commit the candidate on your assigned branch. In the result artifact record the
branch, candidate commit, files changed, exact tests/counts, remaining risks,
and boundary compliance. End the artifact with `STATUS: complete`.

Do not merge, push `master`, move `handoff/current`, or grant yourself
integration authority. Permission prompts are transport events, not authority.
