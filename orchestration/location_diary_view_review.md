# Location Diary View Review

Use this note for Sprint 16 integration review and user testing. The goal is to
keep physical location, resource modelling, waiting-area flow, and diary screen
layout distinct before EMR4 adds more diary operations or Bernie tooling.

This is a review harness, not production implementation.

## Canonical Vocabulary

| Concept | Meaning | Must Not Mean |
|---|---|---|
| Practice | The tenant, admin, reception, billing, user, and shared patient-database unit. | A physical site or one diary screen. |
| PracticeLocation | A physical site of a practice, such as a clinic address. | A diary page, column group, waiting queue, or practitioner. |
| Room | A physical room/resource position at one location. | A waiting area, attendance status, or patient queue. |
| Bookable resource | The person or resource that can receive a booking; near term this is usually a practitioner. | The visual diary column by itself or the physical room alone. |
| Waiting area | A named physical place where arrived patients wait at a location. | Appointment status, room, practitioner, or queue position. |
| Diary template | The configured day layout for a practice/location: columns, slot cadence, breaks, and labels. | A physical location. |
| Diary roster | The date-specific assignment of rooms/resources/practitioners/labels. | A permanent practitioner identity or a booking. |
| Diary column | The visual column shown on the diary grid for a room/resource/label. | The durable room/resource model by itself. |
| Diary page/view group | A screen-real-estate subset of columns within one physical location. | A second physical location, second practice, or separate patient database. |
| Booking slot | A candidate time interval for a bookable resource. | A rendered grid cell, a guaranteed booking, or an appointment status. |
| Appointment status | Same-day operational flow: Booked, Arrived, InConsult, Completed, Cancelled, NoShow/DNA, plus legacy Confirmed where tolerated. | Patient identity linkage, SMS/reminder reply, or waiting-area assignment. |
| Patient identity | Whether the appointment is linked to an EMR patient record or remains provisional/free-text. | Arrival, attendance confirmation, or SMS reply. |
| Booking confirmation | A future communication/reminder signal that a patient intends to attend. | Patient identity linkage or physical arrival. |

## Design Guardrails

- A practice may have one or many physical locations, but the patient database
  and reception/admin tenant boundary remain at practice level.
- Every room, waiting area, roster row, diary template variant, and appointment
  location association should be reviewable against a physical
  `PracticeLocation`.
- A one-location practice should feel natural: no fake multi-site selector, no
  forced "location admin" ceremony, and no new visual clutter.
- A multi-location practice should make the active physical location explicit
  before staff mutate appointments, waiting areas, or rosters.
- Diary page/view groups solve screen width within a location. They may filter
  or paginate columns, but they must not create duplicate physical locations.
- Waiting Room cards/panels, main diary appointment blocks, booking slots, and
  status controls are separate surfaces. A change to one must not be reviewed as
  proof that another changed correctly.
- The word "slot" should mean a candidate bookable interval in API/tool review.
  Say "grid cell" or "appointment block" when discussing the rendered diary.
- The word "room" should mean a physical room. Say "column" for the visual diary
  column and "waiting area" for where arrived patients sit.
- The word "confirmed" needs a qualifier: verified patient identity, booking
  confirmation, legacy `Confirmed` status, or reminder reply.

## Backend Integration Review

After Claude's location-scoped diary backend branch is submitted, Codex should
check:

1. Practice-scoped reads still cannot leak cross-practice locations, rooms,
   waiting areas, rosters, templates, appointments, or practitioners.
2. `PracticeLocation` is treated as a physical site under a practice, not as a
   substitute tenant.
3. Rooms belong to a practice location or otherwise have an explicit safe
   fallback that does not imply "one practice has exactly one location forever".
4. Waiting areas belong to a practice location or have a clear migration path
   from earlier practice-scoped/default data.
5. Diary templates and rosters can be resolved for the active physical location
   and date without requiring the diary UI to infer physical site from column
   label text.
6. Appointments expose or preserve a clear `location_id` contract. Creating,
   updating, check-in, and waiting-room reads should not silently move an
   appointment between physical sites.
7. Room default waiting-area logic remains physical: a room default can suggest
   an arrived patient's waiting area, but it is not itself an attendance state.
8. One-location fallback data remains deterministic after `python seed.py`.
9. Multi-location test/dev data, if added, uses distinct location names and at
   least one room/waiting area/roster row per location so the UI can be reviewed.
10. Route and payload names are documented clearly enough for Antigravity's
    diary selector to consume without guessing.

## Diary UI Integration Review

After Antigravity's location selector/view-boundary branch is submitted, Codex
should check:

1. With one active physical location, the diary opens directly into the day and
   does not display a confusing selector or empty location chrome.
2. With multiple active physical locations, the active site is visible in the
   diary header or equivalent persistent context.
3. Changing location refreshes diary template, roster, appointments, and
   waiting-area data for that physical location without carrying stale cards or
   appointment blocks from the previous site.
4. If the UI also offers diary page/view groups, those controls are labelled as
   views/pages/groups, not locations.
5. A view/page/group switch changes visible columns only. It must not change
   active physical location, selected waiting area, patient identity, or
   appointment status.
