# claude-diary-column-slot-intervals

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | in_progress |
| Created | ec0b230 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-diary-column-slot-intervals --commit-message "Add diary column slot interval support" --message "Diary column slot interval support ready for Codex review"` |

## Mission

Add optional per-column diary slot interval support with a 5-minute minimum, so future diary/template editing can support columns such as GP 15-minute slots and nurse 10-minute slots without hardening around one practice-wide cadence.

## Scope

### In Scope

- Add an optional per-column slot interval field to the diary template data model and API schema, likely `DiaryColumn.slot_interval_minutes` / `DiaryColumnOut.slot_interval_minutes`.
- Add an Alembic migration for the new nullable column.
- Validate or constrain the value so configured intervals are at least 5 minutes and preferably multiples of 5, using the existing project style.
- Update seed data only if needed to keep dev defaults stable.
- Add/update backend tests for the diary template endpoint showing practice default interval remains available and per-column interval can be returned.
- Keep existing fallback behavior intact.

### Out of Scope

- Do not edit `docs/diary/diary.js`; Kepler/Codex worker owns frontend template consumption.
- Do not implement drag/drop booking mutations.
- Do not build a template editor UI.
- Do not change appointment conflict logic unless a test exposes a directly related bug.
- Do not push to `master` or `handoff/current` manually.

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
- Do not manually work around a failed `submit`.
- If `submit` fails, stop and report the exact command, working directory, branch,
  and error output to the orchestrator.
- If these instructions conflict with remembered prior protocol, trust the current
  `handin` alerts and this task packet.

## Verification

- Run the diary template tests, at minimum `.venv\Scripts\python.exe -m pytest tests\test_diary_template.py`.
- Run broader appointment/diary tests if schema or migration changes risk shared behavior.
- Run any migration import/check command normally used in this repo if applicable.

## Merge Criteria

- `GET /api/v1/diary/template` still works for existing templates.
- Existing templates without per-column intervals continue to serialize cleanly.
- A column with a valid interval such as 10 returns that value.
- Invalid intervals below 5 or non-multiples of 5 are rejected or clearly guarded according to the local validation pattern.
- No frontend diary files are changed.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Fill this in before submit:

- Files changed:
- Verification run:
- Remaining risks:
