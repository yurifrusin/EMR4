# Appointment State And Waiting-Area Review

Use this note for Sprint 12 integration and user review before EMR4 starts
drag/drop or resize work. The goal is to keep three concepts separate:
patient-record identity, appointment attendance workflow, and future patient
communication confirmation.

## State Model

| Concept | Current / Near-Term Field | Meaning | Must Not Mean |
|---|---|---|---|
| Linked patient identity | `patient_id` plus embedded `patient` | The diary booking is attached to a real EMR patient record in the same practice. | The patient has arrived, replied to SMS, or been clinically seen. |
| Provisional identity | `patient_name_provisional` with `patient_id = null` | Reception has booked a named person before matching or creating a patient record. | A second patient record, a verified identity, or an attendance status. |
| Identity/linkage confirmed | Derived from `patient_id != null` for now; later may become an explicit audit/event | Staff have matched the diary name to the correct patient record. | "Confirmed" attendance, SMS reply, or Medicare/IHI verification. |
| Attendance workflow | `Appointment.status` | Operational movement through the day: `Booked`, `Arrived`, `InConsult`, `Completed`, `Cancelled`, `NoShow`, `DNA`. | Patient-record linkage or patient reminder response. |
| Legacy `Confirmed` status | Still accepted by enum/API for compatibility | Historical/legacy status that may appear in old data and should render safely. | A routine status option for new workflow, identity proofing, or SMS confirmation. |
| Future SMS/reminder confirmation | Future reminder/SMS model, likely `sms_log` plus reminder response metadata | Patient has replied YES/NO or otherwise responded to a reminder. | Linked patient identity or same-day attendance. |

Policy for Sprint 12 review:

- A booking must have either `patient_id` or `patient_name_provisional`.
- Linking a provisional booking to a patient should set `patient_id` while
  preserving date, time, duration, practitioner, type, reason, notes, status,
  booking channel, waiting area, and queue position unless the user explicitly
  edits them.
- Clearing both `patient_id` and `patient_name_provisional` must be rejected.
- The diary may visually distinguish linked versus provisional bookings, but
  attendance controls must not become the mechanism for linking identity.
- `Confirmed` should not be promoted as a normal attendance action. Keep it
  readable for legacy data and compatible with existing enum responses.

## Attendance And Billing Guard Notes

Reception needs correction flexibility, so the backend can continue to allow
most status backtracking for now. The risky boundary is not `Arrived` or
`InConsult`; it is `Completed` once billing and encounter finalisation are tied
to the appointment.

Near-term guard expectation:

- `Booked`, `Arrived`, and `InConsult` are active operational states.
- `Completed`, `Cancelled`, `NoShow`, and `DNA` are not waiting-room states.
- `Cancelled`, `NoShow`, and `DNA` should remain non-blocking for slot reuse.
- Codex should record whether `Completed` blocks slot reuse after each backend
  integration until billing semantics are deliberately designed.
- Future billing should protect against accidental double-billing if staff move
  `Completed` back and forth. Prefer an audit trail or billing guard over a hard
  status lock that prevents legitimate correction.

## Waiting-Area Model

The current appointment field `waiting_room` is a string and is good enough for
Sprint 12 review, but the product model should evolve toward physical waiting
areas:

- `PracticeLocation.waiting_rooms` already appears in the implementation plan as
  a JSONB holder for physical site waiting areas.
- Room/resource/roster entries should later point to a default waiting area, so
  a room such as "Room 2 / Nurse" can naturally feed "Nurse waiting area" while
  GP rooms feed the main waiting area.
- Appointment-level `waiting_room` should represent the selected physical area
  or override, not an attendance status.
- The waiting-room/patient-flow panel should eventually support tabs or filters
  by physical area, plus an all-areas view. It should also tolerate high-volume
  stacked/condensed cards.
- Kiosk/tablet check-in can assign or confirm the waiting area later, but Sprint
  12 should not implement kiosk behaviour.

## Sprint 12 Integration Review

