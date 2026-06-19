# Booking Create/Edit Review Checklist

Use this after Codex integrates Claude's backend booking create/edit contract and
Antigravity's diary create/edit modal. This review is intentionally limited to
manual booking create/edit through the existing appointments API and diary UI:
drag/drop, resize, recurring appointments, roster admin, taskpane, Command
Centre, Gemini, SMS, kiosk, and online booking remain out of scope.

## Preconditions

- Claude submit is integrated or explicitly superseded, with focused
  appointment create/edit/conflict/auth/scope tests passing.
- Antigravity submit is integrated or explicitly superseded, with
  `node --check docs\diary\diary.js` passing and live/smoke/narrow diary checks
  recorded.
- Codex has inspected that backend changes stayed in appointment
  router/schema/tests and diary changes stayed in `docs/diary/`.
- Local review stack is running with seeded dev data:

```powershell
.\run_dev.ps1
alembic upgrade head
python seed.py
```

## Required Integration Review

1. Confirm `POST /api/v1/appointments` still accepts the canonical local pair
   `appointment_date` plus `start_time_local`, and returns `start_time`,
   `appointment_date`, `start_time_local`, `end_time`, `duration_minutes`,
   patient, practitioner, and appointment type data.
2. Confirm `PUT /api/v1/appointments/{id}` can edit date/time/duration/reason
   without changing patient, practice, booked-by user, booking channel, or
   unrelated appointment fields.
3. Confirm conflicts are explicit `409` responses and include enough detail for
   the diary UI to show a useful failure.
4. Confirm back-to-back adjacent bookings are still allowed.
5. Confirm Cancelled, NoShow, and DNA appointments do not block a new booking.
6. Confirm unauthenticated requests return `401`, disallowed roles cannot mutate,
   and cross-practice patient/practitioner/type IDs cannot be used.
7. Confirm the diary create/edit modal does not silently update the grid before
   the API succeeds.
8. Confirm failed create/edit responses keep the previous appointment visible and
   show a readable error/retry path.
9. Confirm status controls from Sprint 7 still work after create/edit lands.
10. Confirm diary asset cache-bust is bumped if `docs/diary/` changed.

## Required User Review

1. Open the live diary from the taskpane and create a booking in a visible room
   column using the modal.
2. Verify the new appointment appears in the correct date, room/practitioner
   column, time position, duration height, status styling, and appointment-type
   accent.
3. Edit the same appointment's time, duration, reason, and notes; verify the
   card updates only after a successful save.
4. Attempt a booking that overlaps an existing active appointment; verify the UI
   keeps the old grid state and presents the conflict clearly.
5. Narrow the diary window and confirm create/edit controls do not crowd patient
   names, notes, status controls, break labels, date controls, Refresh, or Now.
6. Navigate away and back to the review date, then refresh; verify the created
   and edited booking is still represented from the backend.

## Optional User Review

- Try creating a booking with no appointment type if the modal allows it.
- Try editing only reason/notes without changing time or duration.
- Try creating a booking on a different date and verify date navigation fetches
  it without a stale modal state.
- Try smoke mode for visual affordances, but do not treat smoke mode as proof of
  authenticated backend create/edit behavior.

## PowerShell API Review

These snippets are designed for the seeded local dev stack. They create a scratch
patient, use a seeded appointment to discover a valid practitioner, then run
create, edit, list, conflict, slots, and cleanup checks.

### 1. Login And Discover IDs

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
    first_name = "Booking"
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
$NextDate = $ReviewDateValue.AddDays(1).ToString("yyyy-MM-dd")

"Patient: $($Patient.id)"
"Practitioner: $PractitionerId"
"Appointment type: $AppointmentTypeId"
"Review date: $ReviewDate"
```

### 2. Create A Booking

```powershell
$CreateBody = @{
  patient_id = $Patient.id
  practitioner_id = $PractitionerId
  appointment_type_id = $AppointmentTypeId
  appointment_date = $ReviewDate
  start_time_local = "14:10:00"
  duration_minutes = 20
  reason = "Sprint 8 create review"
  notes = "Created from PowerShell review checklist"
  booked_via = "Receptionist"
} | ConvertTo-Json

