# EMR4 Sprint Closeout

This file tracks what the user should review after each integrated sprint batch
of parallel-agent work. Codex updates it after submitted work has been polled,
reviewed, integrated, verified, pushed, and audited.

## Current Closeout

| Item | Value |
|---|---|
| Batch | Sprint 15: Waiting Room Check-In Operations |
| Integrated through | `847eb01` plus integration-log bookkeeping |
| Status | Integrated locally, verification passed, pending push/audit |
| Last updated | 2026-06-22 |

## What Changed

- Added read-only `GET /api/v1/appointments/{id}/checkin-defaults` so the diary
  or Bernie can ask the backend for the room/default waiting-area suggestion for
  a booked appointment without mutating state.
- Made terminal attendance statuses deliberately clear `waiting_area_id` when
  the PATCH body omits `waiting_area_id`. Explicit UUID and explicit `null`
  values still win over the automatic policy.
- Added focused backend regression tests for default suggestion, inactive/cross-
  practice waiting-area guards, terminal auto-clear, active-status preservation,
  and explicit waiting-area override.
- Improved the diary Waiting Room side panel only: Expected Today cards are
  denser, check-in can send a selected waiting area, arrived patients can be
  reassigned between waiting areas, and the tab strip is hidden when only one
  waiting area is available.
- Kept the main diary grid appointment positioning unchanged. The prior
  accidental appointment-card stacking/cascade behaviour was not reintroduced.
- Added a Sprint 15 review harness with manual checks, API spot checks, and a
  guardrail that future "stacking" requests must say whether they mean Waiting
  Room cards or diary appointment blocks.
- Updated diary assets to `v=66`.

## Recommended User Review

1. Restart the backend and hard refresh the diary.
2. Confirm the live diary loads `diary.js?v=66`.
3. Use the detailed "Sprint 15 Review Harness - Waiting Room Check-In
   Operations" section below.
4. Pay particular attention to waiting-area defaulting/reassignment, terminal
   status clearing/filtering, and the difference between Waiting Room card
   density and main diary grid appointment geometry.

User review result: pending.

## Not Required Before Moving On

- No drag/drop/resize appointment testing is required yet.
- No taskpane Patient Details duplicate testing is required for Sprint 14; that
  was Sprint 13.
- No Command Centre, Scribe, Gemini, billing, results, letters, medications, or
  clinical-note regression is required for this sprint.
- No patient document rewrite, public online-booking, kiosk, SMS/reminder, or
  Bernie runtime testing is required.

## Known Follow-Up

- Patient Details is still a foundation slice. Add stronger validation, Medicare
  IRN polish, IHI/Medicare verification hooks, duplicate-candidate review, and a
  proper shared demographic model before relying on it in routine use.
- GitHub Pages deployment should be kept to canonical `master`.
- Physical waiting areas now exist in the backend, but room/resource admin and
  per-room default waiting-area editing are still future work. The Sprint 14
  design reference is `orchestration/resource_admin_bernie_tool_design.md`.
- Terminal appointment statuses now auto-clear `waiting_area_id` when omitted
  from PATCH. Continue watching whether this feels right in practice, especially
  when status changes are corrected after accidental completion/cancellation.
- The diary waiting-area UI should eventually auto-focus the area associated with
  the active room/column and support true stacked/condensed cards inside
  high-volume Waiting Room sections such as Finished.
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

## Verification

Codex/orchestrator verification for Sprint 14:

- `node --check docs\diary\diary.js` -> passed
- `.venv\Scripts\python.exe -m py_compile app\schemas\appointments.py app\routers\appointments.py tests\test_waiting_area_checkin_contract.py` -> passed
- `git diff --check` -> passed, with only CRLF/LF warnings on Markdown files
- `.venv\Scripts\python.exe -m pytest tests\test_waiting_area_checkin_contract.py -q -p no:randomly` -> 8 passed
- `.venv\Scripts\python.exe -m pytest tests\test_waiting_area_checkin_contract.py tests\test_waiting_area_contract.py tests\test_appointment_status_mutations.py tests\test_break_overlap_contract.py tests\test_appointment_patient_link.py tests\test_appointment_conflicts.py tests\test_diary_template.py tests\test_diary_roster.py tests\test_slots.py tests\test_booking_patient_flow.py tests\test_nurse_practitioner.py -q --tb=short -p no:randomly` -> 111 passed, 1 warning

## Recommended Next Direction

The next sprint should build on the clarified receptionist workflow without yet
jumping to drag/drop. Recommended slices: expose waiting-area assignment in the
diary check-in UI, add small room/waiting-area admin endpoints or admin UI
foundation, and begin a tool-schema-only Bernie proof path after audit/write
confirmation rules are explicit.

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

1. Restart the backend and hard refresh the deployed/local diary surface after
   integration. Confirm the expected diary asset version if the UI branch
   changed `docs/diary/diary.html`.
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