Backend review after Claude submit:

1. Confirm provisional bookings can be created with `patient_name_provisional`
   and no `patient_id`.
2. Confirm linked bookings can be created with `patient_id`.
3. Confirm update/linking a provisional appointment to an existing patient keeps
   unrelated appointment fields stable.
4. Confirm an update cannot leave both `patient_id` and
   `patient_name_provisional` empty.
5. Confirm cross-practice patient IDs cannot be linked.
6. Confirm status mutation remains separate from patient linking.
7. Confirm waiting-room inclusion/exclusion still follows attendance status, not
   linked/provisional identity.
8. Confirm any break-overlap behaviour is warning-compatible, not a hard blocker,
   unless the user explicitly changes that policy.

Diary UI review after Antigravity submit:

1. Create or open a provisional booking and confirm it is visually legible as
   provisional/free-text.
2. Link that booking to an existing patient and confirm the diary card changes
   identity display without changing status, time, duration, or notes.
3. Confirm the status dropdown/actions do not offer `Confirmed` as the normal
   way to link or verify patient identity.
4. Confirm any break-crossing warning appears before save and does not pretend a
   soft break is an impossible booking target.
5. Confirm narrow layout still leaves patient name, provisional marker, status,
   notes, break labels, date controls, Refresh, and Now readable.

## PowerShell API Review

These snippets assume the local dev stack is running and seeded:

```powershell
.\run_dev.ps1
alembic upgrade head
python seed.py
```

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

$ExistingLinked = $SeededAppointments | Where-Object { $_.patient_id } | Select-Object -First 1
if (-not $ExistingLinked) {
  throw "No linked seeded appointment found. Create a patient or reseed, then retry."
}

$PatientId = $ExistingLinked.patient_id

$ReviewDateValue = (Get-Date).Date.AddDays(8)
while ($ReviewDateValue.DayOfWeek -in @([DayOfWeek]::Saturday, [DayOfWeek]::Sunday)) {
  $ReviewDateValue = $ReviewDateValue.AddDays(1)
}
$ReviewDate = $ReviewDateValue.ToString("yyyy-MM-dd")
$NextDate = $ReviewDateValue.AddDays(1).ToString("yyyy-MM-dd")

"Patient: $PatientId"
"Practitioner: $PractitionerId"
"Appointment type: $AppointmentTypeId"
"Review date: $ReviewDate"
```

### 2. Create A Provisional Booking

```powershell
$ProvisionalBody = @{
  patient_name_provisional = "Sprint Twelve Provisional"
  practitioner_id = $PractitionerId
  appointment_type_id = $AppointmentTypeId
  appointment_date = $ReviewDate
  start_time_local = "13:10:00"
  duration_minutes = 20
  reason = "Sprint 12 provisional identity review"
  notes = "Should link without changing attendance state"
  booked_via = "Receptionist"
} | ConvertTo-Json

$Provisional = Invoke-RestMethod `
  -Method Post `
  -Uri "$Base/appointments" `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body $ProvisionalBody

$Provisional | Select-Object id, patient_id, patient_name_provisional, status, appointment_date, start_time_local, duration_minutes, reason
```

Expected: HTTP `201`; `patient_id` is empty/null, `patient_name_provisional`
is returned, and `status` remains the normal attendance default.

### 3. Link The Provisional Booking To A Patient

```powershell
$LinkBody = @{
  patient_id = $PatientId
  patient_name_provisional = $null
} | ConvertTo-Json

$Linked = Invoke-RestMethod `
  -Method Put `
  -Uri "$Base/appointments/$($Provisional.id)" `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body $LinkBody

$Linked | Select-Object id, patient_id, patient_name_provisional, status, appointment_date, start_time_local, duration_minutes, reason, notes, waiting_room, queue_position
```

Expected: HTTP `200`; `patient_id` is populated; provisional name is empty/null;
status, date, time, duration, reason, notes, waiting area, and queue position are
unchanged unless the final Sprint 12 contract deliberately preserves the old
name for audit/display.

### 4. Prove Linking Is Not Attendance

```powershell
$Arrived = Invoke-RestMethod `
  -Method Patch `
  -Uri "$Base/appointments/$($Linked.id)/status" `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body (@{ status = "Arrived" } | ConvertTo-Json)

$Arrived | Select-Object id, patient_id, patient_name_provisional, status
```

