# Patient Reminders Route/Schema Ownership Candidate

Date: 2026-07-08

Sprint: 224

## Purpose

This candidate packet follows
`docs/api-spine/patient-reminders-read-shape-design.md` and the external
read-model implementation-planning review.

It narrows the future ownership discussion for `Query.patient.reminders`
without implementing anything. It does not add a REST route, GraphQL resolver,
GraphQL mutation, Pydantic schema, database query, provider call, Access AI
invocation, RAG, GraphRAG, runtime FGA client, external patient client,
reminder dismissal workflow, or write authority.

## Candidate Ownership

| Planning item | Candidate | Status | Notes |
|---|---|---|---|
| `route_path` | `GET /api/v1/patients/{patient_id}/reminders` | `candidate_only` | Preferred explicit patient-scoped read path; no route exists or is approved here. |
| `router_owner` | existing `app/routers/patients.py` with prefix `/api/v1/patients` | `candidate_only` | Keep the patient reminder read near `get_patient` and `get_patient_summary`; do not treat clinical subresource routes as reminder authority. |
| `schema_owner` | existing `app/schemas/patients.py::PatientReminderOut` | `candidate_only` | Keep the display-safe patient read shape beside other patient summaries; must not add `PatientReminderOut` in this sprint. |
| `graphql_owner` | future external read-model resolver layer | `candidate_only` | Resolver remains blocked until route/read-service ownership and authorization are reviewed. |
| `model_anchor` | `app/models/results.py::Reminder` | `evidence_only` | Model fields exist, but model evidence is not route/schema implementation. |
| `auth_dependency` | authenticated current user with practice and patient scoping | `candidate_only` | Must verify the requested patient belongs to `current_user.practice_id` before reading reminders. |

## Candidate Response Shape

| Field | Candidate source | Planning posture |
|---|---|---|
| `id` | `Reminder.id` | `direct_patient_practice_scoped` |
| `dueAt` | `Reminder.due_date` | `date_to_datetime_policy_pending` |
| `summary` | `Reminder.message` plus `Reminder.reminder_type` | `derive_truncate_display_safe` |
| `status` | `Reminder.is_dismissed` | `open_or_dismissed_only_completed_unavailable` |

## Static Preconditions Before Implementation Proposal

Before any implementation sprint may add a patient reminders route or schema, a
future proposal must document:

- final router module and route path;
- final schema module and class name;
- auth dependency, same-practice filtering, and requested-patient ownership
  check before reminder access;
- date-only to `DateTime` policy for `dueAt`, including timezone and
  time-of-day handling;
- summary derivation and truncation/redaction policy for free-text
  `Reminder.message`;
- status mapping that represents `OPEN` and `DISMISSED`, while failing closed
  or omitting `COMPLETED` until a reviewed source state exists;
- pagination default and maximum result count, with candidate
  `default_limit=20` and `max_limit=100` recorded as unapproved planning
  values;
- deterministic ordering by `Reminder.due_date` ascending with null due dates
  last, then `Reminder.id` as an unapproved planning value;
- empty result behavior, with candidate `200` plus empty list recorded as an
  unapproved planning value;
- missing or cross-practice patient behavior, with candidate `404` recorded as
  an unapproved anti-enumeration planning value;
- forbidden field list covering raw message bodies, raw `reminder_type`,
  `practitioner_id`, `triggered_by_result_id`, referral/result context, patient
  identifiers beyond the route scope, audit internals, command payloads, and
  raw model dumps;
- GraphQL resolver owner and resolver authorization plan;
- tests for auth denial, practice scoping, patient ownership, bounded summary,
  date/status mapping, deterministic ordering, pagination limits, no provider
  calls, no Access AI invocation, no RAG/GraphRAG, and no writes.

Candidate defaults such as `default_limit=20`, `max_limit=100`, ordering by due
date then `Reminder.id`, and missing/cross-practice patients returning `404`
may be proposed later, but they are not approved by this packet.

## Current Non-Implementation Evidence

- `Reminder` exists in `app/models/results.py` with `practice_id`,
  `patient_id`, `practitioner_id`, `triggered_by_result_id`, `reminder_type`,
  `message`, `due_date`, and `is_dismissed` fields.
- `Reminder` has indexes on `practice_id` and `patient_id`, which can support a
  future scoped read.
- `GET /api/v1/patients/{patient_id}` and
  `GET /api/v1/patients/{patient_id}/summary` already verify the patient
  belongs to the authenticated practice, but those routes are not reminder list
  routes.
- `app/routers/clinical.py` owns clinical subresources under the same patient
  prefix, but it does not currently expose patient reminder summaries.
- `app/schemas/patients.py` contains patient summary schemas but no
  patient-reminder response schema.

## Deliberate Exclusions

This packet does not map or approve:

- REST route implementation;
- GraphQL resolver or mutation implementation;
- Pydantic runtime schemas;
- database queries, joins, indexes, migrations, or query optimization;
- date-only to `DateTime` runtime conversion;
- free-text reminder body exposure;
- `ReminderStatus.COMPLETED` support without a reviewed source state;
- raw message bodies, raw `reminder_type`, `practitioner_id`,
  `triggered_by_result_id`, referral/result context, patient identifiers beyond
  the route scope, audit internals, command payloads, or raw model dumps;
- provider calls, live provider gates, provider dry-run wiring, Access AI
  invocation, RAG, GraphRAG, memory, or practice-knowledge facts as reminder
  authority;
- H15/H-series runtime imports or broad historical diary trove mining;
- external patient clients or runtime FGA clients;
- reminder create/update/dismiss/complete/escalate commands;
- result-triage or recall-policy write authority;
- appointment, practitioner, message, SMS, directory, billing, result, or
  clinical write authority;
- model-to-database writes outside REST command handlers;
- raw compatibility deprecation mode changes.

## Closed Gates

This candidate does not authorize:

- adding a REST patient reminder route;
- adding GraphQL resolvers or GraphQL mutations;
- adding Pydantic runtime schemas;
- changing the blocked readiness snapshot;
- changing readiness flags to `true`;
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
- appointment, practitioner, message, SMS, directory, billing, result, or
  clinical write authority;
- model-to-database writes outside REST command handlers;
- raw compatibility deprecation mode changes.

## Boundary

This is a static ownership candidate packet. It does not prove runtime GraphQL
resolver implementation, REST route authorization, database query correctness,
patient scoping correctness, date-to-`DateTime` conversion correctness, summary
redaction correctness, pagination, reminder status semantics, performance,
deployment readiness, provider readiness, external directory readiness,
patient-facing client readiness, or production readiness.

`tests/test_api_spine_patient_reminders_ownership_candidate.py` validates this
packet by parsing only this markdown file, the patient reminders read-shape
design, implementation-planning review, selected router/schema/model sources,
and the blocked readiness snapshot.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_patient_reminders_ownership_candidate.py -q
```
