# Resource Admin And Bernie Tool Design

This note is the Sprint 14 design boundary for resource administration and the
future Bernie receptionist copilot. It is not production implementation. Use it
to keep the next backend/admin slices narrow and to stop Bernie from inheriting
ambiguous diary language.

## Goal

Before Bernie can safely suggest receptionist actions, EMR4 needs stable
resource vocabulary and typed backend contracts. Bernie should be able to find
slots, prepare bookings, link provisional patients, assign waiting areas, and
take messages, but every write remains a staff-confirmed action with audit.

## Canonical Concepts

| Concept | Meaning | Current / Near-Term Source | Must Not Mean |
|---|---|---|---|
| Practice location | A physical site of the practice. | `PracticeLocation`; future location-scoped admin. | A diary column or waiting queue. |
| Room | A physical consult/procedure room at a location. | `Room`; `DiaryRoster` maps room+date to practitioner/label. | A patient waiting area, status, or practitioner identity. |
| Bookable resource | The person or thing that can receive a booking. Near term this is a practitioner/nurse. | `practitioner_id`; `PractitionerSchedule`; future resource abstraction only if non-person resources are needed. | The room the patient sits in while waiting. |
| Diary column | The visual day column shown to reception. | `DiaryColumn` plus date-specific roster merge. | The durable resource model by itself. |
| Waiting area | A named physical place where arrived patients wait. | `WaitingArea`; `Appointment.waiting_area_id`; `Room.default_waiting_area_id`. | Attendance state, queue position, room, or diary column. |
| Booking slot | A candidate time interval for a bookable resource. | Existing `/appointments/slots/{practitioner_id}` plus future slot-search contract. | A rendered diary cell or a guarantee until booked. |
| Linked patient identity | Appointment is attached to a real EMR patient. | `Appointment.patient_id` plus embedded patient. | Arrival, SMS confirmation, or IHI/Medicare verification. |
| Provisional patient identity | Reception has a free-text name before linking/creating the patient record. | `Appointment.patient_name_provisional` with no `patient_id`. | A duplicate patient record or verified identity. |
| Attendance status | Same-day operational flow. | `Appointment.status`: `Booked`, `Arrived`, `InConsult`, `Completed`, `Cancelled`, `NoShow`, `DNA`; legacy `Confirmed` tolerated. | Linked identity or SMS/reminder confirmation. |
| SMS/reminder confirmation | A patient reply or delivery state from communication workflow. | Future reminder/SMS metadata, likely tied to `sms_log` and appointment reminders. | Attendance, identity linkage, or legacy `Confirmed`. |

Policy: when a user or tool says "confirmed", require a qualifier. It can mean
linked patient record, patient replied to reminder, or legacy appointment status.
It must not be stored by guessing.

## Admin Contract Shape

These are endpoint candidates for a future backend/admin slice. They are named to
make the resource boundaries explicit, not to require these exact route strings.

### Waiting Areas

- `GET /api/v1/diary/waiting-areas` already exists for active practice-scoped
  listing.
- Future admin writes:
  - `POST /api/v1/diary/waiting-areas`
  - `PATCH /api/v1/diary/waiting-areas/{waiting_area_id}`
  - `POST /api/v1/diary/waiting-areas/{waiting_area_id}/archive`

Rules:

- Practice-scoped and role-gated to Admin/PracticeOwner, with Receptionist write
  only if product policy later allows it.
- Names are human-facing and ordered; archiving should not erase historical
  appointment references.
- Inactive areas are hidden from normal selection but remain resolvable for old
  appointments.

### Rooms

- Future admin reads/writes:
  - `GET /api/v1/diary/rooms`
  - `POST /api/v1/diary/rooms`
  - `PATCH /api/v1/diary/rooms/{room_id}`
  - `POST /api/v1/diary/rooms/{room_id}/archive`

Rules:

- A room is physical. It may have `default_waiting_area_id`.
- Changing a room default must not rewrite existing appointment
  `waiting_area_id` values unless a separate explicit bulk operation is created.
- Room order is visual/admin order, not appointment queue position.

### Roster And Bookable Resource Assignment

- `GET /api/v1/diary/roster?date=YYYY-MM-DD` already exists for read path.
- Future admin writes:
  - `PUT /api/v1/diary/roster/{date}` for date-specific room assignments.
  - Optional template/default endpoints only after the one-day contract is stable.

Rules:

- `DiaryRoster` maps `(practice, room, date)` to a practitioner or label.
- Near term bookability still depends on `practitioner_id` and schedules.
- Label-only room assignments are visible but not bookable unless/until a real
  resource model exists.
- Do not create resource-only bookings until non-person bookability is designed
  with conflict checks and slots.

### Appointment Types And Schedules

Appointment types and practitioner schedules already exist and can be exposed
through admin later. They should stay separate:

- Appointment type controls duration/default colour/bookability.
- Practitioner schedule controls availability.
- Room roster controls where that practitioner/resource is shown for a date.
- Waiting area controls where an arrived patient waits.

## Check-In Boundary

Claude's Sprint 14 lane owns the backend mutation contract for check-in and
waiting-area assignment. This design only states the boundary that contract should
preserve:

- "Check in" may combine an attendance transition to `Arrived` with an explicit
  waiting-area assignment, if the API makes both fields visible.
