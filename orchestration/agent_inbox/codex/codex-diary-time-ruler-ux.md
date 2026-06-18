# codex-diary-time-ruler-ux

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/diary-time-ruler-ux` |
| Status | submitted |
| Created | 05edbb6 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-diary-time-ruler-ux --commit-message "Refine diary time ruler UX" --message "Diary time-ruler UX ready for Codex review"` |

## Mission

Make flexible diary times understandable in the native diary grid without starting booking create/edit/drag mutations.

## Scope

### In Scope

- Update `docs/diary/diary.js`, `docs/diary/diary.css`, and `docs/diary/diary.html` only as needed.
- Keep a stable visible major grid, likely 15-minute time rows, while allowing 5-minute minimum internal positioning for appointments/breaks.
- Consume or preserve per-column `slot_interval_minutes` data where it is useful, without making the visible UI chaotic.
- Add exact-time affordances for non-grid-aligned booking/break starts/ends, such as hover titles, small time readouts, or border-focused labels.
- Add a "Now" control and/or opening auto-scroll near the current time.
- Maintain smoke mode and narrow-window behavior.
- Bump diary cache version if deployed HTML references change.

### Out of Scope

- Do not edit backend models, schemas, routers, migrations, or tests; Claude owns roster backend work.
- Do not implement booking drag/drop, resize, create, delete, or status mutations.
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

- Run `node --check docs\diary\diary.js`.
- Open smoke mode or otherwise visually verify desktop and narrow diary widths.
- Verify date navigation and refresh still work.
- Verify the 10:00 long booking remains visibly long and notes remain readable.

## Merge Criteria

- Flexible times are clearer to a user than before.
- The visible diary remains stable and scannable at narrow and normal widths.
- No backend or Gemini files are changed.
- No booking mutation behavior is introduced.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Fill this in before submit:

- Files changed:
- Verification run:
- Remaining risks:
