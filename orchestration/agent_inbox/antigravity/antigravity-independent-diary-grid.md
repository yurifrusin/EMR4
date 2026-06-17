# antigravity-independent-diary-grid

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | 882381e |
| Start Command | `python scripts\agent_worktrees.py handin` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-independent-diary-grid --commit-message "Build independent diary column grid" --message "Independent diary column grid ready for Codex review"` |

## Mission

Replace the read-only diary's shared table-body rendering with an independent positioned-column layout suitable for future drag/drop and arbitrary slot durations, while preserving current read-only behavior.

## Scope

### In Scope

docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js only. Use existing appointments API data. Prefer appointment_date/start_time_local for placement. Preserve date nav, refresh, auth handshake, lifecycle styling, per-column breaks, and read-only behavior. Bump diary asset cache bust if assets change.

### Out of Scope

No backend changes. No booking create/update/delete. No drag/drop. No status mutation. No Room/DiaryRoster API work. Do not edit taskpane or Command Centre files.

## Required Steps

1. Run the start command above.
2. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
3. Work only inside the stated scope unless the user or Codex expands it.
4. Do not merge to `master`.
5. Do not move `handoff/current`.
6. Run the verification listed below.
7. Finish with the submit command above.

## Hard Stop Rules

- Do not push to `master` or `handoff/current`.
- Do not manually work around a failed `submit`.
- If `submit` fails, stop and report the exact command, working directory, branch,
  and error output to the orchestrator.
- If these instructions conflict with remembered prior protocol, trust the current
  `handin` alerts and this task packet.

## Verification

Run node --check docs/diary/diary.js. Perform browser visual QA if available: desktop and narrow viewport render nonblank grid; multi-slot appointment spans its interval; text is not incoherently clipped; overlapping appointments remain visible; break rows/blocks still render; auto-refresh can run silently without spinner flash.

## Merge Criteria

The diary no longer depends on shared table rows for appointment layout; each practitioner/room column can be reasoned about independently; current read-only workflows remain stable; no obvious clipped/overlapping text in normal 15-30 minute appointments; code remains scoped to docs/diary.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Fill this in before submit:

- Files changed:
- Verification run:
- Remaining risks:
