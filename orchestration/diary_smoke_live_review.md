# Diary Smoke and Live Review

Use this checklist after Sprint 5 submissions are integrated locally, before
pushing the batch through to `master`.

## Purpose

Confirm the diary remains reviewable in both modes after the date control,
current-time marker, roster consumption, and test database hardening work lands.
This review is intentionally read-only. Booking create/edit/drag/drop/status
mutations remain out of scope.

## Smoke Mode Versus Live Diary

- `?smoke=true` is an auth-free visual fixture. It intentionally uses mock
  template, appointment, type, and roster-like data embedded in the diary client.
- Smoke mode may differ from the taskpane popout because it does not prove the
  Office dialog auth handshake, live backend API calls, session expiry handling,
  database seed state, or deployed ngrok/backend wiring.
- Live diary means opening the diary through the taskpane popout, or an
  authenticated diary URL, against the integrated backend. Use live mode for
  roster-driven columns, auth failure behaviour, and real appointment mapping.
- A smoke-only pass is useful for fast layout checks, but it is not enough to
  close Sprint 5 if roster or auth behaviour changed.

## Preconditions

- Claude's test DB hardening submit has been reviewed and integrated, or its
  remaining risk has been explicitly recorded.
- Antigravity's diary date/Now-marker submit has been reviewed and integrated.
- Sprint 4 roster consumption remains present: live diary fetches
  `/api/v1/diary/roster?date=YYYY-MM-DD` and falls back safely when appropriate.
- Local DB has the latest migrations applied and `python seed.py` has been run
  if seeded roster rows are part of the review.
- Local backend is running on port `8001`, or the deployed diary target is using
  a backend with the same integrated sprint code.

## Codex Integration Checks

1. Claude test DB hardening:
   - Run the focused diary roster/template pytest suites twice in succession if
     feasible.
   - Expected: reruns do not leave a partial test DB or fail on missing base
     tables such as `practices`.
   - If a broader test run is skipped, record why and whether fixture changes
     were narrow enough to keep the risk contained.

2. Antigravity date control:
   - Verify the new date picker/control changes the selected diary date.
   - Expected: Prev, Next, Today, Now, and Refresh still work after using the
     picker.
   - Expected: changing the selected date triggers live roster/date data reload
     rather than only changing the label.

3. Current-time marker:
   - On today's date, verify Now scrolls close to the current time and the marker
     remains visible.
   - Expected: the marker is softer than the previous heavy line and does not
     obscure appointment text, notes, break labels, or narrow-layout controls.
   - On non-today dates, verify the marker/auto-scroll behaviour is not
     misleading.

4. Live roster-driven columns:
   - In live mode, use today's seeded roster rows and confirm Room 1/2/3 show Dr
     Shera, Nurse, and `[Available]` as expected.
   - Navigate to a date without roster rows and confirm template fallback still
     shows the normal columns instead of turning every room into `[Available]`.
   - Confirm appointment cards still map by effective practitioner AHPRA and do
     not appear in label-only rooms.

5. Smoke mode:
   - Open `docs/diary/diary.html?smoke=true` locally or the equivalent deployed
     Pages URL.
   - Expected: smoke mode remains auth-free and shows the mock irregular-time
     fixtures, long/overlapping appointments, Room 2's 10-minute cadence, and
     Room 3 as `[Available]`.
   - Do not treat smoke-mode mock roster/header values as proof of live backend
     roster behaviour.

6. Regression sweep:
   - Confirm Refresh and silent auto-refresh do not flash or reset the grid
     unexpectedly.
   - Confirm long appointments, booking notes, break blocks, off-grid hover
     bubbles/tooltips, per-column cadence labels, footer text, and narrow layout
     still render coherently.
   - Confirm no booking mutation UI or behaviour was introduced by this sprint.

## User Review After Deploy

Ask the user to manually review the diary after the final push has deployed:

1. Open/reopen the Word Online add-in, then open the diary from the taskpane.
2. Use the date picker to jump to today, tomorrow, and a manually chosen future
   date; confirm the visible date and columns update each time.
3. On today's seeded date, confirm Room 1/2/3 show Dr Shera, Nurse, and
   `[Available]`.
4. Navigate to a date without roster rows and confirm the diary falls back to the
   normal template columns.
5. Press Now on today's date and confirm the current-time marker is useful but
   visually quiet.
6. Check that notes, long appointments, break blocks, Refresh, and narrow window
   layout still feel usable.
7. Optionally open `https://yurifrusin.github.io/EMR4/diary/diary.html?smoke=true`
   to confirm the smoke fixture still works, remembering that smoke mode is mock
   data and not a live roster/auth test.

## Review Notes To Capture

- Exact URLs tested and whether each was smoke, live local, deployed Pages, or
  Office dialog.
- Backend data condition tested: seeded roster, no roster, auth failure, or
  simulated fetch failure.
- Exact pytest commands/results from Claude's test DB hardening verification.
- Whether Antigravity's date picker and softer Now marker were checked in both
  normal and narrow widths.
- Any header wording, marker contrast, or smoke/live mismatch that could confuse
  reception staff.
