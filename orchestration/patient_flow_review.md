# Patient Flow Review Checklist

This checklist covers read-only patient-flow visibility before EMR4 adds booking
mutation, drag/drop, or status-update controls.

## Status Semantics

| Status | Operational Meaning | Diary Review Expectation | Waiting Room Expectation |
|---|---|---|---|
| Booked | Appointment exists, no same-day attendance signal yet | Visible as a normal appointment card with patient name, reason, duration, and type accent | Included until a terminal status replaces it |
| Confirmed | Patient has confirmed attendance | Visually stronger than Booked without implying arrival | Included |
| Arrived | Patient has checked in and is waiting | Clearly scan-able as waiting/ready for rooming | Included and ordered by `queue_position`, then local start time |
| InConsult | Patient is currently with a clinician | Distinct from Arrived and Completed; should not look available | Included |
| Completed | Consultation/appointment is finished | If shown in diary, must read as completed, not actionable or waiting | Excluded |
| Cancelled | Appointment cancelled before attendance | If shown in diary, visually de-emphasised and non-blocking for future booking logic | Excluded |
| NoShow | Patient did not attend | If shown in diary, visually de-emphasised and distinct from Cancelled if possible | Excluded |
| DNA | Did-not-attend status, retained where practice uses this wording | If shown in diary, visually de-emphasised and distinct from active flow | Excluded |

## Post-Integration User Review

1. Open the live diary from the taskpane and confirm normal Booked appointments
   remain easy to read.
2. In smoke mode, verify Confirmed, Arrived, InConsult, Completed, Cancelled,
   NoShow, and DNA states are visually distinguishable without needing to read
   a hidden tooltip.
3. Narrow the diary window and confirm status affordances do not crowd patient
   names, booking notes, break labels, or header controls.
4. Confirm the current-time marker remains visible but does not dominate status
   colours or cover appointment text.
5. Check that long appointments, overlapping appointments, off-grid appointments,
   and booking notes still render as before.
6. Confirm terminal statuses do not appear in the waiting-room endpoint, while
   Booked, Confirmed, Arrived, and InConsult do.
7. Confirm waiting-room results are scoped to today, practice, optional
   practitioner filter, and ordered by `queue_position` before local start time.
8. Record whether the status badges feel useful or too visually busy before
   proceeding to status mutation controls.

## Not Yet Required

- Do not test booking create/edit/drag/drop yet; those controls remain out of
  scope.
- Do not test receptionist status-change controls yet; Sprint 6 only clarifies
  read-only state.
- Do not treat smoke mode as proof of live auth, roster, or waiting-room backend
  behaviour.

## Follow-Up Questions

- Should Completed appointments stay visible in the main diary, move to a
  filtered view, or remain visible but de-emphasised?
- Should Cancelled, NoShow, and DNA all occupy the diary grid, or should some be
  hidden by default once booking mutation exists?
- Should the waiting-room view later split Arrived from InConsult into separate
  operational lanes?
