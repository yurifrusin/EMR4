# codex-diary-template-api

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/diary-template-api` |
| Status | in_progress |
| Created | 882381e |
| Start Command | `python scripts\agent_worktrees.py handin` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-diary-template-api --commit-message "Add diary template API foundation" --message "Diary template API foundation ready for Codex review"` |

## Mission

Create the backend foundation for serving diary template/room roster configuration from the API instead of embedding it permanently in docs/diary/diary.js.

## Scope

### In Scope

Add narrowly scoped backend models/schemas/router/migration as needed for Room and diary roster/template read APIs. Keep defaults compatible with current diary_template.json. Add focused tests if practical. Update orchestration notes only if the API contract is clarified.

### Out of Scope

No frontend diary rewrite; Antigravity owns that slice. No booking mutations, drag/drop, SMS, waiting-room UI, or online booking portal. Do not remove the embedded diary template until a frontend task consumes the API.

## Required Steps

1. Run the start command above.
2. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
3. Work only inside the stated scope unless the user or Codex expands it.
4. Do not merge to `master`.
5. Do not move `handoff/current`.
6. Run the verification listed below.
7. Finish with the submit command above.

## Verification

Run .venv\\Scripts\\python.exe -m compileall app scripts tests seed.py. Run relevant pytest tests or add/run focused tests if backend routes are added. Run alembic heads/current/upgrade head if a migration is added.

## Merge Criteria

A future frontend can fetch a practice diary template/room roster from an authenticated backend endpoint; migration chain remains single-headed; existing appointment tests still pass; current diary remains functional if the frontend does not yet consume the API.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Fill this in before submit:

- Files changed:
- Verification run:
- Remaining risks:
