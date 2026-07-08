# External Router Read-Model Gap Inventory

Date: 2026-07-08

Sprint: 212

## Purpose

This inventory follows `docs/api-spine/external-router-read-root-inventory.md`
by expanding the external-router rows that are still explicit read-model gaps.

It covers only these reserved GraphQL read surfaces:

- `Query.practice.practitioners`
- `Query.patient.reminders`
- `Query.patient.messages`
- `Query.directorySearch.RACGP_GUIDELINES`
- `Query.directorySearch.COCHRANE_LIBRARY`

This is static declaration continuity. It does not create GraphQL resolvers, add
REST routes, import routers at runtime, query databases, call providers, or
grant write authority.

## Gap Inventory

| GraphQL read surface | Current backing model/source | Current route source | Coverage | Required future read model | Gap posture | Notes |
|---|---|---|---|---|---|---|
| `Query.practice.practitioners` | `app/models/tenancy.py::Practitioner` | `none` | `model_only` | `GET /api/v1/practice/practitioners` or equivalent practice-scoped read route | `route_gap` | `Practice.practitioners` and `User.practitioner_id` exist, and diary template/roster reads carry practitioner IDs, but no dedicated practitioner directory route currently exposes the GraphQL `Practitioner` list shape. |
| `Query.patient.reminders` | `app/models/results.py::Reminder` | `none` | `model_only` | `GET /api/v1/patients/{patient_id}/reminders` or equivalent patient-scoped read route | `route_and_shape_gap` | `Reminder` has practice, patient, practitioner, due-date, type, message, and dismissed fields, but no read route maps it to `PatientReminder`. `due_date` is a `Date`, while SDL `dueAt` is `DateTime`; `is_dismissed` cannot represent SDL `ReminderStatus.COMPLETED`. |
| `Query.patient.messages` | `app/models/messaging.py::InternalMessage`; `app/models/messaging.py::SmsLog` | `none` | `model_only` | `GET /api/v1/patients/{patient_id}/messages` or equivalent patient-scoped read route | `route_and_shape_gap` | Internal and SMS message models exist, but no safe patient message summary route currently maps them to `PatientMessageSummary`. This likely needs a two-table union with truncated summaries; `MessageChannel.EMAIL` has no backing model, and `InternalMessage` is staff-to-staff with a patient link rather than patient-facing communication. |
| `Query.directorySearch.RACGP_GUIDELINES` | `none` | `none` | `none` | local/cited read-only RACGP directory adapter with source labels | `source_and_licensing_gap` | No RACGP guideline lookup table, route, or adapter is mapped. A future surface needs a reviewed local/cited source and citation model; practice-knowledge advisory facts do not become directory authority. |
| `Query.directorySearch.COCHRANE_LIBRARY` | `none` | `none` | `none` | local/cited read-only Cochrane directory adapter with source labels | `source_and_licensing_gap` | No Cochrane lookup table, route, or adapter is mapped. A future surface needs licensing/subscription review plus a cited local or approved external source; practice-knowledge advisory facts do not become directory authority. |

Coverage meanings:

- `model_only`: a current SQLAlchemy model can anchor a future read model, but
  no dedicated safe read route is mapped.
- `none`: no current committed model/source/route is mapped for the read
  surface in this inventory.

Gap posture meanings:

- `route_gap`: backing data exists, but a tenant/patient/practice-scoped read
  route is missing.
- `route_and_shape_gap`: backing data exists, but a read route and lossless SDL
  mapping are both missing.
- `source_and_licensing_gap`: no approved local/cited source exists for the read
  surface, and licensing/source review is a prerequisite.

## Future Read-Model Requirements

Before any gap becomes a runtime read model:

- practitioner reads must be practice-scoped, active-filtered, and limited to
  the display-safe `Practitioner` shape reserved in the SDL;
- reminder reads must be patient-scoped, practice-scoped, and read-only, with
  no dismissal or mutation authority; any future schema must explicitly handle
  `due_date` versus `dueAt` and the missing `COMPLETED` status representation;
- message reads must be patient-scoped, practice-scoped, and summary-only, with
  no SMS send/receive or internal-message mutation authority; any future schema
  must avoid raw bodies, document the InternalMessage/SmsLog two-table split,
  and keep EMAIL as an unfilled SDL reservation until a reviewed model exists;
- RACGP and Cochrane directory reads must use a reviewed local/cited source and
  source labels, not provider prompts, practice-knowledge advisory facts, RAG,
  GraphRAG, or raw web retrieval;
- every future route must remain a GET/read surface and must not become a
  GraphQL mutation or command tunnel.

## Deliberate Exclusions

This inventory does not map:

- practitioner create/update/onboarding commands;
- reminder dismissal, creation, escalation, or result-triage commands;
- SMS send/receive, internal message creation, or notification commands;
- RACGP/Cochrane provider, RAG, GraphRAG, web-search, or live external lookup
  wiring;
- Access AI invocation, provider prompt, provider response, or provider dry-run
  surfaces;
- practice-knowledge advisory facts as directory authority.

## Closed Gates

This inventory does not authorize:

- adding GraphQL resolvers or GraphQL mutations;
- adding new REST routes;
- adding provider calls or live provider gates;
- provider dry-run wiring;
- runtime FGA clients;
- external patient clients;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- broad historical diary trove mining;
- Access AI invocation wiring;
- reminder, message, SMS, practitioner, or directory write authority;
- model-to-database writes outside REST command handlers;
- raw compatibility deprecation mode changes.

## Boundary

This is a static gap inventory. It does not prove runtime GraphQL resolver
implementation, route authorization policy, database query shape, pagination,
performance, provider readiness, external directory licensing, patient-facing
client readiness, or deployment readiness.

`tests/test_api_spine_external_read_model_gap_inventory.py` validates this file
by parsing only this markdown file, the GraphQL SDL, selected model/router
sources, and `docs/api-spine/external-router-read-root-inventory.md`.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_external_read_model_gap_inventory.py -q
```
