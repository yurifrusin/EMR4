# antigravity-diary-status-controls

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | ea0b41d |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-diary-status-controls --commit-message "Add diary status controls" --message "Diary status controls ready for Codex review"` |

## Mission

Add restrained read-only-diary status mutation affordances now that the status visual language has passed user review.

## Scope

### In Scope

Edit docs/diary/diary.html, docs/diary/diary.css, and docs/diary/diary.js only. Add practical, low-clutter controls for changing an appointment status through the existing PATCH /api/v1/appointments/{appointment_id}/status endpoint. Preserve the current status badges/colour coding, roster-driven columns, smoke mode, date picker, Now marker, booking notes, long appointments, narrow layout, and auth/session handling. Prefer a compact popover/menu or focused action affordance over always-visible button clutter. Include safe handling for 401/session expiry and failed PATCH responses. Bump diary cache version if diary assets change. Fill Completion Notes before submit.

### Out of Scope

No backend route/model/schema/test changes, no taskpane or Command Centre edits, no drag/drop booking edits, no appointment create/edit form, no roster admin UI, no Gemini/AI changes.

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

Run node --check docs\diary\diary.js. Manually smoke check or describe how to check status controls in smoke/live mode, narrow layout, failed update handling, and that booking drag/drop/edit remains absent. Report exact commands/results.

## Merge Criteria

Diary status controls are discoverable but restrained, use the existing authenticated API, handle success/failure/session expiry clearly, preserve visual/narrow-layout quality, and introduce no booking mutation behavior beyond status changes.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