- Waiting-area assignment can also be corrected without changing attendance.
- Cross-practice waiting-area IDs must be rejected.
- Provisional appointments should be handled deliberately. If reception checks in
  an unlinked patient, the UI/tool should warn that identity is still provisional
  rather than silently treating arrival as linkage.

## Bernie Tool Boundary

Bernie is a supervised internal copilot. The model may reason and propose, but
only typed tools with validated arguments touch backend state.

Recommended tool classes:

| Tool | Kind | Purpose | Write Guard |
|---|---|---|---|
| `search_patient` | Read | Find candidate patients by name, DOB, phone, Medicare/IHI hints. | No write. Return ambiguity warnings. |
| `get_patient_booking_context` | Read | Show upcoming/past appointment context for a selected patient. | No write. Practice-scoped. |
| `find_slots` | Read | Return candidate intervals using practitioner/resource, appointment type, duration, roster, breaks, and conflicts. | No write. Mark soft break overlaps. |
| `prepare_booking` | Proposal | Build a booking proposal for a linked or provisional patient. | Staff confirms before `POST /appointments`. |
| `prepare_booking_update` | Proposal | Build reschedule/type/duration/note changes. | Staff confirms before `PUT /appointments/{id}`. |
| `prepare_patient_link` | Proposal | Link a provisional appointment to a selected patient record. | Staff confirms; preserve unrelated fields. |
| `prepare_check_in` | Proposal | Move to `Arrived` and optionally assign `waiting_area_id`. | Staff confirms; warn on provisional identity. |
| `prepare_status_change` | Proposal | Move between attendance states. | Staff confirms; no SMS or identity side effects. |
| `take_message` | Proposal/Write | Draft or create an internal message. | Prefer staff confirmation; urgent/clinical content escalates. |
| `handoff_to_receptionist` | Control | Stop automation and surface ambiguity or policy conflict. | No mutation. |

Tool response shape should be consistent:

- `proposal_summary`: plain-language receptionist-facing summary.
- `typed_action`: the exact endpoint/action and validated arguments.
- `warnings`: identity ambiguity, break overlap, inactive resource, provisional
  patient, SMS consent, or policy warnings.
- `requires_confirmation`: always `true` for writes in the first Bernie release.
- `audit_context`: user, practice, appointment/patient IDs, model request ID,
  tool name, proposed arguments, confirmation timestamp once accepted.

## Safety And Audit Requirements

- Bernie must not call database sessions, ORM models, or raw SQL directly.
- Write tools require existing route/service validation and RBAC, not a parallel
  privileged path.
- Human confirmation is required for appointment, patient-link, waiting-area,
  status, message, and SMS actions.
- Every confirmed Bernie write needs audit. The project still lacks a general
  `audit_log`; until that lands, Bernie implementation should not move beyond
  proposal-only or should add a focused audited-action table as part of an
  approved security slice.
- Treat diary text, appointment notes, and patient-supplied text as untrusted
  prompt input. Model output is advisory until validated by typed schemas.
- Patient-facing Bernie variants are explicitly deferred until the internal tool
  layer, audit model, rate limiting, and identity proofing are proven.

## SMS / Reminder Boundary

SMS confirmation should be modelled as communication state, not appointment
attendance or patient identity.

Near-term rules:

- `sms_log` can record outbound/inbound delivery and reply state.
- A future reminder response may annotate an appointment with "patient replied
  yes/no", but it must not set `patient_id` or `Appointment.status`.
- "Patient replied YES" can help reception decide, but `Arrived` still means the
  patient is physically present or staff have explicitly marked arrival.
- SMS consent belongs to patient demographics/communication policy and should be
  checked before Bernie proposes SMS actions.

## First Implementation Slices

Recommended order after Sprint 14 plans are accepted:

1. Finish Claude's check-in contract so `Arrived` plus waiting-area assignment is
   explicit and test-covered.
2. Add resource-admin read/write endpoints for waiting areas and rooms, with
   focused practice-scope/RBAC/archive tests.
3. Add roster admin writes for date-specific room assignments, still using
   practitioner-backed bookability.
4. Add a tool-schema-only Bernie design harness or service layer with no LLM
   runtime, proving typed arguments and proposal responses.
5. Add audit logging before enabling any staff-confirmed Bernie write path.

## Acceptance Checklist

- A room can have a default waiting area without becoming a waiting area.
- A roster entry can make a room visually assigned without inventing a new
  practitioner or resource.
- A booking can stay provisional without being treated as an unverified patient
  record.
- Attendance can change without linking identity or changing SMS state.
- SMS/reminder reply can exist without changing attendance or identity.
- Bernie slot finding can explain practitioner, room, duration, break, and
  conflict reasoning.
- Bernie write proposals name the exact action and require human confirmation.
- Nearby surfaces remain separate: no diary grid geometry changes, no Waiting
  Room panel card changes, no taskpane or Command Centre changes.

## Open Risks

- Legacy `Confirmed` remains in the appointment enum and can keep causing naming
  confusion until a deprecation or migration path is chosen.
- The current appointment model requires `practitioner_id`; non-person resources
  need a deliberate future schema, not a shortcut through label-only rooms.
- Bernie safety depends on audit logging and RBAC maturity. Tool schemas should
  not outrun the security workstream.
- Admin writes need careful archive semantics so old appointments remain
  readable even after rooms or waiting areas change.
- SMS confirmation needs reminder metadata design before it can be included in
  Bernie actions.
