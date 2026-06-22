# EMR4 Sprint Closeout

This file tracks what the user should review after each integrated sprint batch
of parallel-agent work. Codex updates it after submitted work has been polled,
reviewed, integrated, verified, pushed, and audited.

## Current Closeout

| Item | Value |
|---|---|
| Batch | Sprint 16: Location-Aware Diary Foundations |
| Integrated through | `0298a12` plus audited closeout status update |
| Status | Pushed, mirrors realigned, audited; ready for user review |
| Last updated | 2026-06-22 |

## What Changed

- Added location scoping to diary resources: `Room`, `WaitingArea`, and
  `DiaryTemplate` now carry nullable `location_id` links to `PracticeLocation`.
- Added `GET /api/v1/diary/locations` and optional `location_id` filters for
  diary template, roster, waiting-area, appointment-list, and waiting-room reads.
- Seed now creates the dev `Main Street Surgery` location and attaches seeded
  rooms, waiting areas, roster, and sample appointments to it.
- Added a Codex integration repair so room display order is unique within each
  physical location, not across the whole practice. This allows each site to
  have its own first room.
- The live diary location selector now consumes `/diary/locations`, persists the
  active physical location, and passes `location_id` to live diary reads and new
  booking creation. Smoke mode still offers Main/North/East mock locations.
- Hotfix: appointment location filtering and conflict detection now agree for
  legacy appointments with no `location_id`. In a one-location practice, those
  older appointments are treated as belonging to the only active location so
  they are visible in the diary instead of becoming hidden conflicts.
- Added `orchestration/location_diary_view_review.md` to keep practice,
  physical location, room/resource, waiting area, diary view/page group,
  booking slot, appointment status, patient identity, and booking confirmation
  separate for future diary and Bernie work.
- Updated diary assets to `v=70`.

## Recommended User Review

After this is pushed/deployed, review the live diary:

1. Restart backend if needed, run migrations if not already current, run
   `python seed.py`, and hard refresh the diary. Confirm it loads
   `diary.js?v=70`.
2. Open the diary from the taskpane. Confirm the location selector shows the
   seeded `Main Street Surgery` (or the current dev location name) and the diary
   still loads today's appointments, roster, and Waiting Room data.
3. Create one new booking in Room 1. Confirm it saves and remains visible after
   refresh. This checks that new bookings inherit the active `location_id`.
4. If a conflict warning names an unexpected appointment time, check that the
   conflicting appointment is visible in the filtered diary. Legacy unscoped
   dev bookings should no longer be hidden in a one-location practice.
5. In smoke mode (`?smoke=true`), switch between Main Clinic, North Branch, and
   East Specialty Suite. Confirm grid appointments and Waiting Room side-panel
   cards filter by the selected mock location.
6. Confirm the one-location live case does not feel like a new admin workflow:
   the location should be visible context, not a busy multi-site control.
7. Confirm existing Waiting Room area tabs and sections still behave as before.

## Not Required Before Moving On

- No drag/drop/resize appointment testing is required yet.
- No taskpane Patient Details duplicate testing is required for Sprint 16.
- No Command Centre, Scribe, Gemini, billing, results, letters, medications, or
  clinical-note regression is required for this sprint.
- No patient document rewrite, public online-booking, kiosk, SMS/reminder, or
  Bernie runtime testing is required.

## Known Follow-Up

- Patient Details is still a foundation slice. Add stronger validation, Medicare
  IRN polish, IHI/Medicare verification hooks, duplicate-candidate review, and a
  proper shared demographic model before relying on it in routine use.
- GitHub Pages deployment should be kept to canonical `master`.
- Multi-location admin UI does not exist yet. For now, location data is seeded
  and API-backed; proper practice/location/room/waiting-area administration is a
  future slice.
- The diary still needs a future page/view-group model for wide locations with
  too many columns. That is a screen-layout concern inside one physical location.
- Physical waiting areas now exist in the backend, but room/resource admin and
  per-room default waiting-area editing are still future work. The Sprint 14
  design reference is `orchestration/resource_admin_bernie_tool_design.md`.
- Terminal appointment statuses now auto-clear `waiting_area_id` when omitted
  from PATCH. Continue watching whether this feels right in practice, especially
  when status changes are corrected after accidental completion/cancellation.
- The diary waiting-area UI should eventually auto-focus the area associated with
  the active room/column and support true stacked/condensed cards inside
  high-volume Waiting Room sections such as Finished.
- The project must support practices with multiple physical locations served by
  one reception/practice-management team and one patient database. The next
  diary/resource work should make the location boundary explicit before more
  diary features assume a single physical site.
- One location may still need multiple diary page views or column groups because
  of screen real estate. Treat this as a view/pagination problem within a
  location, separate from choosing a practice location/site.
