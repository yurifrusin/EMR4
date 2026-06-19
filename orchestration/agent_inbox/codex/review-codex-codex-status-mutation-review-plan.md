# review-codex-codex-status-mutation-review-plan

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/status-mutation-review-plan` |
| Source Task | `codex-status-mutation-review-plan` |
| Status | queued |

## Review Request

Status mutation review plan ready for Codex review

## Worker Completion Notes

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

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/codex/codex-status-mutation-review-plan.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