6. Main diary appointment block geometry remains unchanged unless the approved
   Antigravity packet explicitly changes it.
7. Waiting Room side-panel cards remain a separate review surface from main
   diary appointment blocks. Do not call both "stacking" without naming which
   surface is under review.
8. Status controls do not become the mechanism for choosing location or waiting
   area.
9. Provisional/linked patient display remains separate from location selector
   and attendance status.
10. Narrow layout still shows enough location context that reception staff do
    not accidentally mutate the wrong site.

## Bernie Tool Vocabulary

Future Bernie tools should require location/resource context when the action can
affect a diary, room, waiting area, roster, or appointment.

Recommended tool argument naming:

| Tool Area | Required Context |
|---|---|
| `find_slots` | `practice_id`, `location_id`, date range, bookable resource/practitioner, appointment type/duration. |
| `prepare_booking` | `location_id`, bookable resource/practitioner, appointment date/time/duration, linked or provisional patient identity. |
| `prepare_booking_update` | Existing appointment id plus any changed `location_id`, room/resource, time, duration, type, reason, or notes. |
| `check_in_patient` | Appointment id, intended attendance status, optional `waiting_area_id`, and current `location_id` for confirmation text. |
| `assign_waiting_area` | Appointment id, `waiting_area_id`, and location consistency check. |
| `change_attendance_status` | Appointment id and status only; no implicit patient linkage, booking confirmation, or location move. |
| `handoff_to_receptionist` | Plain-language ambiguity reason, including wrong-location or multi-location uncertainty where relevant. |

Bernie response text should name the physical location when it proposes or
executes a diary mutation. Example: "Prepare a 20-minute booking for Margaret at
Main Street, Room 1 with Dr Shera" is reviewable. "Book Margaret in Room 1" is
ambiguous if the practice has more than one physical site.

## Manual User Review Checklist

1. Start from a fresh local dev stack, apply migrations if the backend branch
   adds them, run `python seed.py`, and hard refresh the diary.
2. Review the one-location case first. Confirm the diary still feels like the
   existing simple practice diary and that no fake location workflow is imposed.
3. If multi-location seed or test data is present, switch between locations and
   confirm each site shows its own rooms, waiting areas, rosters, and
   appointments.
4. Confirm a room/resource label visible in one location does not cause
   appointments from another location to appear merely because the label text is
   similar.
5. Confirm Waiting Room tabs/sections filter by physical waiting area at the
   active location, not by appointment status or room name alone.
6. Confirm active-location switching does not alter appointment status, linked
   patient identity, booking confirmation, waiting-area assignment, or notes.
7. If diary page/view groups exist, switch groups and confirm only visible
   columns change.
8. Test narrow/windowed diary layout. The active physical location should remain
   visible enough to avoid wrong-site operations.
9. Open or create a provisional appointment if available. Confirm unverified
   identity language remains separate from location and status language.
10. Record any label that feels overloaded, especially "Confirmed", "Room",
    "Waiting Room", "slot", "page", "view", or "stacking".

## API Spot-Check Snippets

These are review aids. Use actual route names and IDs from the integrated Sprint
16 backend submission; do not treat these snippets as a final contract if Claude
chooses different names.

```powershell
$base = "http://localhost:8001/api/v1"
$headers = @{ Authorization = "Bearer <JWT>" }

# Discover locations for the logged-in practice, if the submitted backend exposes
# such an endpoint. Expected: only this practice's active locations.
$locations = @(Invoke-RestMethod `
  -Method Get `
  -Uri "$base/diary/locations" `
  -Headers $headers)

$locationId = $locations[0].id
$today = (Get-Date).ToString("yyyy-MM-dd")

# Review location-scoped template/roster reads using the final submitted routes.
Invoke-RestMethod `
  -Method Get `
  -Uri "$base/diary/template?location_id=$locationId" `
  -Headers $headers

Invoke-RestMethod `
  -Method Get `
  -Uri "$base/diary/roster?date=$today&location_id=$locationId" `
  -Headers $headers

# Review appointment filtering. Expected: rows belong to the requested physical
# location and do not include another site's appointments.
Invoke-RestMethod `
  -Method Get `
  -Uri "$base/appointments?date_from=$($today)T00:00:00&date_to=$($today)T23:59:59&location_id=$locationId" `
  -Headers $headers
```

## Not Required Yet

- Drag/drop, resize handles, appointment block geometry changes, or overlap lane
  redesign.
- Full practice/location/room/waiting-area admin UI.
- Public online booking, kiosk check-in, patient PWA, SMS/reminder confirmation,
  or phone/voice automation.
- Taskpane, Command Centre, Scribe, Gemini, billing, results, or clinical-note
  regression.
- Autonomous Bernie runtime. Tool vocabulary only; no model-to-database path.

## Merge Gate

Proceed beyond Sprint 16 only when integration review shows that physical
location is explicit where needed, one-location fallback remains simple,
multi-location data does not leak across sites or practices, and diary
view/page/group layout is not being modelled as physical location.

Drag/drop/resize and Bernie write tools should remain deferred until location,
room/resource, waiting-area, roster, appointment identity, and attendance-state
semantics are all stable and reviewable.