$Created = Invoke-RestMethod `
  -Method Post `
  -Uri "$Base/appointments" `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body $CreateBody

$Created | Select-Object id, appointment_date, start_time_local, duration_minutes, status, reason
```

Expected: HTTP `201`, returned `status` is `Booked` unless the integrated sprint
intentionally changes the default, and `end_time` reflects the duration.

### 3. Edit The Booking

```powershell
$EditBody = @{
  appointment_date = $ReviewDate
  start_time_local = "14:35:00"
  duration_minutes = 25
  reason = "Sprint 8 edit review"
  notes = "Edited from PowerShell review checklist"
} | ConvertTo-Json

$Edited = Invoke-RestMethod `
  -Method Put `
  -Uri "$Base/appointments/$($Created.id)" `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body $EditBody

$Edited | Select-Object id, appointment_date, start_time_local, duration_minutes, status, reason, notes
```

Expected: HTTP `200`; patient, practitioner, practice, status, and booked channel
remain stable unless explicitly edited by the sprint contract.

### 4. List And Confirm The Edited Booking

```powershell
$Listed = @(Invoke-RestMethod `
  -Method Get `
  -Uri "$Base/appointments?date_from=$($ReviewDate)T00:00:00&date_to=$($NextDate)T00:00:00" `
  -Headers $Headers)

$Listed |
  Where-Object id -eq $Created.id |
  Select-Object id, appointment_date, start_time_local, duration_minutes, status, reason
```

Expected: the edited appointment is returned once, ordered with other bookings
by local appointment date and time.

### 5. Conflict Check

```powershell
$ConflictBody = @{
  patient_id = $Patient.id
  practitioner_id = $PractitionerId
  appointment_type_id = $AppointmentTypeId
  appointment_date = $ReviewDate
  start_time_local = "14:45:00"
  duration_minutes = 15
  reason = "Sprint 8 expected conflict"
  booked_via = "Receptionist"
} | ConvertTo-Json

try {
  Invoke-RestMethod `
    -Method Post `
    -Uri "$Base/appointments" `
    -Headers $Headers `
    -ContentType "application/json" `
    -Body $ConflictBody
  throw "Expected conflict, but appointment was created."
} catch {
  [int]$_.Exception.Response.StatusCode
  $_.ErrorDetails.Message
}
```

Expected: status code `409`; response body identifies a conflict and, ideally,
the conflicting appointment ID/start/end.

### 6. Slot Availability Check

```powershell
$Slots = @(Invoke-RestMethod `
  -Method Get `
  -Uri "$Base/appointments/slots/$PractitionerId?date=$($ReviewDate)T00:00:00" `
  -Headers $Headers)

$Slots |
  Where-Object { $_.start_time -match "14:30|14:45|15:00" } |
  Select-Object start_time, end_time, available
```

Expected: slots overlapping the edited booking are unavailable; adjacent
non-overlapping slots remain available when they fit the schedule.

### 7. Cleanup / Non-Blocking Status Check

```powershell
$Cancelled = Invoke-RestMethod `
  -Method Patch `
  -Uri "$Base/appointments/$($Created.id)/status" `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body (@{ status = "Cancelled" } | ConvertTo-Json)

$RetryAfterCancel = Invoke-RestMethod `
  -Method Post `
  -Uri "$Base/appointments" `
  -Headers $Headers `
  -ContentType "application/json" `
  -Body $ConflictBody

$RetryAfterCancel | Select-Object id, appointment_date, start_time_local, duration_minutes, status, reason
```

Expected: after cancellation, the same overlapping booking can be created
because Cancelled is non-blocking. Cancel or delete the retry appointment after
manual review if you want the dev diary tidy.

## Explicitly Out Of Scope

- Drag/drop, resize, delete UI, and recurring appointments.
- Roster admin UI or room assignment management.
- Waiting-room display app, kiosk check-in, SMS reminder behavior, and online
  booking portal behavior.
- Clinical note, taskpane consultation workflow, Command Centre, or Gemini review.
- Any final decision on public patient-facing booking semantics.

## Merge Gate

Proceed past Sprint 8 only if create/edit succeeds through both API and diary UI,
conflict/session failures are honest and recoverable, status controls remain
intact, and any unresolved exceptions are recorded in
`orchestration/sprint_closeout.md`.
