# EMR4 Sprint Closeout

This file tracks what the user should review after each integrated sprint batch
of parallel-agent work. Codex updates it after submitted work has been polled,
reviewed, integrated, verified, pushed, and audited.

## Current Closeout

| Item | Value |
|---|---|
| Batch | Sprint 20: Security Baseline |
| Integrated through | Sprint 20 security baseline integration |
| Status | Integrated locally with verification passing; ready for push/deploy audit |
| Last updated | 2026-06-24 |

## What Changed

- Added `.github/workflows/python-security.yml` for `pip-audit` and Bandit.
- Added `.github/workflows/node-security.yml` for Office manifest validation,
  blocking production `npm audit --omit=dev`, and non-blocking full npm audit
  visibility for build-tool/devDependency risks.
- Added `.github/workflows/codeql.yml` for GitHub CodeQL analysis across Python
  and JavaScript/TypeScript plus `.github/dependabot.yml` for GitHub Actions,
  pip, and npm update tracking.
- Added `pyproject.toml` with Bandit configuration only; no runtime Python
  package configuration was introduced there.
- Added `orchestration/security_baseline_review.md`, the Ariadne-facing review
  harness for collecting local audit output, GitHub security signals, and future
  Codex Security scan results.
- During integration, Ariadne applied the small security dependency bumps surfaced
  by Claude's `pip-audit`: `cryptography==48.0.1` and
  `pydantic-settings==2.14.2`, clearing the blocking Python CVE gate.

## Recommended User Review

No clinical UI smoke test is required for Sprint 20 because no app, diary,
taskpane, Command Centre, migration, or patient-flow runtime code changed. The
manual review is GitHub/security-signal oriented:

1. After the push, open GitHub Actions and confirm `Python Security`,
   `Node & Office Add-in Security Baseline`, `CodeQL`, and `Deploy GitHub Pages`
   appear as expected.
2. Confirm `Python Security` passes on `master`; it should now report no known
   vulnerabilities after the dependency bumps.
3. Confirm `Node & Office Add-in Security Baseline` passes even though the full
   npm audit step logs the known devDependency/build-tool vulnerabilities.
4. Confirm GitHub's Security tab shows CodeQL/Dependabot signals beginning to
   populate after their first scheduled/manual runs.
5. Optional but recommended: start a Codex Security diff scan against the Sprint
   20 integration diff and record any validated findings before the next runtime
   feature sprint.

## Not Required Before Moving On

- No diary, waiting-room, resource-admin, taskpane, Command Centre, Word add-in,
  booking/status, patient-admin, migration, seed-data, or GitHub Pages visual
  deployment testing is required for Sprint 20.
- No forced npm devDependency upgrade is required yet; the full npm audit is
  deliberately non-blocking until those build-tool updates can be tested as their
  own slice.

## Known Follow-Up

- `npm audit` still reports 16 devDependency/build-tool vulnerabilities
  (13 moderate, 3 high). Production dependency audit is clean; the remaining
  build-tool supply-chain work should be planned separately if it starts to
  affect CI runner or developer-machine risk tolerance.
- Bandit's full low-severity output includes a silent `try/except/pass` in
  `app/routers/consultation.py`; consider replacing it with bounded logging in a
  later backend hygiene sprint.
- CodeQL build/language settings may need tuning after the first GitHub Actions
  run; keep the workflow minimal unless GitHub reports a concrete setup problem.
- Dependabot labels may need to be created in GitHub if PR labels are desired;
  missing labels should not block dependency update PRs.
- Future auth, RBAC, clinical-data route, or AI-tooling changes should use the
  Codex Security plugin and/or Claude `/security-review` as an on-demand deep
  review complement to the always-on CI gates.

## Verification

- `.venv\Scripts\pip-audit.exe -r requirements.txt --desc` -> passed after
  bumping `cryptography` and `pydantic-settings`; no known vulnerabilities.
- `.venv\Scripts\bandit.exe -r app/ scripts/ -ll -ii -c pyproject.toml` ->
  passed; no medium+ severity/confidence issues.
- `npm run validate` in `EMR4 Sidebar` -> passed; manifest valid.
- `npm audit --omit=dev` in `EMR4 Sidebar` -> passed; 0 production
  vulnerabilities.
- `npm audit` in `EMR4 Sidebar` -> non-blocking visibility check reported the
  known 16 devDependency/build-tool vulnerabilities.
- Python/PyYAML parsed `.github/workflows/python-security.yml`,
  `.github/workflows/node-security.yml`, `.github/workflows/codeql.yml`, and
  `.github/dependabot.yml` successfully.
- `git diff --check` -> passed, with existing line-ending warnings only.
- Codex Security app-mediated scan was not run during the automated heartbeat
  integration because it requires an interactive workspace start; the review path
  is documented in `orchestration/security_baseline_review.md`.

## Recommended Next Direction

After Sprint 20 GitHub Actions are observed, the strongest next candidates are:

1. Build-tool/devDependency remediation plan for the Node/Office toolchain.
2. Roster admin writes for date-specific room/practitioner assignments.
3. Appointment type/schedule admin foundations.
4. A small operation-result pattern for diary/admin surfaces.
5. Duplicate merge workflow design/implementation if patient-admin safety should
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
