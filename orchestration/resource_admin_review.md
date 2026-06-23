# Sprint 19 Resource Admin Review

Use this note for Sprint 19 integration review and user testing. It is a review
harness for the first rooms/waiting-areas admin slice, not a broader resource
model or Bernie runtime.

## Vocabulary Guardrails

| Concept | Means | Must Not Mean |
|---|---|---|
| PracticeLocation | Physical practice site. | Diary page, waiting queue, or tenant. |
| Room | Physical consulting/procedure room at a location or practice-wide fallback. | Waiting area, practitioner identity, or appointment status. |
| WaitingArea | Physical place where arrived patients wait. | Attendance state, room, queue position, or diary column. |
| Diary grid | Visual day layout and appointment blocks. | Durable resource admin model. |
| Appointment status | Same-day operational state such as Booked/Arrived/InConsult. | Patient identity verification or booking confirmation. |
| Bernie | Future supervised copilot/tool layer. | Direct autonomous runtime for this sprint. |

## Integrated Surface

- Backend resource admin contract:
  - `GET /api/v1/diary/rooms`
  - `POST /api/v1/diary/rooms`
  - `PATCH /api/v1/diary/rooms/{room_id}`
  - `POST /api/v1/diary/waiting-areas`
  - `PATCH /api/v1/diary/waiting-areas/{area_id}`
- Diary resource admin UI:
  - Admin button in the diary header.
  - Rooms and Waiting Areas tabs in `#admin-modal`.
  - Create/edit/archive controls scoped to the active location.
  - Smoke-mode mock CRUD for local UI review.

## Integration Checks

- Admin/PracticeOwner can create, edit, and soft-archive rooms.
- Admin/PracticeOwner can create, edit, and soft-archive waiting areas.
- GP/Receptionist users cannot mutate resources; frontend hiding is only an
  affordance and backend RBAC remains authoritative.
- `default_waiting_area_id` accepts only an active same-practice waiting area
  that is compatible with the room location.
- Soft-archived resources are hidden from normal active lists but historical
  appointment/roster references remain readable.
- Duplicate room `display_order` returns a clear conflict instead of a server
  traceback.
- The admin UI uses backend `PATCH` soft-archive semantics, not destructive
  deletes.

## User Review Checklist

1. Start the dev stack, apply migrations if needed, run `python seed.py`, and
   hard-refresh the diary assets.
2. Log in as an Admin/PracticeOwner and open the diary.
3. Confirm the Admin button appears without cluttering the one-location diary.
4. Open Resource Administration and create a waiting area.
5. Create a room with that waiting area as its default.
6. Edit the room name/order/default and confirm visible success feedback.
7. Archive the room and confirm it disappears from the active admin list.
8. Archive a waiting area and confirm existing appointments/roster display do
   not break.
9. Log in as a GP or Receptionist and confirm mutation controls are unavailable
   and backend writes are forbidden.
10. Check that main diary appointment geometry, Waiting Room cards, taskpane,
    Command Centre, appointment status controls, and booking proposal flows are
    unchanged.

## API Spot Checks

These snippets are review aids. Replace IDs and token values with the local dev
values from the current run.

```powershell
$base = "http://localhost:8001/api/v1"
$headers = @{ Authorization = "Bearer <ADMIN_JWT>" }

$newArea = Invoke-RestMethod -Method Post `
  -Uri "$base/diary/waiting-areas" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body (@{ name = "Quiet Waiting"; display_order = 9 } | ConvertTo-Json)

$newRoom = Invoke-RestMethod -Method Post `
  -Uri "$base/diary/rooms" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body (@{
    name = "Review Room"
    display_order = 9
    default_waiting_area_id = $newArea.id
  } | ConvertTo-Json)

Invoke-RestMethod -Method Patch `
  -Uri "$base/diary/rooms/$($newRoom.id)" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body (@{ is_active = $false } | ConvertTo-Json)
```

## Not Required Yet

- Roster editor, diary template editor, drag/drop, resize, appointment geometry,
  booking create/edit/status semantics, public booking, kiosk, SMS reminders,
  taskpane/Command Centre changes, duplicate merge, or Bernie runtime.
- Non-person bookable resources. Rooms remain physical locations/columns; near
  term bookability still comes from practitioner-backed scheduling.

## Merge Gate

Sprint 19 is mergeable when backend tests pass, diary JS syntax passes,
`git diff --check` passes, submitted review packets are marked, and the closeout
states the manual resource-admin review path.
