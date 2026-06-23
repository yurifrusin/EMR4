# EMR4 Sprint Closeout

This file tracks what the user should review after each integrated sprint batch
of parallel-agent work. Codex updates it after submitted work has been polled,
reviewed, integrated, verified, pushed, and audited.

## Current Closeout

| Item | Value |
|---|---|
| Batch | Sprint 19: Resource Admin Foundations |
| Integrated through | Sprint 19 integration batch |
| Status | Integrated and pushed; diary asset v82 deployed, pending user review |
| Last updated | 2026-06-23 |

## What Changed

- Added the first backend admin contract for diary physical rooms and waiting
  areas: list rooms, create/update/soft-archive rooms, and create/update/
  soft-archive waiting areas.
- Added Admin/PracticeOwner RBAC for resource mutations while preserving normal
  authenticated read paths for diary resource data.
- Added practice and location scoping plus active-resource validation for room
  `default_waiting_area_id`.
- Added focused `tests/test_diary_resource_admin.py` coverage for auth gates,
  role gates, practice isolation, CRUD, soft archive, duplicate room order
  conflict handling, and roster preservation after archive.
- Added a restrained diary Resource Administration modal for rooms and waiting
  areas under the active location context, with smoke-mode mock CRUD and visible
  success/failure feedback.
- Added `orchestration/resource_admin_review.md` as the Sprint 19 review harness
  and clarified the post-poll review/integration rule in protocol docs.
- During Codex integration, repaired the diary UI adapter to use the final
  backend `PATCH` soft-archive contract instead of `PUT`/`DELETE`.
- During Ariadne self-testing, found and hotfixed two live UI issues before
  handing user tests back: Office.js blocks native `window.confirm`, so archive
  now uses a safe second-click fallback; Admin affordance visibility now uses
  a more robust role check with `/auth/me` fallback and tolerant role spelling;
  and the Admin entry point is visible/discoverable with access denied inside
  the modal for non-admin users while backend RBAC still protects writes.
- During user review, hotfixed the resource-admin modal so create/edit forms
  show explicit Save/Cancel actions at the top and bottom, newly saved resources
  default to the next display order, refresh into view with a highlight, and the
  Waiting Room waiting-area tabs use a visible horizontal scrollbar when the
  tab set overflows.
- During user review, hotfixed the Waiting Room filter tabs so configured
  waiting areas are the canonical source, ordered by admin `display_order`, old
  legacy/template labels are mapped to configured areas when possible, and the
  `Unassigned` tab is suppressed when configured waiting areas exist.
- During user review, hotfixed Waiting Room pane state restoration so the saved
  open state explicitly removes the hidden class after diary reloads/admin
  refreshes, the close button always closes rather than toggles, and the header
  button exposes an active/expanded state.
- During user review, hotfixed waiting-area admin save/archive sync so the
  Waiting Room pane refreshes its active waiting-area cache immediately, clears
  stale check-in default cache entries, and resets the selected tab if the
  selected area was archived.

## Recommended User Review

Use `orchestration/resource_admin_review.md` for the detailed checklist. Minimum
manual review:

1. Hard-refresh the diary after GitHub Pages refreshes and confirm the diary
   loads `diary.js?v=82` / `diary.css?v=82`.
2. Log in as an Admin/PracticeOwner, open the diary, and confirm the Admin
   button appears without cluttering the one-location diary.
3. Create a waiting area, then create a room using that waiting area as the
   default.
4. Edit the room and waiting area, confirming visible success feedback.
5. Archive the room and waiting area, confirming they disappear from active lists
   without breaking existing diary/roster display.
6. Log in as a GP or Receptionist and confirm admin controls are unavailable and
   backend writes are forbidden.
7. Confirm main diary appointment blocks, Waiting Room cards, appointment status
   controls, booking proposals, taskpane, and Command Centre are unchanged.

## Not Required Before Moving On

- No roster editor, diary template editor, drag/drop, resize, appointment
  geometry redesign, booking/status semantics, patient duplicate merge, taskpane,
  Command Centre, or Bernie runtime testing is required for Sprint 19.
- No migration was added for this sprint; the rooms and waiting-area tables
  already existed.
- No non-person bookable-resource schema is required yet.

## Known Follow-Up

- Waiting-area `display_order` duplicates are not currently constrained like room
  order; decide later whether that should become a DB/indexed uniqueness rule.
- General audit logging remains a future platform need before Bernie or higher
  autonomy write paths expand.
- Non-person bookable resources remain deliberately deferred; rooms are physical
  rooms, not bookable entities by themselves.
- A broader practice-admin area may eventually absorb this diary modal once
  resource, roster, template, appointment type, and practitioner schedule admin
  all exist.

## Verification