- Sprint 16 review should use `orchestration/location_diary_view_review.md` to
  keep practice, physical location, room/resource, waiting area, diary view/page
  group, booking slot, appointment status, patient identity, and booking
  confirmation language separate.
- Appointment state still needs the planned distinction between patient identity
  linkage, attendance workflow, and future SMS/reminder confirmation.
- Bernie should continue to follow
  `orchestration/resource_admin_bernie_tool_design.md`: typed proposals,
  human-confirmed writes, and audit.
- Drag/drop/resize should remain deferred until the resource model and patient
  flow semantics are settled.
- The `pytest_asyncio` loop-scope deprecation warning remains.
- Do not run two pytest processes against the same `gp_pms_test` database in
  parallel; concurrent runs can collide during fixture setup/teardown.
- Future data cleanup should explicitly backfill or review old appointments
  where `location_id` is null before multi-location production use.

## Verification

Codex/orchestrator verification for Sprint 16:

- `node --check docs\diary\diary.js` -> passed
- `.venv\Scripts\python.exe -m py_compile app\models\diary.py app\routers\diary.py app\routers\appointments.py app\schemas\diary.py seed.py` -> passed
- `git diff --check` -> passed
- `.venv\Scripts\python.exe -m pytest tests\test_location_scoped_diary.py tests\test_waiting_area_checkin_defaults.py tests\test_waiting_area_checkin_contract.py tests\test_waiting_area_contract.py tests\test_appointment_status_mutations.py tests\test_diary_template.py tests\test_diary_roster.py -q --tb=short -p no:randomly` -> 82 passed, 1 warning
- `.venv\Scripts\alembic.exe upgrade head` -> applied `g7h8i9j0k1l2`
- `.venv\Scripts\python.exe seed.py` -> created/linked the dev practice location
- `.venv\Scripts\python.exe -m py_compile app\routers\appointments.py` -> passed
- `.venv\Scripts\python.exe -m pytest tests\test_booking_create_edit.py -q --tb=short -p no:randomly` -> 31 passed, 1 warning
- `.venv\Scripts\python.exe -m pytest tests\test_location_scoped_diary.py -q --tb=short -p no:randomly` -> 18 passed, 1 warning
- Live API spot-check: `GET /appointments?...&location_id=<Main Street Surgery>`
  now includes legacy null-location bookings such as the `11:35` dev booking.

## Recommended Next Direction

The next sprint should stay on the diary/resource track and make the new
location boundary operationally useful without building a full admin console.
Recommended options: add a small location/room/waiting-area seed/review harness
for multi-site smoke testing; improve booking modal location context; or start
the room/resource admin foundation that will eventually let a practice manager
edit locations, rooms, default waiting areas, and diary templates.

---

## Sprint 15 Review Harness - Waiting Room Check-In Operations

Use this section after the Sprint 15 backend and diary UI worker branches are
reviewed and integrated. It is a user-review harness, not evidence that the
implementation has already landed.

### Design Guardrails

- A **Waiting Area** is a named physical place where arrived patients wait.
- A **Room** is a physical consult/procedure room. It may have a default waiting
  area, but it is not itself a waiting area.
- A **Practitioner** is the bookable clinician/resource for the appointment.
- **Attendance status** is same-day workflow: Booked, Arrived/Waiting,
  InConsult, Completed, Cancelled, NoShow, or DNA.
- **Booking confirmation** is the patient's intention/response to attend and is
  separate from attendance status.
- **Patient identity** should be described as **Verified** or **Unverified**.
  Do not use "Confirmed" for identity; reserve it for booking attendance intent
  or legacy appointment status only when clearly qualified.
- Bernie may execute deterministic, low-risk operational actions with audit and
  reporting, such as an unambiguous check-in/status correction. Slot selection,
  booking choice, rescheduling, externally consequential actions, clinical
  actions, and ambiguous identity cases still require staff confirmation.
- Any future request for "stacking" must specify the surface:
  **Waiting Room cards** inside the side panel, or **diary appointment blocks**
  on the room/time grid. These are different layout problems and should not be
  changed together by default.

### Manual User Review Checklist

1. Pull latest, restart the backend, rerun `python seed.py`, and hard refresh
   the deployed/local diary surface. Confirm the diary loads `diary.js?v=68`.
2. Open today's diary and the Waiting Room panel. Confirm Expected Today cards
   are compact, chronological by appointment time, and readable without looking
   like the main diary grid's overlapping appointment blocks.
3. Confirm ordinary diary appointment blocks on the room/time grid still use
   their existing time geometry. The Sprint 15 Waiting Room work must not
   introduce appointment-block stacking/cascade changes in the main diary grid.
4. Check in an appointment from Expected Today without manually selecting a
   waiting area when the appointment's room has a default. Confirm the patient
   appears in the correct/default Waiting Area section and the appointment
   detail shows that area consistently.
