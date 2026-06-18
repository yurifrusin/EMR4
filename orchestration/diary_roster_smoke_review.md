# Diary Roster Smoke Review

Use this checklist after Sprint 4 roster backend and frontend submissions are
integrated locally, before pushing the batch through to `master`.

## Purpose

Confirm the diary can show date-specific room roster assignments without losing
the existing read-only diary behaviours. This review is intentionally limited to
roster visibility and fallback. Booking create/edit/drag/drop/status mutations
remain out of scope.

## Preconditions

- Claude's backend roster contract submit has been reviewed and integrated.
- Antigravity's diary roster consumption submit has been reviewed and integrated.
- Local DB has the latest diary migrations applied and dev seed data loaded if
  the test depends on seeded roster rows.
- Local backend is running on port `8001`, or the deployed diary target is using
  a backend with the same integrated roster contract.

## Browser Checks

1. Normal fallback path:
   - Open the diary through the taskpane or authenticated diary URL.
   - Use a date with no roster rows.
   - Expected: columns fall back to the template, including Room 1 / Dr Alex
     Shera, Room 2 / Nurse, and Room 3 / [Available].

2. Date-specific roster path:
   - Open a date with seeded roster rows.
   - Expected: room order follows the backend roster response; practitioner
     assignments and label-only rooms render in the column headers.
   - Expected: [Available] or equivalent label-only rooms remain visibly
     distinct and do not attract practitioner-mapped appointments.

3. Appointment mapping:
   - Confirm appointments still render under the practitioner whose AHPRA number
     matches the effective roster/template column assignment.
   - Expected: appointments are not duplicated, hidden, or shifted into
     label-only rooms.

4. Date navigation:
   - Click Previous, Next, Today, and Now.
   - Expected: each date change refetches date-specific roster data and preserves
     the existing current-time marker and auto-scroll behaviour for today.

5. Resilience:
   - Exercise or simulate empty roster, roster 404, and roster 401/temporary
     failure paths.
   - Expected: empty/unavailable roster falls back safely where appropriate; a
     true auth failure still shows the existing session-expired behaviour.

6. Existing diary behaviours:
   - Verify Refresh and silent auto-refresh do not flash or reset the grid
     unexpectedly.
   - Verify the 10:00 long booking stays visibly long and booking notes remain
     readable.
   - Verify break blocks, off-grid time edge bubbles/tooltips, per-column cadence
     labels, footer text, and narrow layout still render coherently.

7. Smoke mode:
   - Open `docs/diary/diary.html?smoke=true` locally or the equivalent deployed
     Pages URL.
   - Expected: smoke mode remains auth-free and continues to show the irregular
     timing fixtures, Room 2's 10-minute cadence, Room 3 as [Available], and the
     long/overlapping appointment examples.

## Review Notes To Capture

- Exact URLs tested and whether they were local, deployed Pages, or Office dialog.
- Backend data condition tested: no roster, seeded roster, auth failure, or
  simulated fetch failure.
- Any header/column wording that could confuse reception staff.
- Any regression in flexible-time, notes, or narrow-layout behaviour.
