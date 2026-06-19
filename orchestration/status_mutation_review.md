# Controlled Status Mutation Review Checklist

Use this after Codex integrates Claude's backend status mutation contract and
Antigravity's diary status controls. This review is intentionally status-only:
booking create, edit, delete, drag/drop, resize, roster admin, taskpane,
Command Centre, Gemini, SMS, and online booking remain out of scope.

## Preconditions

- Claude submit is integrated or explicitly superseded, with focused appointment
  status, waiting-room, and slots tests passing.
- Antigravity submit is integrated or explicitly superseded, with
  `node --check docs\diary\diary.js` passing and diary asset cache-bust updated
  if diary files changed.
- Codex has inspected that backend changes stayed in appointment
  router/schema/tests and diary changes stayed in `docs/diary/`.

## API Contract Review

1. Confirm unauthenticated status PATCH returns 401.
2. Confirm disallowed roles cannot mutate appointment status.
3. Confirm allowed staff roles can PATCH only appointments in their own
   `practice_id`.
4. Confirm invalid status values are rejected by the enum/schema.
5. Confirm each valid status round-trips in the returned appointment payload:
   Booked, Confirmed, Arrived, InConsult, Completed, Cancelled, NoShow, DNA.
6. Confirm status-only PATCH does not alter patient, practitioner, date, time,
   duration, appointment type, notes, reason, or booking channel.
7. Confirm terminal/non-blocking statuses free slot availability as intended:
   Cancelled, NoShow, DNA. Record whether Completed is deliberately blocking or
   non-blocking before booking edit work begins.

## Diary UI Review

1. Open the live diary from the taskpane and verify status controls are
   discoverable but not always-on clutter.
2. Change one appointment through the normal status path: Booked -> Confirmed ->
   Arrived -> InConsult -> Completed.
3. Confirm each successful change updates the visible card status, colour/badge,
   and any status menu state without a full page reload unless the implementation
   intentionally refreshes.
4. Confirm Cancelled, NoShow, and DNA remain visually de-emphasised and do not
   look like active waiting patients.
5. Narrow the diary window and verify the controls do not crowd patient names,
   booking notes, break labels, date controls, Refresh, or Now.
6. Confirm long, overlapping, off-grid, and note-heavy appointments still render
   and can still be inspected.
7. Confirm smoke mode remains useful for visual status review but is not treated
   as proof of live auth or backend mutation.

## Waiting Room Review

1. After setting a same-day appointment to Booked, Confirmed, Arrived, and
   InConsult, verify `/api/v1/appointments/waiting-room` includes it.
2. After setting the same appointment to Completed, Cancelled, NoShow, and DNA,
   verify the waiting-room endpoint excludes it.
3. Confirm waiting-room ordering still uses `queue_position` first, then
   `start_time_local`.
4. Confirm practitioner filtering and cross-practice isolation still hold after
   status changes.

## Failure And Session Review

1. Force or simulate an expired token and confirm diary status mutation shows a
   clear session-expired path instead of silently reverting or pretending success.
2. Force or simulate a failed PATCH response and confirm the UI preserves the
   last known status, shows a readable error, and allows retry.
3. Confirm rapid repeated clicks or menu changes cannot leave two visible statuses
   for the same appointment.
4. Confirm auto-refresh does not overwrite an in-flight mutation with stale data
   without a visible recovery path.

## Not Required Yet

- Booking create/edit/delete/drag/drop/resize.
- Roster admin UI or room reassignment.
- Waiting-room display app, SMS reminder behavior, kiosk check-in, or online
  booking portal behavior.
- Clinical note, taskpane consultation, Command Centre, or Gemini workflow review.

## Merge Gate

Proceed to booking create/edit planning only if the API contract, live diary UI,
waiting-room behavior, and failure/session checks above are all reviewed or any
exceptions are recorded in `orchestration/sprint_closeout.md`.