5. Check in an appointment while explicitly selecting a non-default waiting
   area. Confirm the explicit choice wins over the room default and survives a
   refresh.
6. If the UI supports changing the waiting area after arrival, move an arrived
   patient to another waiting area. Confirm the patient moves sections without
   changing practitioner, room, appointment time, or patient identity state.
7. Move a checked-in patient through Waiting/Arrived -> InConsult -> Completed.
   Confirm Waiting Room sections update immediately and after refresh:
   Waiting/Arrived patients are active in their area, InConsult patients appear
   only in the in-consult section, and Completed patients appear only in the
   finished/terminal section if that section is displayed.
8. Set terminal statuses Cancelled, NoShow, and DNA on appointments that had a
   waiting area. Confirm they do not remain incorrectly visible in active
   Waiting Area sections. If the backend preserves `waiting_area_id` for
   history, the active UI must still filter terminal statuses out of active
   waiting lists.
9. Test a practice/day with exactly one active waiting area. Confirm the UI does
   not show a clipped, fake, or confusing tab strip; the single area should read
   as the natural context rather than a broken multi-tab control.
10. Test an Unverified/provisional appointment if available. Check-in may be
    allowed, but the UI should not imply that arrival verified the patient
    identity. The displayed language should keep identity verification separate
    from attendance.

### Backend / API Spot Checks

Use these only after getting a staff JWT and real IDs from the dev database or
browser network panel. Route names may need the `/api/v1` prefix depending on
the caller base URL.

```powershell
$base = "http://localhost:8001/api/v1"
$headers = @{ Authorization = "Bearer <JWT>" }
$appointmentId = "<appointment-uuid>"
$waitingAreaId = "<waiting-area-uuid>"

# Explicit check-in to a waiting area.
Invoke-RestMethod -Method Patch `
  -Uri "$base/appointments/$appointmentId/status" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body (@{ status = "Arrived"; waiting_area_id = $waitingAreaId } | ConvertTo-Json)

# Default/no explicit waiting area path. Verify this follows the integrated
# backend contract: either room default assignment or existing assignment
# preservation, as specified by the Sprint 15 backend worker.
Invoke-RestMethod -Method Patch `
  -Uri "$base/appointments/$appointmentId/status" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body (@{ status = "Arrived" } | ConvertTo-Json)

# Terminal status should not leave the patient visible in active waiting areas.
Invoke-RestMethod -Method Patch `
  -Uri "$base/appointments/$appointmentId/status" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body (@{ status = "Completed"; waiting_area_id = $null } | ConvertTo-Json)
```

API review expectations:

- Cross-practice or inactive `waiting_area_id` values are rejected.
- Explicit `waiting_area_id = null` clears the appointment's waiting area when
  the contract allows clearing.
- Moving to InConsult, Completed, Cancelled, NoShow, or DNA does not strand the
  patient in active waiting-area feeds.
- Status transitions do not link a provisional patient to a real patient record,
  do not change booking confirmation state, and do not alter practitioner/room
  assignment unless a separate explicit endpoint says so.

### Sprint 15 Review Questions For Codex/Orchestrator

- Did Claude's backend branch make terminal-status clearing explicit, or does it
  preserve `waiting_area_id` for history while filtering in the waiting-room
  endpoint/UI?
- Did Antigravity keep Expected Today compacting scoped to Waiting Room cards
  only, with no diary-grid appointment geometry changes?
- Does the single-waiting-area state read naturally, or should the next UI slice
  replace tabs with a simple heading/count when only one active area exists?
- Are there audit hooks yet for Bernie-style direct check-in/status execution?
  If not, keep Bernie write tools at proposal/report level or limit execution to
  the already validated route behaviour.

---

## Sprint 16 Review Harness - Location-Aware Diary Foundations

Use `orchestration/location_diary_view_review.md` after the Sprint 16 backend
and diary UI worker branches are reviewed and integrated. This closeout pointer
is intentionally brief; the harness file owns the vocabulary table, backend
integration review, diary UI review, Bernie tool vocabulary, manual user review,
API spot checks, and merge gate.

Codex/orchestrator should specifically report whether:

- Backend location scoping keeps practice tenancy separate from physical
  location scoping.
- Rooms, waiting areas, diary templates, rosters, and appointments are
  associated with a physical location or have a deliberate safe fallback.
- The diary UI exposes the active physical location when there is more than one
  site, while the one-location case stays uncluttered.
- Diary page/view groups are treated as screen layout inside a location, not as
  extra locations.
- Waiting Room panels/cards, main diary appointment blocks, booking slots, and
  status controls remain separate review surfaces.
- Bernie tool language requires explicit location/resource context before any
  future write proposal.
