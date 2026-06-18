# antigravity-diary-template-smoke-path

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | ff387e5 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-diary-template-smoke-path --commit-message "Add diary template smoke path" --message "Diary template smoke path ready for Codex review"` |

## Mission

Create a small visual/user-review smoke path for the now template-driven diary grid so the orchestrator/user can verify that rooms, tints, breaks, footer, and appointments still render correctly after `docs/diary/diary.js` begins consuming `GET /api/v1/diary/template`.

## Scope

### In Scope

- Inspect the integrated diary frontend and backend template endpoint behavior.
- Add a lightweight smoke/review aid if useful, preferably documentation or a narrowly scoped static/dev-only helper rather than production complexity.
- Verify the diary still renders seeded template-driven columns, per-column breaks, footer text, appointment spans, overlap lanes, and click-to-expand notes.
- Record precise manual review steps and any visual concerns in the task packet completion notes.

### Out of Scope

- Do not implement booking create/edit/drag/drop mutations.
- Do not change backend diary models or schemas; Claude owns per-column interval modelling.
- Do not rewrite the diary layout or lifecycle styling unless a small fix is required for the smoke path.
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

- Run `node --check docs\diary\diary.js` if diary JS is touched.
- If adding a smoke helper, verify it opens/runs locally or explain the exact manual verification path.
- Capture any browser/user review notes needed for Codex integration.

## Merge Criteria

- The review path clearly proves the diary is now template-driven without requiring the user to infer from code.
- Any code changes are small, scoped, and do not conflict with Claude's backend interval task.
- Existing diary behavior remains intact.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Fill this in before submit:

- Files changed:
- Verification run:
- Remaining risks:
