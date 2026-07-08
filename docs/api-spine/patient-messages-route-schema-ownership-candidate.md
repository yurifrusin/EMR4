# Patient Messages Route/Schema Ownership Candidate

Date: 2026-07-08

Sprint: 225

## Purpose

This candidate packet follows
`docs/api-spine/patient-messages-read-shape-design.md` and the external
read-model implementation-planning review.

It narrows the future ownership discussion for `Query.patient.messages`
without implementing anything. It does not add a REST route, GraphQL resolver,
GraphQL mutation, Pydantic schema, database query, provider call, Access AI
invocation, RAG, GraphRAG, runtime FGA client, external patient client,
SMS send/receive workflow, internal-message workflow, or write authority.

## Candidate Ownership

| Planning item | Candidate | Status | Notes |
|---|---|---|---|
| `route_path` | `GET /api/v1/patients/{patient_id}/messages` | `candidate_only` | Preferred explicit patient-scoped read path; no route exists or is approved here. |
| `router_owner` | existing `app/routers/patients.py` with prefix `/api/v1/patients` | `candidate_only` | Keep the patient message read near `get_patient` and `get_patient_summary`; do not treat clinical subresource routes as message authority. |
| `schema_owner` | existing `app/schemas/patients.py::PatientMessageSummaryOut` | `candidate_only` | Keep the display-safe patient read shape beside other patient summaries; must not add `PatientMessageSummaryOut` in this sprint. |
| `graphql_owner` | future external read-model resolver layer | `candidate_only` | Resolver remains blocked until route/read-service ownership and authorization are reviewed. |
| `model_anchor` | `app/models/messaging.py::InternalMessage` and `app/models/messaging.py::SmsLog` | `evidence_only` | Model fields exist, but model evidence is not route/schema implementation. The two-table union over separate backing tables is a documented shape gap. |
| `auth_dependency` | authenticated current user with practice and patient scoping | `candidate_only` | Must verify the requested patient belongs to `current_user.practice_id` before reading messages. |

## Candidate Response Shape

| Field | Candidate source | Planning posture |
|---|---|---|
| `id` | `InternalMessage.id` or `SmsLog.id` with ID namespace prefix (`internal-{id}`, `sms-{id}`) | `union_id_namespace_pending` |
| `sentAt` | `InternalMessage.created_at` (proxy); `SmsLog.sent_at` (actual sent) | `derive_rename_gap` |
| `channel` | derived from backing table source; `INTERNAL` or `SMS`; no `EMAIL` model exists | `derive_channel_incomplete_enum` |
| `summary` | `InternalMessage.subject` preferred; `SmsLog.message_body` requires reviewed truncation/redaction | `derive_truncate_display_safe` |
| `status` | `InternalMessage.is_read`; `SmsLog.status` with `SmsDirection`; no clean union map to SDL `MessageStatus` exists | `incomplete_status_union_pending` |

## Static Preconditions Before Implementation Proposal

Before any implementation sprint may add a patient messages route or schema, a
future proposal must document:

- final router module and route path;
- final schema module and class name;
- auth dependency, same-practice filtering, and requested-patient ownership
  check before message access;
- ID namespace strategy for the two-table union over `InternalMessage` and `SmsLog`,
  such as `internal-{id}` and `sms-{id}` prefixes;
- timestamp mapping policy for `sentAt`: `InternalMessage.created_at` is a
  creation proxy while `SmsLog.sent_at` is a true sent timestamp; null/default
  behavior and ordering must be documented before runtime exposure;
- `INTERNAL`/`SMS` channel derivation from table source, with explicit
  unreachable `EMAIL` until a reviewed backing model/source exists;
- summary derivation and truncation/redaction policy: `InternalMessage.subject`
  preferred over `InternalMessage.body`; `SmsLog.message_body` requires a
  reviewed truncation limit;
- `SmsLog` inclusion policy: direction and `SmsType` filtering must be
  documented; bulk SMS and inbound replies must be default-excluded unless a
  later review explicitly approves them;
- status mapping that covers `InternalMessage.is_read` (READ vs. unread/internal)
  and `SmsStatus` values (`Queued`, `Sent`, `Delivered`, `Failed`, `Replied`)
  without lossy mapping to SDL `MessageStatus` (`DRAFT`, `SENT`, `RECEIVED`,
  `FAILED`, `READ`);
- pagination default and maximum result count, with candidate
  `default_limit=20` and `max_limit=100` recorded as unapproved planning
  values;
- deterministic ordering by message timestamp descending with stable source/id
  tie-breakers, recorded as an unapproved planning value;