- `.venv\Scripts\python.exe -m py_compile app\schemas\diary.py app\routers\diary.py tests\test_diary_resource_admin.py` -> passed
- `.venv\Scripts\python.exe -m pytest tests\test_diary_resource_admin.py -q --tb=short -p no:randomly` -> 25 passed
- `.venv\Scripts\python.exe -m pytest tests\test_location_scoped_diary.py tests\test_diary_roster.py tests\test_diary_template.py tests\test_waiting_area_contract.py -q --tb=short -p no:randomly` -> 46 passed
- `node --check docs\diary\diary.js` -> passed after v82 waiting-area pane sync hotfix
- `git diff --check` -> passed, with CRLF/LF warnings only
- Chrome deployed smoke check: `diary.js?v=75` archive bug reproduced, hotfixed,
  and v75 smoke archive passed; v77 role-affordance code is pushed but GitHub
  Pages was serving v77 at the last automated deployment poll after the v78 push.
- Chrome local smoke check against `http://127.0.0.1:8765/diary/diary.html?smoke=true`
  after v79: Admin modal opened; Waiting Areas add form showed top and bottom
  Save/Cancel controls; new waiting area appeared immediately with order 3 and a
  highlight; edit/cancel returned to the list; first archive click showed the
  inline fallback warning; second click archived successfully.
- Chrome local smoke check after v80: Waiting Room panel loaded `diary.js?v=80`
  and rendered waiting-area tabs as `All`, `Main Waiting Room`,
  `Sub-waiting Room B` with no `Unassigned` tab while configured waiting areas
  existed.
- Chrome local smoke check after v81: Waiting Room pane opened from the header
  button, restored open after reload with `aria-expanded="true"` and active
  button styling, and the close button hid the pane with `aria-expanded="false"`.
- Chrome local smoke check after v82: creating `Pane Sync Smoke` in Resource
  Administration added it to the open Waiting Room pane tabs immediately; the
  first archive click showed the inline confirm fallback; the second archive
  removed it from the admin list and the Waiting Room pane tabs without reload.
- Chrome deployed smoke check after v82: creating `Deployed Pane Sync Smoke`
  added it to the open Waiting Room pane tabs immediately; archiving it removed
  it from both the admin list and pane tabs without reload; GitHub Pages served
  `diary.js?v=82` / `diary.css?v=82`.

## Recommended Next Direction

After Sprint 19 user review, the strongest next candidates are:

1. Roster admin writes for date-specific room/practitioner assignments.
2. Appointment type/schedule admin foundations.
3. A small operation-result pattern for diary/admin surfaces so success/failure
   feedback stays visible and consistent.
4. Duplicate merge workflow design/implementation, if patient-admin safety should
   take priority over diary admin depth.

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

---

## Sprint 17 Review Harness - Command/Proposal Workflow Retrofit

Use `orchestration/command_proposal_review.md` after the Sprint 17 backend and
diary UI worker branches are reviewed and integrated. This closeout pointer is
intentionally brief; the harness file owns the command/proposal vocabulary,
integration checklist, expected response classes, and PowerShell snippets.

Codex/orchestrator should specifically report whether:

- Proposal endpoints are non-mutating and return typed commands for staff
  confirmation.
- Safe create proposals still require staff confirmation before the diary is
  written.
- Conflict proposals return `safe=false`, `autonomy_tier=blocked`, and a stable
  `appointment_conflict` block without creating an appointment.
- Break overlaps and provisional patients return warnings, not blocks, and stay
  confirmable by staff.
- The diary UI treats blocked proposals as hard stops and warning proposals as
  explicit confirmation paths.
- Booking slots, diary grid cells, Waiting Room cards, appointment status, and
  patient identity are described as separate surfaces.
- No Sprint 17 work starts a Bernie runtime, bypasses normal appointment route
  validation, or creates a privileged agent-only write path.

### Sprint 17 Integrated Outcome

Integrated submissions:

- Claude: existing-appointment update/status proposal contracts.
- Antigravity: diary new-booking modal create-proposal preflight.
- Codex/Banach: command proposal review harness and API snippets.

Verification run after integration:

```powershell
.venv\Scripts\python.exe -m py_compile app\routers\appointments.py app\schemas\appointments.py tests\test_appointment_update_proposal.py tests\test_appointment_proposals.py
node --check docs\diary\diary.js
.venv\Scripts\python.exe -m pytest tests\test_appointment_update_proposal.py tests\test_appointment_proposals.py tests\test_appointment_status_mutations.py tests\test_booking_create_edit.py tests\test_break_overlap_contract.py -q --tb=short -p no:randomly
git diff --check
```

Result: `75 passed`; JS syntax and whitespace checks clean.

Manual user review:

- Confirm diary assets load at `diary.js?v=72`.
- Create a normal non-conflicting booking and confirm it saves.
- Try an overlapping booking and confirm the modal blocks the save before writing.
- Create a booking that crosses a break and confirm the warning appears, then `Confirm & Save` writes it.
- Create a provisional-patient booking and confirm the warning appears, then `Confirm & Save` writes it.
- Confirm the proposal warning/error copy is readable in the booking modal and does not disturb the main diary grid or Waiting Room panel.

User review result: positive after hotfix `d081834`; break-crossing warning now appears for the visible break path.
