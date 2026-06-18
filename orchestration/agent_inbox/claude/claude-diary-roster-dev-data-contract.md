# claude-diary-roster-dev-data-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | submitted |
| Created | 2f511a1 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-diary-roster-dev-data-contract --commit-message "Harden diary roster dev-data contract" --message "Diary roster dev-data contract ready for Codex review"` |

## Mission

Make the diary roster backend contract seedable, testable, and safe for frontend consumption, so the diary can render date-specific room assignments without requiring booking mutation work.

## Scope

### In Scope

- Inspect app/models/diary.py, app/schemas/diary.py, app/routers/diary.py, seed.py, migrations, and tests before changing anything.\n- Ensure local/dev data can produce useful Room and DiaryRoster rows from the existing diary template or seed patterns.\n- Add or tighten focused tests for GET /api/v1/diary/roster?date=YYYY-MM-DD, including empty fallback, practice scoping, room ordering, label-only rooms, and practitioner AHPRA assignment.\n- Keep GET /api/v1/diary/template backward-compatible.\n- If a migration or seed update is needed, keep it idempotent and narrow.

### Out of Scope

- Do not edit docs/diary/diary.html, docs/diary/diary.css, or docs/diary/diary.js; Antigravity owns frontend consumption.\n- Do not implement booking drag/drop, resize, create, delete, or status mutations.\n- Do not alter consultation AI, taskpane, command-centre, or Gemini code.\n- Do not push to master or handoff/current manually.

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

- Run .venv\\Scripts\\python.exe -m pytest tests\\test_diary_roster.py tests\\test_diary_template.py.\n- Run broader appointment/diary tests if shared factories or appointment contracts are touched.\n- Run Alembic head/current/upgrade checks if migrations are added or changed.\n- Report exact commands and results in Completion Notes.

## Merge Criteria

- Roster endpoint gives the frontend a deterministic date-specific room list when seed/dev data exists.\n- Empty/no-roster behaviour remains safe and backward-compatible.\n- Practice scoping is tested and no cross-practice leakage is possible.\n- Room ordering, label-only rooms, and practitioner AHPRA assignment are covered.\n- No frontend, Gemini, or booking mutation files are changed.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Fill this in before submit:

- Files changed:
- Verification run:
- Remaining risks:
