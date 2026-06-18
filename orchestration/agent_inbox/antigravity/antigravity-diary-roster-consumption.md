# antigravity-diary-roster-consumption

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | 2f511a1 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-diary-roster-consumption --commit-message "Consume diary roster in frontend" --message "Diary roster consumption ready for Codex review"` |

## Mission

Wire the native diary frontend to consume the date-specific roster endpoint when available, while preserving template fallback, smoke mode, narrow layout, and read-only diary behaviour.

## Scope

### In Scope

- Edit only docs/diary/diary.html, docs/diary/diary.css, and docs/diary/diary.js unless a tiny docs note is essential.\n- Fetch GET /api/v1/diary/template and GET /api/v1/diary/roster?date=YYYY-MM-DD for the selected diary date.\n- Merge roster entries into visible columns by room/order when entries exist, preserving template breaks/tints/slot intervals where sensible.\n- Show label-only rooms such as [Available] clearly.\n- Preserve fallback to template columns when roster is empty or unavailable.\n- Preserve smoke mode, date navigation, Refresh, Now/current-time affordances, long booking rendering, booking notes, and narrow-window behaviour.\n- Bump diary cache version if diary.html references change.

### Out of Scope

- Do not edit backend models, schemas, routers, migrations, seed, or tests; Claude owns the backend contract slice.\n- Do not implement booking drag/drop, resize, create, delete, or status mutations.\n- Do not alter taskpane, command-centre, consultation AI, or Gemini code.\n- Do not push to master or handoff/current manually.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Work only inside the stated scope unless the user or Codex expands it.
5. Do not merge to `master`.
6. Do not move `handoff/current`.
7. Run the verification listed below.
8. Finish with the submit command above.

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

- Run node --check docs\\diary\\diary.js.\n- Manually smoke-test or describe browser checks for normal mode fallback and ?smoke=true.\n- Verify date navigation still refetches date-specific data.\n- Verify the 10:00 long booking remains visibly long and booking notes remain readable.\n- Verify narrow layout still works.

## Merge Criteria

- Diary columns can be sourced from roster data without losing template fallback.\n- Existing smoke-mode and read-only diary behaviours are preserved.\n- Frontend remains robust if roster fetch returns empty, 404/401, or temporarily fails.\n- No backend, taskpane, command-centre, Gemini, or booking mutation work is introduced.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Fill this in before submit:

- Files changed:
- Verification run:
- Remaining risks:
