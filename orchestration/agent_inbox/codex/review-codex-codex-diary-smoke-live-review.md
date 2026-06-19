# review-codex-codex-diary-smoke-live-review

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/diary-smoke-live-review` |
| Source Task | `codex-diary-smoke-live-review` |
| Status | integrated |

## Review Request

Diary smoke/live review checklist ready for Codex review

## Worker Completion Notes

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

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/codex/codex-diary-smoke-live-review.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result: Accepted and integrated. The branch is documentation-only and
  provides the Sprint 5 smoke/live review checklist.
- Follow-up required: Use `orchestration/diary_smoke_live_review.md` during
  post-deploy user review and before the next mutation-oriented sprint.
