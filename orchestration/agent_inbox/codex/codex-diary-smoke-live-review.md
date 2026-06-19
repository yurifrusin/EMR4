# codex-diary-smoke-live-review

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/diary-smoke-live-review` |
| Status | integrated |
| Created | cf47471 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-diary-smoke-live-review --commit-message "Add diary smoke live review checklist" --message "Diary smoke/live review checklist ready for Codex review"` |

## Mission

Create a lightweight Codex review aid for this sprint: clarify smoke-mode versus live diary expectations, preserve the manual review checklist, and identify what the orchestrator should verify after Claude and Antigravity submit.

## Scope

### In Scope

Inspect current diary smoke mode, sprint_closeout.md, parallel_workstreams.md, and recent user review notes. Add or update small orchestration documentation/checklist artifacts only if useful. Clarify that ?smoke=true intentionally uses mock data and can differ from the taskpane popout. Include checks for date picker behavior, softer Now marker, roster-driven live columns, and the test DB hardening follow-up. Keep the work review-oriented and small.

### Out of Scope

Do not edit production backend, diary frontend implementation, taskpane, Command Centre, Gemini/AI code, migrations, seed data, or tests unless a tiny documentation-linked smoke note genuinely requires it. Do not push to master or handoff/current manually.

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

Run git diff --check. If no JS is touched, node --check is not required. Completion Notes must include the exact post-integration manual review checklist Codex should use.

## Merge Criteria

Codex has a concise, accurate review checklist for this sprint; smoke/live differences are explicit; no production behavior changes are introduced; checklist can be copied into sprint_closeout after integration.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

- This task deliberately avoids production JS/backend/test changes, so it cannot
  prove the live diary behaviour by itself. Codex must use this as a review aid
  after Claude and Antigravity submit.
- Smoke mode remains useful but intentionally mocked. It should not be treated as
  evidence that the Office dialog auth handshake, live roster endpoint, session
  expiry handling, or backend seed data path is correct.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `orchestration/diary_smoke_live_review.md`;
  `orchestration/agent_inbox/codex/codex-diary-smoke-live-review.md`.
- Verification run: `git diff --check` -> passed. No JS touched, so
  `node --check` is not required.
- Remaining risks: This branch is documentation-only. It cannot validate
  Antigravity's date picker/current-time marker implementation, Claude's test DB
  hardening, or live roster fetching until those submitted branches are integrated
  locally and checked by Codex.
- Exact post-integration manual review checklist for Codex:
  1. Run Claude's focused diary roster/template pytest suites twice in succession
     if feasible and confirm reruns do not leave a partial test DB or fail on
     missing base tables such as `practices`.
  2. In live mode, verify Antigravity's new date picker changes the selected
     diary date and that Prev, Next, Today, Now, and Refresh still work after
     using it.
  3. Confirm date changes in live mode refetch roster/date data, not just the
     visible label.
  4. On today's live diary, verify the Now control scrolls close to the current
     time and the softened current-time marker is visible without obscuring
     appointment text, notes, break labels, or narrow-layout controls.
  5. On a non-today date, verify current-time marker and auto-scroll behaviour is
     not misleading.
  6. In live mode with seeded roster rows, confirm Room 1/2/3 show Dr Shera,
     Nurse, and `[Available]`.
  7. In live mode on a date without roster rows, confirm the diary falls back to
     normal template columns rather than turning every room into `[Available]`.
  8. Confirm appointment cards still map by effective practitioner AHPRA and do
     not appear in label-only rooms.
  9. Open `docs/diary/diary.html?smoke=true` locally or the deployed Pages smoke
     URL and confirm it remains auth-free with mock irregular-time fixtures,
     long/overlapping appointments, Room 2's 10-minute cadence, and Room 3 as
     `[Available]`.
  10. Record explicitly that smoke mode is mock data and does not prove the
      Office dialog auth handshake, live roster endpoint, session expiry
      handling, or backend seed state.
  11. Sweep Refresh, silent auto-refresh, long appointments, booking notes, break
      blocks, off-grid hover bubbles/tooltips, per-column cadence labels, footer
      text, and narrow layout for regressions.
  12. Confirm no booking create/edit/drag/drop/status mutation behaviour was
      introduced by Sprint 5.
