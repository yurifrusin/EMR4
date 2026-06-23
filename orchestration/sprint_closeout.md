# EMR4 Sprint Closeout

This file tracks what the user should review after each integrated sprint batch
of parallel-agent work. Codex updates it after submitted work has been polled,
reviewed, integrated, verified, pushed, and audited.

## Current Closeout

| Item | Value |
|---|---|
| Batch | Sprint 18: Patient Admin Safety and Duplicate Visibility |
| Integrated through | Sprint 18 integration batch |
| Status | Integrated and verified locally; push/realign pending |
| Last updated | 2026-06-23 |

## What Changed

- Added a read-only `GET /api/v1/patients/duplicate-groups` endpoint for
  practice-scoped duplicate review. It groups likely duplicates by strong IHI,
  strong Medicare+IRN, and softer same-name-plus-DOB matches, and includes
  appointment/encounter reference counts for safe review.
- Added `scripts/audit_patient_duplicates.py`, a read-only developer helper for
  inspecting likely duplicate patient records before any manual cleanup. It
  prints evidence and reference counts only; it never deletes, merges, or
  updates records.
- Improved taskpane patient search so full-name searches such as
  `alice alston` search broadly and then filter locally instead of failing when
  the backend only matches one term.
- Moved New Patient and Patient Details error/status messages close to the
  action buttons and added visible action-status feedback so failed saves are
  harder to miss in the narrow Word taskpane.
- Updated taskpane assets to `v=54`.

## Recommended User Review

After this is pushed/deployed:

1. Hard refresh the Word taskpane and confirm it loads `taskpane.js?v=54`.
2. Search patients by a full name, for example `alice alston`. Confirm the
   expected patient appears, not "No results found".
3. Try a normal Patient Details edit and confirm the success/failure message is
   visible near the action buttons, not only at the top of the scroll area.
4. Try to save a duplicate Medicare+IRN combination. Confirm the save is blocked
   and the feedback is visible near `Save Details`.
5. Try a New Patient validation failure and confirm the bottom action area
   shows a clear failure state without needing to scroll back to the top.
6. Optional API check: call `GET /api/v1/patients/duplicate-groups` with a staff
   JWT and confirm duplicate groups include match reasons and reference counts.
7. Optional dev-data check: run
   `.venv\Scripts\python.exe scripts\audit_patient_duplicates.py` and confirm it
   reports likely duplicates without changing data.

## Not Required Before Moving On

- No diary, Waiting Room, booking modal, appointment proposal, or location
  selector testing is required for Sprint 18.
- No Command Centre, Scribe, Gemini, billing, results, letters, medications, or
  clinical-note regression is required for this sprint.
- No manual duplicate cleanup is required before moving on. The audit helper is
  read-only and exists to make cleanup safer later.

## Known Follow-Up

- Patient Details duplicate handling is safer, but still not a full patient
  merge workflow. We still need a deliberate review/merge/archive design before
  deleting or consolidating real records.
- The read-only duplicate endpoint uses in-Python bucketing for now. That is fine
  for dev and small practices, but large production datasets will need indexed
  query paths or a stored duplicate-review table.
- Same-phone-plus-DOB is intentionally not a duplicate key yet. It may become a
  separate soft review signal later.
- The taskpane still needs broader "operation result" design so all important
  success/failure messages remain visible in narrow Word layouts.
- Demographic edits should eventually update the patient document header, add
  IRN/IHI where appropriate, and use the future SharePoint/document URL model.
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

Codex/orchestrator verification for Sprint 18:

- `.venv\Scripts\python.exe -m py_compile app\schemas\patients.py app\routers\patients.py tests\test_patient_duplicate_review.py scripts\audit_patient_duplicates.py tests\test_audit_patient_duplicates.py` -> passed
- `node --check "EMR4 Sidebar\src\taskpane\taskpane.js"` -> passed
- `node --check docs\taskpane\taskpane.js` -> passed
- `git diff --check` -> passed, with a CRLF/LF warning on
  `orchestration/integration_log.md`
- `.venv\Scripts\python.exe -m pytest tests\test_patient_duplicate_review.py tests\test_audit_patient_duplicates.py tests\test_patients.py -q --tb=short -p no:randomly` -> 38 passed, 1 pytest-asyncio warning
- `.venv\Scripts\python.exe scripts\audit_patient_duplicates.py` -> read-only run
  completed and reported the current Billy Frusin duplicate group.

## Recommended Next Direction

After Sprint 18 user review, the next sprint can return to diary/resource work
or continue patient-admin safety. Recommended options are: a proper duplicate
review/merge workflow design, a taskpane operation-result pattern for narrow
layouts, or the next diary/resource admin slice for locations, rooms, and
waiting areas.

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
