# Patient Messages Read-Shape Design

Date: 2026-07-08

Sprint: 217

## Purpose

This design packet follows
`docs/api-spine/external-router-read-model-gap-inventory.md` for the
`Query.patient.messages` gap.

It defines a future patient message summary read shape only. It does not add a
REST route, GraphQL resolver, GraphQL mutation, Pydantic schema, database
query, provider call, runtime FGA client, Access AI invocation, SMS send/receive
workflow, internal-message workflow, or write authority.

This design does not add a REST route.

## Target Read Surface

| GraphQL read surface | Current gap posture | Future REST read shape | Runtime status |
|---|---|---|---|
| `Query.patient.messages` | `route_and_shape_gap` | `GET /api/v1/patients/{patient_id}/messages` or equivalent patient-scoped GET read | `not_implemented` |

## Display-Safe Field Mapping

| GraphQL field | Current source | Mapping posture | Notes |
|---|---|---|---|
| `PatientMessageSummary.id` | `InternalMessage.id`; `SmsLog.id` | `union_id_gap` | Future read must namespace or otherwise disambiguate IDs across the two backing tables before exposing a single list, such as `internal-{id}` and `sms-{id}`. |
| `PatientMessageSummary.sentAt` | `InternalMessage.created_at`; `SmsLog.sent_at` | `derive_rename_gap` | `SmsLog.sent_at` is a sent timestamp, while `InternalMessage.created_at` is only a creation-time proxy; future read must document ordering and null/default behavior before runtime exposure. |
| `PatientMessageSummary.channel` | `InternalMessage`; `SmsLog`; no email model | `incomplete_channel_enum` | `INTERNAL` and `SMS` can be derived from table source, but `EMAIL` has no current backing model/source. |
| `PatientMessageSummary.summary` | `InternalMessage.subject`; `SmsLog.message_body` | `derive_truncate` | Summary must be display-safe and bounded; prefer bounded `InternalMessage.subject`, and raw message bodies must not be projected as-is. |
| `PatientMessageSummary.status` | `InternalMessage.is_read`; `SmsLog.status`; `SmsDirection` | `incomplete_enum_gap` | Internal read/unread and SMS delivery/reply statuses do not map cleanly to the SDL `MessageStatus` enum without a reviewed union policy. |

## Current Supporting Evidence

- `InternalMessage` exists in `app/models/messaging.py` with practice, sender,
  recipient, optional patient, optional appointment, subject, body, priority,
  read state, and created timestamp fields.
- `SmsLog` exists in `app/models/messaging.py` with practice, optional patient,
  direction, phone number, raw body, SMS type, delivery/reply status, external
  ClickSend identifier, and sent timestamp fields.
- Both models have practice indexes; `SmsLog` also has a patient index.
- Current `app/routers/patients.py` exposes patient demographics and clinical
  summary reads, but no patient message summary read.
- Current `app/routers/clinical.py` exposes clinical subresource reads and
  writes, but no patient message summary read.
- Existing messaging data is potential backing evidence only. It is not a
  current API read model and not evidence that `Query.patient.messages` is
  implemented.
  It is not evidence that `Query.patient.messages` is implemented.

## Known Shape Gaps

- No current dedicated patient messages GET route exists.
- No current `PatientMessageSummaryOut` or equivalent response schema exists.
- The future shape likely needs a two-table union over `InternalMessage` and `SmsLog`.
- `InternalMessage` is staff-to-staff communication with an optional patient
  link; it is not necessarily a patient-facing message, and a future route may need to exclude internal-message bodies entirely or use subject-only summary semantics.
- `SmsLog` direction and SMS type need a reviewed inclusion policy; bulk SMS and
  inbound replies may not be appropriate for the first patient message summary
  read.
- `SmsLog.phone_number`, `clicksend_message_id`, raw `message_body`, raw `body`, sender/recipient IDs, appointment IDs, and external delivery IDs are
  deliberately outside the future patient message summary read shape.
- `MessageChannel.EMAIL` is reserved in the SDL but has no current backing model/source; `EMAIL` is reserved in the SDL but has no current backing model/source.
- `MessageStatus` needs a reviewed union policy: `InternalMessage.is_read` can
  support `READ` versus an unread/internal state, while `SmsStatus` values such
  as `Queued`, `Sent`, `Delivered`, `Failed`, and `Replied` do not map
  losslessly to `DRAFT`, `SENT`, `RECEIVED`, `FAILED`, and `READ`; current
  sources do not map cleanly to the SDL `MessageStatus` enum.
- SMS send/receive, internal-message creation, notification delivery, and
  messaging audit workflows are command surfaces, not part of this read-shape
  design.

## Future Route Requirements

Before any implementation sprint may add the patient messages read:

- the route must be a patient-scoped GET read under an explicit reviewed path;
- the route must depend on the authenticated user and filter by `current_user.practice_id`;
- the route must verify the requested patient belongs to the authenticated user's practice before reading messages;
- the response shape must include only `id`, `sentAt`, `channel`, bounded `summary`, and `status`;
- the two-table union must document ID namespace, timestamp ordering, channel derivation, and status mapping;
- `EMAIL` must remain unreachable or omitted until a reviewed backing model/source exists;
- raw message bodies must not be exposed without a truncation/redaction policy;
- `InternalMessage.subject` should be preferred over `InternalMessage.body`; SMS summaries need a reviewed truncation limit before runtime exposure;
- bulk SMS should be default-excluded unless a later review explicitly approves it;
- ordering must be deterministic, preferably by message timestamp descending with stable source/id tie-breakers;
- pagination or bounded result-size policy must be documented before production rollout;
- the route must not expose phone numbers, ClickSend IDs, sender IDs, recipient IDs, appointment IDs, raw patient identifiers beyond the route scope, raw bodies, audit internals, or command payloads;
- the route must not send, receive, create, mark-read, retry, deliver, or mutate messages;
- the route must not be used as provider, RAG, GraphRAG, Access AI, or external patient-client authority.

## Closed Gates

This design does not authorize:

- adding a REST patient messages route;
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
- SMS send/receive, internal-message creation, mark-read, retry, delivery, or notification commands;
- result-triage, reminder, appointment, practitioner, or directory write authority;
- model-to-database writes outside REST command handlers;
- raw compatibility deprecation mode changes.

## Boundary

This is a static read-shape design packet. It does not prove runtime GraphQL
resolver implementation, REST route authorization, patient scoping, union query
correctness, ID namespacing, timestamp ordering, message status semantics, text
redaction, pagination, performance, deployment readiness, or patient-facing
client readiness. It does not prove patient-facing client readiness.

`tests/test_api_spine_patient_messages_read_shape_design.py` validates this
packet by parsing only this markdown file, the GraphQL SDL, selected
model/router/schema source files, and the external read-model gap inventory.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_patient_messages_read_shape_design.py -q
```