Expected: status changes to `Arrived`; patient linkage fields remain unchanged.

### 5. Waiting-Room Inclusion Uses Attendance State

```powershell
$TodayCandidate = $SeededAppointments |
  Where-Object { $_.appointment_date -eq $Today -and $_.patient_id } |
  Select-Object -First 1

if (-not $TodayCandidate) {
  throw "No linked same-day seeded appointment found. Seed or create one for waiting-room review."
}

$TodayArrived = Invoke-RestMethod `
  -Method Patch `
  -Uri "$Base/appointments/$($TodayCandidate.id)/status" `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body (@{ status = "Arrived" } | ConvertTo-Json)

$WaitingRoom = @(Invoke-RestMethod `
  -Method Get `
  -Uri "$Base/appointments/waiting-room" `
  -Headers $Headers)

$WaitingRoom |
  Where-Object id -eq $TodayCandidate.id |
  Select-Object id, patient_id, patient_name_provisional, status, waiting_room, queue_position

$TodayCompleted = Invoke-RestMethod `
  -Method Patch `
  -Uri "$Base/appointments/$($TodayCandidate.id)/status" `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body (@{ status = "Completed" } | ConvertTo-Json)

$AfterCompleted = @(Invoke-RestMethod `
  -Method Get `
  -Uri "$Base/appointments/waiting-room" `
  -Headers $Headers)

$AfterCompleted |
  Where-Object id -eq $TodayCandidate.id |
  Select-Object id, patient_id, patient_name_provisional, status, waiting_room, queue_position
```

Expected: the appointment appears after `Arrived` and returns no row after
`Completed`. Patient linkage fields are not what decide waiting-room inclusion.

### 6. Clearing All Identity Is Rejected

```powershell
$BadIdentityBody = @{
  patient_id = $null
  patient_name_provisional = $null
} | ConvertTo-Json

try {
  Invoke-RestMethod `
    -Method Put `
    -Uri "$Base/appointments/$($Linked.id)" `
    -Headers $Headers `
    -ContentType "application/json" `
    -Body $BadIdentityBody
  throw "Expected identity validation failure, but update succeeded."
} catch {
  [int]$_.Exception.Response.StatusCode
  $_.ErrorDetails.Message
}
```

Expected: validation failure, ideally `400` or `422`, and the appointment still
has either a linked patient or provisional name after refetch.

### 7. Future SMS Confirmation Remains Out Of Scope

```powershell
$Refetched = Invoke-RestMethod `
  -Method Get `
  -Uri "$Base/appointments?date_from=$($ReviewDate)T00:00:00&date_to=$($NextDate)T00:00:00" `
  -Headers $Headers

$Refetched |
  Where-Object id -eq $Linked.id |
  Select-Object id, patient_id, patient_name_provisional, status, booked_via
```

Expected: there is no requirement for an SMS confirmation flag in the appointment
payload. If one appears in a submitted implementation, Codex should verify it is
not being used as patient identity linkage or same-day attendance.

## Not Required Yet

- Drag/drop, resize handles, recurring appointments, or roster admin.
- Billing implementation, Medicare claiming, or invoice generation.
- Real ADHA/IHI verification.
- ClickSend webhook handling, two-way SMS confirmation, kiosk check-in, or
  patient mobile/PWA booking flows.
- Taskpane or Command Centre clinical workflows.

## Merge Gate

Proceed to drag/drop/resize only when Sprint 12 integration proves that
provisional-to-linked identity works through API and diary UI, attendance state
remains separate, waiting-room inclusion still follows attendance, and physical
waiting-area follow-up is recorded without blocking the current sprint.
