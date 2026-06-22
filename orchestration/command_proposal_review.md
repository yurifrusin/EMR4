# Command Proposal Review Harness

Use this harness for Sprint 17 and future command/proposal work. It is a
review aid, not production implementation. The goal is to prove that risky
workflow changes can be prepared as typed, non-mutating proposals before any
staff-confirmed write happens.

## Review Boundary

- This harness reviews API/tool contracts and orchestration evidence.
- It does not review diary-grid layout, booking modal visuals, Waiting Room
  cards, taskpane behaviour, Command Centre behaviour, or Bernie runtime.
- In this document, "slot" means a candidate bookable interval from the API, not
  a rendered diary grid cell.
- "Blocked" means the proposal must not be confirmed until the block is resolved.
  It should still return a reviewable response when possible.
- "Warning" means staff can still confirm after seeing the issue.

## Canonical Response Shape

Proposal endpoints should return the same conceptual fields even when the exact
command payload differs by action:

| Field | Review Expectation |
|---|---|
| `intent` | Names the action being proposed, such as `create_appointment`. |
| `safe` | `true` only when there are no hard blocks. |
| `requires_confirmation` | `true` for booking/reschedule and other judgement-heavy writes. |
| `autonomy_tier` | `proposal` for confirmable actions, `blocked` for hard stops. |
| `summary` | Plain-language text a receptionist can compare with the request. |
| `command` | The exact typed arguments that would be sent to the write endpoint. |
| `warnings` | Soft issues with stable `code`, `severity`, and `message`. |
| `blocks` | Hard issues with stable `code`, `severity`, and `message`. |
| `result_report` | Required later for confirmed/executed commands. Not expected from a proposal-only endpoint. |
| `audit_context` | Required later for confirmed/executed commands. Until the audit table exists, keep high-risk writes proposal-only. |

The first implemented endpoint is:

```text
POST /api/v1/appointments/proposals/create
```

It accepts the appointment-create payload and returns a typed create command
without writing to the diary.

Expected create-proposal response classes:

| Path | Expected Response |
|---|---|
| Safe linked patient | `safe=true`, `autonomy_tier=proposal`, no warnings/blocks, `requires_confirmation=true`. |
| Conflict | `safe=false`, `autonomy_tier=blocked`, `blocks[].code=appointment_conflict`, `conflict` populated. |
| Break overlap | `safe=true`, `warnings[].code=break_overlap`, `breaks_overlap` populated. |
| Provisional patient | `safe=true`, `patient_identity=provisional`, `warnings[].code=provisional_patient`. |

## Integration Review Checklist

Use this when reviewing submitted backend or frontend branches that touch the
command/proposal pattern.

1. Confirm proposal endpoints do not create, update, cancel, or status-change
   appointments.
2. Confirm the proposal response contains a typed `command` with canonical
   appointment date, local start time, duration, practitioner/resource context,
   patient identity, location where applicable, and booking channel.
3. Confirm hard validation errors still use normal HTTP error semantics for bad
   auth, bad role, invalid IDs, cross-practice IDs, or malformed payloads.
4. Confirm domain conflicts that staff can understand are represented as blocks
   in a proposal response, not as partial writes.
5. Confirm warnings are specific and stable enough for the diary UI or Bernie to
   show without parsing prose.
6. Confirm `requires_confirmation` stays true for booking creation, reschedule,
   cancellation, externally consequential actions, and ambiguous identity.
7. Confirm `safe=true` does not mean auto-execute. It means "eligible for staff
   confirmation".
8. Confirm the diary UI, if touched by another workstream, calls the proposal
   endpoint before the write endpoint and does not mutate the grid while a
   proposal is blocked.
9. Confirm wording separates booking slots, diary grid cells, appointment
   status, waiting areas, and patient identity.
10. Confirm future Bernie tools use the same proposal endpoint instead of
    inventing a parallel privileged path.

## Local PowerShell Snippets

These snippets are designed to be copy-pasteable against the seeded local dev
stack. They discover IDs from existing data and create a scratch patient only
for proposal review. They do not create an appointment unless a reviewer later
chooses to call the real write endpoint with the returned command.

### 1. Login And Discover Review IDs

```powershell
$Base = "http://127.0.0.1:8001/api/v1"

$Login = Invoke-RestMethod `
  -Method Post `
  -Uri "$Base/auth/login" `
  -ContentType "application/x-www-form-urlencoded" `
  -Body @{ username = "dr.shera@emr4dev.local"; password = "Password1!" }

$Headers = @{ Authorization = "Bearer $($Login.access_token)" }

$Today = (Get-Date).ToString("yyyy-MM-dd")
$Horizon = (Get-Date).AddDays(30).ToString("yyyy-MM-dd")
$SeededAppointments = @(Invoke-RestMethod `
  -Method Get `
  -Uri "$Base/appointments?date_from=$($Today)T00:00:00&date_to=$($Horizon)T00:00:00" `
  -Headers $Headers)

if ($SeededAppointments.Count -eq 0) {
  throw "No seeded appointments found. Run python seed.py, then retry."
}

$PractitionerId = $SeededAppointments[0].practitioner_id
$AppointmentTypeId = $SeededAppointments[0].appointment_type_id

if (-not $AppointmentTypeId) {
  $Types = @(Invoke-RestMethod -Method Get -Uri "$Base/appointments/types" -Headers $Headers)
  if ($Types.Count -gt 0) { $AppointmentTypeId = $Types[0].id }
}

