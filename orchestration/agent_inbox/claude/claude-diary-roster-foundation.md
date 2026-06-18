# claude-diary-roster-foundation

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | integrated |
| Created | 05edbb6 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-diary-roster-foundation --commit-message "Add diary roster foundation" --message "Diary roster foundation ready for Codex review"` |

## Mission

Add the backend foundation for date-specific diary room/roster configuration so the diary can eventually show Room 1/2/3 assignments from data rather than static template columns.

## Scope

### In Scope

- Inspect the current diary template backend before changing it.
- Add narrowly scoped Room and DiaryRoster-style persistence, or an equivalent local pattern, for date-by-room assignment to a practitioner or a label such as `[Available]`.
- Add an Alembic migration if new tables/columns are required.
- Add Pydantic schemas and authenticated API route/service support sufficient for Codex/frontend workers to fetch roster state later.
- Preserve the current `GET /api/v1/diary/template` contract unless you explicitly add backward-compatible fields.
- Add focused tests for practice scoping, serialization, and default/empty roster behavior.

### Out of Scope

- Do not edit `docs/diary/diary.js`, `docs/diary/diary.css`, or `docs/diary/diary.html`; Codex worker owns the diary UX slice.
- Do not implement drag/drop booking mutations.
- Do not change appointment conflict logic unless a directly related test exposes a blocker.
- Do not touch Gemini/Vertex AI SDK migration.
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

- Run the focused diary tests, at minimum `.venv\Scripts\python.exe -m pytest tests\test_diary_template.py`.
- Run any new roster tests you add.
- Run Alembic head/current/upgrade checks if a migration is added.
- Run broader appointment/diary tests if shared contracts are touched.

## Merge Criteria

- Existing diary template tests still pass.
- Migration chain remains single-headed and upgradeable.
- Roster data is practice-scoped and cannot leak between practices.
- The API shape is backward-compatible with the current diary frontend.
- The work gives a clear next integration path for the frontend without forcing drag/drop booking edits.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Fill this in before submit:

- Files changed:
- Verification run:
- Remaining risks:
