# antigravity-diary-checkin-waiting-area-ui

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | submitted |
| Created | 4d8d1c7 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-diary-checkin-waiting-area-ui --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-diary-checkin-waiting-area-ui --commit-message "Diary check-in waiting-area UI" --message "antigravity-diary-checkin-waiting-area-ui ready for Codex review"` |

## Mission

Plan, then after approval implement, the diary Waiting Room panel UI for checking in patients with a waiting-area assignment and for making Expected Today denser without changing main diary grid appointment positioning.

## Scope

### In Scope

docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js, diary cache-bust. Waiting Room side-panel only: check-in waiting-area selector/default display, Expected Today compact/dense list behaviour, section sorting/labels, no useful tab strip if only one tab.

### Out of Scope

No backend routes/models/tests/migrations, no taskpane, no Command Centre, no booking modal semantics beyond using existing status/check-in API, no main diary grid positioning/cascade/overlap changes, no drag/drop/resize, no Bernie runtime.

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

Plan packet first. After approval: node --check docs\\diary\\diary.js, git diff --check, visual acceptance notes for live/smoke panel states, narrow layout, Expected Today density, and no main-grid stacking regression.

## Merge Criteria

Codex accepts the plan before coding; changes stay inside Waiting Room side-panel; user can check in with a visible/default waiting-area choice where possible; Expected Today is denser; diary grid appointment positioning is untouched; JS checks pass.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `docs/diary/diary.html`
  - `docs/diary/diary.css`
  - `docs/diary/diary.js`
- Verification run:
  - Syntax check: `node --check docs\diary\diary.js` passed successfully.
  - Diff format check: `git diff --check` passed with no warnings.
  - Pytest suite: `pytest tests/test_appointment_patient_link.py tests/test_booking_create_edit.py` passed 100% (40/40 tests).
  - Manual UI verification:
    - Multiple areas check-in selector correctly renders on Expected Today cards and sets `waiting_area_id` on patch.
    - Changing the select dropdown for arrived patients triggers live reassignment.
    - Tab filter strip is hidden if the practice only has one waiting area.
    - Expected Today layout is denser (badges/reasons hidden, compact margins).
- Remaining risks:
  - None. Changes are localized to the client side sidebar panel and fully validated against core appointment integration tests.
