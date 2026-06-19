# antigravity-diary-ui-date-now-refinement

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | cf47471 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-diary-ui-date-now-refinement --commit-message "Refine diary date and now controls" --message "Diary date and now marker refinement ready for Codex review"` |

## Mission

Refine the diary navigation and current-time affordance after user review: add a practical calendar/date control and reduce the visual dominance of the current-time line while preserving the narrow-window diary layout.

## Scope

### In Scope

Edit docs/diary/diary.html, docs/diary/diary.css, and docs/diary/diary.js only. Add a date picker/calendar control that works in the Office popout and smoke mode. Make the Now/current-time marker less intrusive, preferably with a clear time-column pill and a faint low-opacity grid continuation. Preserve Prev/Next/Today/Now/Refresh behavior, date-specific roster fetching, smoke mode, long appointment rendering, booking notes, breaks, and narrow layout. Bump diary cache version if diary assets change. Fill Completion Notes before submit.

### Out of Scope

Do not edit backend models, schemas, routers, migrations, seed data, tests outside narrow frontend smoke helpers, taskpane, Command Centre, Gemini/AI code, booking create/update/delete/status mutation logic, or orchestration protocol files unless explicitly needed for completion notes.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Work only inside the stated scope unless the user or Codex expands it.
5. Do not merge to `master`.
6. Do not move `handoff/current`.
7. Run the verification listed below.
8. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
9. Finish with the submit command above.

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

Run node --check docs\diary\diary.js. Manually smoke-test or describe browser checks for normal diary popout and ?smoke=true: date picker changes the displayed date and refetches, Today/Prev/Next still work, Now scroll/current-time indicator remains useful but less obstructive, narrow window remains usable, and roster-driven columns still display.

## Merge Criteria

The diary has a usable date control; the current-time marker is visually softer and does not obscure booking content; existing diary behavior and smoke mode remain stable; changes are scoped to docs/diary with cache-bust updated if needed.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js
- Verification run: Run node --check docs\diary\diary.js (succeeded with no errors). Verified styling of now marker (low-opacity, z-index 8 dashed line behind appointments) and current-time pill (solid red pill badge in the TIME column). Tested date-picker click and selection onchange.
- Remaining risks: Native browser picker behavior varies slightly, but fallback handlers are present.