$Patient = Invoke-RestMethod `
  -Method Post `
  -Uri "$Base/patients" `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body (@{
    first_name = "Proposal"
    last_name = "Review"
    date_of_birth = "1980-01-01"
    sex = "Other"
    phone_mobile = "0400000000"
  } | ConvertTo-Json)

$ReviewDateValue = (Get-Date).Date.AddDays(7)
while ($ReviewDateValue.DayOfWeek -in @([DayOfWeek]::Saturday, [DayOfWeek]::Sunday)) {
  $ReviewDateValue = $ReviewDateValue.AddDays(1)
}
$ReviewDate = $ReviewDateValue.ToString("yyyy-MM-dd")

"Patient: $($Patient.id)"
"Practitioner: $PractitionerId"
"Appointment type: $AppointmentTypeId"
"Review date: $ReviewDate"
```

### 2. Safe Linked-Patient Proposal

```powershell
$SafeBody = @{
  patient_id = $Patient.id
  practitioner_id = $PractitionerId
  appointment_type_id = $AppointmentTypeId
  appointment_date = $ReviewDate
  start_time_local = "14:10:00"
  duration_minutes = 20
  reason = "Proposal safe path review"
  booked_via = "Receptionist"
} | ConvertTo-Json

$SafeProposal = Invoke-RestMethod `
  -Method Post `
  -Uri "$Base/appointments/proposals/create" `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body $SafeBody

$SafeProposal | Select-Object intent, safe, requires_confirmation, autonomy_tier, patient_identity, summary
$SafeProposal.command | Select-Object patient_id, practitioner_id, appointment_date, start_time_local, duration_minutes, booked_via
```

Expected: `safe=True`, `autonomy_tier=proposal`, `requires_confirmation=True`,
`patient_identity=linked`, no warnings, no blocks. Confirm by listing the review
date that no appointment was created merely by proposing it.

### 3. Blocked Conflict Proposal

Use an existing active appointment to choose a known conflict. This keeps the
snippet independent of exact seeded times.

```powershell
$Existing = $SeededAppointments |
  Where-Object { $_.status -notin @("Cancelled", "NoShow", "DNA") } |
  Select-Object -First 1

if (-not $Existing) {
  throw "No active seeded appointment found for conflict review."
}

$ConflictBody = @{
  patient_id = $Patient.id
  practitioner_id = $Existing.practitioner_id
  appointment_type_id = $Existing.appointment_type_id
  appointment_date = $Existing.appointment_date
  start_time_local = $Existing.start_time_local
  duration_minutes = 15
  reason = "Proposal conflict path review"
  booked_via = "Receptionist"
} | ConvertTo-Json

$ConflictProposal = Invoke-RestMethod `
  -Method Post `
  -Uri "$Base/appointments/proposals/create" `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body $ConflictBody

$ConflictProposal | Select-Object intent, safe, requires_confirmation, autonomy_tier, summary
$ConflictProposal.blocks
$ConflictProposal.conflict | Select-Object appointment_id, start_time_local, duration_minutes, status, patient_name
```

Expected: HTTP `200`, `safe=False`, `autonomy_tier=blocked`,
`blocks.code` includes `appointment_conflict`, and `conflict` identifies the
blocking booking. The proposal should not create a new appointment.

### 4. Break-Warning Proposal

Break data depends on the configured diary template. Use a known break if seed
data supplies one, or treat this as a targeted manual spot-check after creating
a break in test data.

```powershell
$BreakBody = @{
  patient_id = $Patient.id
  practitioner_id = $PractitionerId
  appointment_type_id = $AppointmentTypeId
  appointment_date = $ReviewDate
  start_time_local = "10:45:00"
  duration_minutes = 15
  reason = "Proposal break warning review"
  booked_via = "Receptionist"
} | ConvertTo-Json

$BreakProposal = Invoke-RestMethod `
  -Method Post `
  -Uri "$Base/appointments/proposals/create" `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body $BreakBody

$BreakProposal | Select-Object safe, requires_confirmation, autonomy_tier, summary, breaks_overlap
$BreakProposal.warnings
```

Expected when `10:45` overlaps a configured break for that practitioner:
`safe=True`, `warnings.code` includes `break_overlap`, and `breaks_overlap`
names the break. If no warning appears, first check whether the selected
practitioner/date has a break at that time.

### 5. Provisional-Patient Warning Proposal

```powershell
$ProvisionalBody = @{
  patient_name_provisional = "Walk-in Proposal Review"
  practitioner_id = $PractitionerId
  appointment_type_id = $AppointmentTypeId
  appointment_date = $ReviewDate
  start_time_local = "15:10:00"
  duration_minutes = 15
  reason = "Proposal provisional path review"
  booked_via = "Receptionist"
} | ConvertTo-Json

$ProvisionalProposal = Invoke-RestMethod `
  -Method Post `
  -Uri "$Base/appointments/proposals/create" `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body $ProvisionalBody

$ProvisionalProposal | Select-Object safe, requires_confirmation, autonomy_tier, patient_identity, summary
$ProvisionalProposal.warnings
$ProvisionalProposal.command | Select-Object patient_id, patient_name_provisional, appointment_date, start_time_local
```

Expected: `safe=True`, `patient_identity=provisional`, warning code
`provisional_patient`, `command.patient_id` empty, and
`command.patient_name_provisional` populated.

## Schema-Level Verification

When a live local stack is not available, use the focused pytest contract as the
non-brittle verification path:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_appointment_proposals.py -q --tb=short -p no:randomly
```

That suite covers auth, safe non-mutating proposal, conflict block,
break-overlap warning, and provisional-patient warning.

## Merge Gate

Do not proceed to autonomous Bernie runtime or direct command execution until:

- Proposal endpoints are non-mutating and practice-scoped.
- Warning/block codes are stable enough for UI and tool consumers.
- Staff confirmation is explicit for judgement-heavy writes.
- The diary UI treats a blocked proposal as a hard stop.
- A future audit path is designed before confirmed/executed commands are enabled
  for high-risk workflows.
