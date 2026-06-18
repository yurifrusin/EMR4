# EMR4 Sprint Closeout

This file is the user-facing closeout note for the latest fully integrated batch
of parallel-agent work. Codex updates it after submitted work has been polled,
reviewed, integrated, verified, pushed, and audited.

## Current Closeout

| Item | Value |
|---|---|
| Batch | Phase 2 diary foundation sprint |
| Integrated through | current `master` |
| Status | Ready for user review |
| Last updated | 2026-06-18 |

## What Changed

- Appointment backend is hardened around auth, practice scoping, conflict checks,
  duration-aware slots, and canonical clinic-local date/time fields.
- Diary UI now renders as a native independent positioned-column grid rather than
  a shared table body.
- Multi-slot appointments span their real duration, overlapping bookings remain
  visible, and short appointment reasons are preserved in tooltips instead of
  being visibly clipped.
- Narrow diary windows now wrap the top header controls instead of cutting them
  off to the right.
- Diary template backend foundation exists at `GET /api/v1/diary/template`.
- Diary UX decisions captured for later: arbitrary appointment durations, optional
  per-column slot cadence, click-to-expand notes, possible lifecycle colour bars,
  and a future "Now" scroll control.
- Orchestration now has task packets, review packets, an integration log, audit,
  and stale disposable worktree detection.

## Recommended User Review

These checks are worth doing before dispatching the next set of agent tasks:

1. Start the dev stack with `.\run_dev.ps1`.
2. If the 10:00 demo booking still renders as a 15-minute booking, run
   `.venv\Scripts\python.exe seed.py` once to repair existing seeded demo
   durations without recreating the database.
3. Open the Word Online add-in and sign in as the dev clinic user.
4. Open the diary from the taskpane.
5. Confirm the diary loads without an auth/error banner.
6. Check the seeded appointments:
   - 09:00 Margaret Thompson appears as confirmed / bold blue / all caps.
   - 09:15 Billy Frusin appears as a normal short booking without clipped reason text.
   - 10:00 Margaret Thompson spans 45 minutes and can show its reason line.
7. Use Previous, Today, Next, and Refresh to confirm date navigation still works.
8. Check narrow/mobile-ish width: header controls should wrap into a taller header,
   and columns should remain usable with horizontal scrolling.
9. Open the break editor for a column, change a break locally, save, and confirm
   the break block re-renders.

## Not Required Before Moving On

- Full online booking portal testing: not built yet.
- Drag/drop appointment mutations: not built yet.
- Room/roster admin UI testing: not built yet.
- Clinical note workflow regression: this sprint did not touch the Word clinical
  anchoring path, though a quick smoke test is always welcome.

## Known Follow-Up

- `docs/diary/diary.js` still embeds the diary template literal. It should next
  fetch `GET /api/v1/diary/template`.
- Preserve booking flexibility when adding edit/drag UI: the API already allows
  arbitrary `duration_minutes`, but the diary template currently has one practice-wide
  interval. Add optional per-column slot interval config before the template editor
  hardens around only 15-minute rows. Treat 5 minutes as the minimum staff editing/snap
  unit, with normal columns still free to default to 10 or 15 minutes.
- GitHub Pages can serve a stale build even after `master` is pushed. For any
  diary/taskpane deploy, verify the live `?v=N` and trigger a Pages rebuild with
  `gh api --method POST repos/yurifrusin/EMR4/pages/builds` if needed.
- Two stale disposable Codex worktrees remain visible in `audit`:
  - `codex/diary-template-api`: clean, can be retired.
  - `codex/time-model`: dirty, should be reviewed before retirement.
- Vertex AI `generative_models` emits a deprecation warning and should be migrated
  before the 2026-06-24 removal date.

## Recommended Next Direction

Proceed with a small, high-confidence next sprint:

1. Wire the diary frontend to `GET /api/v1/diary/template`.
2. Add a small user-visible smoke path for template-driven rooms/columns.
3. Retire or explicitly preserve stale disposable Codex worktrees.
4. Start the Gemini SDK migration spike before adding more AI-facing features.

Do not start drag/drop booking mutations until the template API is consumed by the
frontend and the user has visually reviewed the diary grid foundation.
