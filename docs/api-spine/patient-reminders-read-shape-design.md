# Patient Reminders Read-Shape Design

Date: 2026-07-08

Sprint: 215

## Purpose

This design packet follows
`docs/api-spine/external-router-read-model-gap-inventory.md` for the
`Query.patient.reminders` gap.

It defines a future patient reminder summary read shape only. It does not add a
REST route, GraphQL resolver, GraphQL mutation, Pydantic schema, database
query, provider call, runtime FGA client, Access AI invocation, reminder
dismissal workflow, or write authority.

This design does not add a REST route.

## Target Read Surface

| GraphQL read surface | Current gap posture | Future REST read shape | Runtime status |
|---|---|---|---|
| `Query.patient.reminders` | `route_and_shape_gap` | `GET /api/v1/patients/{patient_id}/reminders` or equivalent patient-scoped GET read | `not_implemented` |

## Display-Safe Field Mapping

| GraphQL field | Current source | Mapping posture | Notes |
|---|---|---|---|
| `PatientReminder.id` | `app/models/results.py::Reminder.id` | `direct` | Must remain scoped to authenticated user's practice and requested patient. |
| `PatientReminder.dueAt` | `Reminder.due_date` | `date_to_datetime_gap` | Current model stores a `Date`, while SDL reserves nullable `DateTime`; future implementation must define timezone and time-of-day semantics before exposing this as `dueAt`. |
| `PatientReminder.summary` | `Reminder.message`; `Reminder.reminder_type` | `derive_truncate` | Summary must be display-safe and bounded; raw `message` text must not be projected as-is. |
| `PatientReminder.status` | `Reminder.is_dismissed` | `incomplete_enum` | Boolean can represent `OPEN` versus `DISMISSED`, but cannot represent SDL `COMPLETED` without a new reviewed model/source state. |

## Current Supporting Evidence

- `Reminder` exists in `app/models/results.py` with practice, patient,
  practitioner, result-trigger, type, message, due-date, and dismissed fields.
- The model has indexes on `practice_id` and `patient_id`, which can support a
  future scoped read.
- Current `app/routers/patients.py` exposes patient demographics and clinical
  summary reads, but no reminder list read.
- Current `app/routers/clinical.py` exposes clinical subresource reads and
  writes, but no patient reminder summary read.
- Existing reminder data is a potential backing model only. It is not a current
  API read model and not evidence that `Query.patient.reminders` is
  implemented.
  It is not evidence that `Query.patient.reminders` is implemented.

## Known Shape Gaps

- No current dedicated patient reminder GET route exists.
- No current `PatientReminderOut` or equivalent summary response schema exists.
- `Reminder.due_date` is a date-only field, while GraphQL `dueAt` is nullable
  `DateTime`.
- `Reminder.is_dismissed` cannot represent `ReminderStatus.COMPLETED`.
- `Reminder.message` is free text and must not be exposed without a bounded
  summary policy.
- raw `message`, `reminder_type`, `triggered_by_result_id`, raw `practitioner_id`, and internal result/referral context are deliberately
  outside the future reminder summary read shape unless a later reviewed SDL
  expansion adds display-safe fields.
- Reminder creation, dismissal, completion, escalation, recall policy, and
  result-triage actions are command surfaces, not part of this read-shape
  design.

## Future Route Requirements

Before any implementation sprint may add the patient reminders read:

- the route must be a patient-scoped GET read under an explicit reviewed path;
- the route must depend on the authenticated user and filter by `current_user.practice_id`;
- the route must verify the requested patient belongs to the authenticated user's practice before reading reminders;
- the response shape must include only `id`, nullable `dueAt`, bounded `summary`, and `status`;
- `dueAt` conversion must have a documented date-only to DateTime policy before runtime exposure;
- `status` mapping must fail closed or omit `COMPLETED` until a reviewed source state exists;
- ordering must be deterministic, preferably by due date then created/id;
- pagination or bounded result-size policy must be documented before production rollout;
- the route must not expose reminder message raw bodies without truncation/redaction policy;
- the route must not expose practitioner IDs, result IDs, referral IDs, patient identifiers beyond the route scope, audit internals, or command payloads;
- the route must not dismiss, complete, create, escalate, or mutate reminders;
- the route must not be used as provider, RAG, GraphRAG, Access AI, or external patient-client authority.

## Closed Gates

This design does not authorize:

- adding a REST patient reminder route;
- adding GraphQL resolvers or GraphQL mutations;
- adding Pydantic runtime schemas;
- provider calls or live provider gates;
- provider dry-run wiring;
- runtime FGA clients;
- external patient clients;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- broad historical diary trove mining;
- Access AI invocation wiring;
- reminder create/update/dismiss/complete/escalate commands;
- result-triage or recall-policy write authority;
- appointment, practitioner, message, SMS, or directory write authority;
- model-to-database writes outside REST command handlers;
- raw compatibility deprecation mode changes.

## Boundary

This is a static read-shape design packet. It does not prove runtime GraphQL
resolver implementation, REST route authorization, patient scoping,
date-to-DateTime conversion correctness, reminder status semantics, text
redaction, pagination, performance, deployment readiness, or patient-facing
client readiness. It does not prove patient-facing client readiness.

`tests/test_api_spine_patient_reminders_read_shape_design.py` validates this
packet by parsing only this markdown file, the GraphQL SDL, selected
model/router/schema source files, and the external read-model gap inventory.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_patient_reminders_read_shape_design.py -q
```