- empty result behavior, with candidate `200` plus empty list recorded as an
  unapproved planning value;
- missing or cross-practice patient behavior, with candidate `404` recorded as
  an unapproved anti-enumeration planning value;
- forbidden field list covering phone numbers, ClickSend IDs, sender IDs,
  recipient IDs, appointment IDs, raw patient identifiers beyond the route
  scope, raw message bodies, raw `InternalMessage.body`, `SmsLog.direction`,
  `SmsLog.sms_type`, `InternalMessage.priority`, audit internals, command
  payloads, and raw model dumps;
- GraphQL resolver owner and resolver authorization plan;
- tests for auth denial, practice scoping, patient ownership, two-table union
  ID namespace, timestamp ordering, channel derivation, bounded summary,
  status mapping, deterministic ordering, pagination limits, bulk/inbound
  exclusion, no provider calls, no Access AI invocation, no RAG/GraphRAG, no
  writes, and no EMAIL exposure.

Candidate defaults such as `default_limit=20`, `max_limit=100`, ordering by
message timestamp descending with stable tie-breakers, and missing/cross-practice
patients returning `404` may be proposed later, but they are not approved by
this packet.

## Current Non-Implementation Evidence

- `InternalMessage` exists in `app/models/messaging.py` with `practice_id`,
  `sender_id`, `recipient_id`, `patient_id`, `appointment_id`, `subject`,
  `body`, `priority`, `is_read`, and `created_at` fields.
- `InternalMessage` has indexes on `practice_id` and `recipient_id`.
- `SmsLog` exists in `app/models/messaging.py` with `practice_id`,
  `patient_id`, `direction`, `phone_number`, `message_body`, `sms_type`,
  `status`, `clicksend_message_id`, and `sent_at` fields.
- `SmsLog` has indexes on `practice_id` and `patient_id`, which can support
  a future scoped read.
- `GET /api/v1/patients/{patient_id}` and
  `GET /api/v1/patients/{patient_id}/summary` already verify the patient
  belongs to the authenticated practice, but those routes are not message list
  routes.
- `app/routers/clinical.py` owns clinical subresources under the same patient
  prefix, but it does not currently expose patient message summaries.
- `app/schemas/patients.py` contains patient summary schemas but no
  patient-message response schema.

## Deliberate Exclusions

This packet does not map or approve:

- REST route implementation;
- GraphQL resolver or mutation implementation;
- Pydantic runtime schemas;
- database queries, joins, indexes, migrations, or query optimization;
- two-table union query logic, ID namespace generation, or timestamp mapping;
- free-text message body exposure beyond a reviewed summary;
- `MessageChannel.EMAIL` support without a reviewed backing model/source;
- `MessageStatus` lossy mapping without a reviewed union policy;
- raw message bodies, phone numbers, `clicksend_message_id`, sender/recipient
  IDs, appointment IDs, `SmsLog.direction`, `SmsLog.sms_type`,
  `InternalMessage.priority`, patient identifiers beyond the route scope,
  audit internals, command payloads, or raw model dumps;
- provider calls, live provider gates, provider dry-run wiring, Access AI
  invocation, RAG, GraphRAG, memory, or practice-knowledge facts as message
  authority;
- H15/H-series runtime imports or broad historical diary trove mining;
- external patient clients or runtime FGA clients;
- SMS send/receive, internal-message creation, mark-read, retry, delivery,
  notification, or audit commands;
- result-triage, reminder, appointment, practitioner, or directory write
  authority;
- model-to-database writes outside REST command handlers;
- raw compatibility deprecation mode changes.

## Closed Gates

This candidate does not authorize:

- adding a REST patient messages route;
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
- SMS send/receive, internal-message creation, mark-read, retry, delivery, or
  notification commands;
- result-triage, reminder, appointment, practitioner, or directory write
  authority;
- model-to-database writes outside REST command handlers;
- raw compatibility deprecation mode changes.

## Boundary

This is a static ownership candidate packet. It does not prove runtime GraphQL
resolver implementation, REST route authorization, database query correctness,
patient scoping correctness, two-table union correctness, ID namespace
correctness, timestamp ordering correctness, channel derivation correctness,
summary redaction correctness, pagination, message status semantics,
performance, deployment readiness, provider readiness, external directory
readiness, patient-facing client readiness, or production readiness.

`tests/test_api_spine_patient_messages_ownership_candidate.py` validates this
packet by parsing only this markdown file, the patient messages read-shape
design, implementation-planning review, selected router/schema/model sources,
and the blocked readiness snapshot.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_patient_messages_ownership_candidate.py -q
```
