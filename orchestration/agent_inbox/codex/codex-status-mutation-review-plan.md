# codex-status-mutation-review-plan

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/status-mutation-review-plan` |
| Status | integrated |
| Created | ea0b41d |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-status-mutation-review-plan --commit-message "Add status mutation review plan" --message "Status mutation review plan ready for Codex review"` |

## Mission

Prepare the integration and user-review checklist for controlled appointment status mutation before booking edit work begins.

## Scope

### In Scope

Documentation/checklist only. Inspect orchestration/patient_flow_review.md, orchestration/sprint_closeout.md, orchestration/parallel_workstreams.md, the appointment status route/tests, and diary status UI expectations. Add or update a small orchestration checklist that defines the post-integration review path for status mutation: API checks, diary UI checks, waiting-room behavior, failure/session handling, and what remains out of scope. Fill Completion Notes before submit.

### Out of Scope

No production backend/frontend implementation, no tests, no migrations, no taskpane/Command Centre/Gemini changes, no booking create/edit/drag/drop work.

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

Run git diff --check. No JS/Python test required unless implementation files are touched. Completion Notes must include the exact manual review checklist Codex should use after integrating Claude and Antigravity.

## Merge Criteria

Codex has a concise review checklist for status mutation controls; user review criteria are explicit; no production behavior changes are introduced.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `orchestration/status_mutation_review.md` added. No production backend/frontend code, tests, migrations, taskpane, Command Centre, Gemini, or booking mutation implementation was edited.
- Verification run: `git diff --check` -> passed.
- Remaining risks: This is a review plan only. It assumes Claude and Antigravity submits define the final endpoint/UI behavior. Codex should update `orchestration/sprint_closeout.md` during integration if their actual implementation intentionally differs from this checklist, especially around whether `Completed` blocks future slot availability.

Manual review checklist Codex should use after integrating Claude and Antigravity:

1. Confirm Claude's submit is integrated or superseded with focused appointment status, waiting-room, and slots tests passing.
2. Confirm Antigravity's submit is integrated or superseded with `node --check docs\diary\diary.js` passing and diary cache-bust updated if diary assets changed.
3. Confirm the integrated diff stays scoped: backend status contract in appointment router/schema/tests, diary controls in `docs/diary/`, and no taskpane, Command Centre, Gemini, migrations, roster admin, or booking create/edit/drag/drop work unless explicitly justified.
4. API: unauthenticated status PATCH returns 401.
5. API: disallowed roles cannot mutate appointment status.
6. API: allowed staff roles can PATCH only appointments in their own `practice_id`.
7. API: invalid status values are rejected by enum/schema validation.
8. API: Booked, Confirmed, Arrived, InConsult, Completed, Cancelled, NoShow, and DNA each round-trip in the returned appointment payload.
9. API: status-only PATCH does not alter patient, practitioner, date, time, duration, appointment type, notes, reason, or booking channel.
10. API/slots: Cancelled, NoShow, and DNA free slot availability. Record whether Completed is deliberately blocking or non-blocking before booking edit work begins.
11. Diary UI: open the live diary from the taskpane and verify status controls are discoverable but not always-on clutter.
12. Diary UI: change one appointment through Booked -> Confirmed -> Arrived -> InConsult -> Completed and confirm each success updates visible card status, colour/badge, and menu state.
13. Diary UI: set Cancelled, NoShow, and DNA and confirm they remain visually de-emphasised and do not look like active waiting patients.
14. Diary UI: narrow the diary window and confirm controls do not crowd patient names, booking notes, break labels, date controls, Refresh, or Now.
15. Diary UI: confirm long, overlapping, off-grid, and note-heavy appointments still render and can still be inspected.
16. Diary UI: confirm smoke mode remains useful for visual review but is not treated as proof of live auth or backend mutation.
17. Waiting room: after Booked, Confirmed, Arrived, and InConsult, verify `/api/v1/appointments/waiting-room` includes the same-day appointment.
18. Waiting room: after Completed, Cancelled, NoShow, and DNA, verify `/api/v1/appointments/waiting-room` excludes the appointment.
19. Waiting room: confirm ordering remains `queue_position` first, then `start_time_local`.
20. Waiting room: confirm practitioner filtering and cross-practice isolation still hold after status changes.
21. Failure/session: force or simulate expired token and confirm the diary shows a clear session-expired path.
22. Failure/session: force or simulate failed PATCH and confirm the UI preserves the last known status, shows a readable error, and allows retry.
23. Failure/session: rapid repeated status clicks or menu changes cannot leave two visible statuses for the same appointment.
24. Failure/session: auto-refresh does not overwrite an in-flight mutation with stale data without a visible recovery path.
25. Out of scope: do not require booking create/edit/delete/drag/drop/resize, roster admin, waiting-room display app, SMS, kiosk, online booking, clinical note, taskpane consultation, Command Centre, or Gemini review for this sprint.
