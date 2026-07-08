# External Read-Model Ownership Consolidation Preflight

Date: 2026-07-08

Sprint: 226

## Purpose

This preflight consolidates the three static ownership candidates added for the
external read-model gap set:

- `Query.practice.practitioners(activeOnly: Boolean = true)`;
- `Query.patient.reminders`;
- `Query.patient.messages`.

It does not approve implementation. It does not add REST routes, GraphQL
resolvers, GraphQL mutations, Pydantic schemas, database queries, migrations,
provider calls, Access AI invocation, RAG, GraphRAG, runtime FGA clients,
external patient clients, source manifests, or write authority.

## Consolidated Inputs

| Candidate | Artifact | Gap posture | Ownership posture |
|---|---|---|---|
| `practice_practitioners` | `docs/api-spine/practitioner-directory-route-schema-ownership-candidate.md` | `route_gap` | `candidate_only` route/schema ownership with `evidence_only` model anchor |
| `patient_reminders` | `docs/api-spine/patient-reminders-route-schema-ownership-candidate.md` | `route_and_shape_gap` | `candidate_only` route/schema ownership with `evidence_only` model anchor |
| `patient_messages` | `docs/api-spine/patient-messages-route-schema-ownership-candidate.md` | `route_and_shape_gap` | `candidate_only` route/schema ownership with `evidence_only` model anchors |

All three candidates inherit the blocked posture from
`docs/api-spine/external-read-model-implementation-planning-review.md`,
`docs/api-spine/external-read-model-combined-readiness-review.md`,
`docs/api-spine/external-read-model-readiness-dag.json`, and
`tests/fixtures/api_spine_external_readiness/blocked_readiness_status.json`.

## Ownership Matrix

| Candidate | Future REST read path | Router owner | Schema owner | Model evidence | Runtime status |
|---|---|---|---|---|---|
| `practice_practitioners` | `GET /api/v1/practice/practitioners` | new `app/routers/practice.py` | new `app/schemas/practice.py::PractitionerOut` | `app/models/tenancy.py::Practitioner` | `blocked` |
| `patient_reminders` | `GET /api/v1/patients/{patient_id}/reminders` | existing `app/routers/patients.py` | existing `app/schemas/patients.py::PatientReminderOut` | `app/models/results.py::Reminder` | `blocked` |
| `patient_messages` | `GET /api/v1/patients/{patient_id}/messages` | existing `app/routers/patients.py` | existing `app/schemas/patients.py::PatientMessageSummaryOut` | `app/models/messaging.py::InternalMessage`; `app/models/messaging.py::SmsLog` | `blocked` |

The ownership split is intentional:

- practitioner directory is practice-scoped and belongs under a future explicit
  practice router;
- reminders and messages are patient-scoped read summaries and belong near the
  existing patient read routes;
- GraphQL ownership remains a future external read-model resolver layer for all
  three candidates and is not approved here.

## Complexity Ranking

| Rank | Candidate | Reason |
|---|---|---|
| `1_lowest` | `practice_practitioners` | Single table, practice-scoped only, no patient ownership check, no date conversion, no incomplete enum, no two-table union. |
| `2_middle` | `patient_reminders` | Single table but requires patient ownership, date-only to `DateTime` policy, bounded free-text summary policy, and `COMPLETED` status remains unavailable. |
| `3_highest` | `patient_messages` | Two-table `InternalMessage`/`SmsLog` union with ID namespace, timestamp, channel, status, body truncation, bulk SMS, inbound reply, and internal-staff-message policy gaps. |

## First Runtime Go/No-Go Candidate

Recommended first go/no-go candidate: `practice_practitioners`.

This is not implementation approval. It means a future sprint may write a
reviewed implementation proposal for the practitioner directory before the
patient reminder or patient message surfaces, provided the proposal still keeps
the current readiness snapshot blocked until explicitly replaced.

Rationale:

- it is the only `route_gap`, while reminders and messages remain
  `route_and_shape_gap`;
- it is practice-scoped only and avoids patient anti-enumeration handling;
- it does not expose patient PHI, reminder free text, phone numbers, ClickSend
  IDs, internal staff message bodies, or result/referral context;
- it has a single backing table and no union-ID namespace or lossy status map;
- its main implementation risk is sensitive practitioner identifier exclusion,
  which can be tested deterministically at the response-schema boundary.

## Preflight Checks Before Any Implementation Proposal

Before any runtime route or schema sprint, the proposal must prove:

1. `blocked_readiness_status.json` still has `dag_decision: blocked`,
   `rest_route_ready: false`, `graphql_resolver_ready: false`, and
   `external_read_model_runtime_ready: false`.
2. The target candidate's ownership packet still has only `candidate_only` and
   `evidence_only` ownership rows.
3. No current router contains `@router.get("/practice/practitioners"`,
   `@router.get("/{patient_id}/reminders"`, or
   `@router.get("/{patient_id}/messages"`.
4. No current schema file contains `class PractitionerOut`,
   `class PatientReminderOut`, or `class PatientMessageSummaryOut`.
5. The implementation proposal lists auth denial, practice scoping, patient
   scoping where applicable, pagination, deterministic ordering, empty/error
   behavior, forbidden fields, and no-provider/no-write tests before code.
6. GraphQL resolver ownership and authorization remain plan-only unless a
   separate reviewed GraphQL implementation proposal is opened later.
7. Runtime readiness flags remain false unless Yuri explicitly approves a gate
   replacement with updated tests and closeout language.

## Candidate-Specific Preflight Emphasis

| Candidate | Must resolve before route code |
|---|---|
| `practice_practitioners` | `PractitionerOut` sensitive-field exclusions; `displayName` derivation; active-only default; default-location join scope; `default_limit=50`; `max_limit=200`; deterministic name/id ordering. |
| `patient_reminders` | patient ownership `404`; `dueAt` date-to-DateTime policy; bounded summary policy; `OPEN`/`DISMISSED` status map; `COMPLETED` unavailable; `default_limit=20`; `max_limit=100`. |
| `patient_messages` | two-table union policy; `internal-{id}`/`sms-{id}` namespace or equivalent; timestamp ordering; `EMAIL` blocked; bulk SMS and inbound reply policy; status union policy; raw body/phone/internal staff exclusions. |

## Closed Gates

This preflight does not authorize:

- adding REST routes;
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
- source manifests as approved runtime configuration;
- RACGP or Cochrane content ingestion, indexing, caching, embedding, scraping,
  live lookup, or sync jobs;
- reminder, message, SMS, practitioner, directory, appointment, billing, result,
  or clinical write authority;
- model-to-database writes outside REST command handlers;
- raw compatibility deprecation mode changes.

## Boundary

This is a static consolidation and go/no-go preflight. It does not prove runtime
GraphQL resolver implementation, REST route authorization, database query
correctness, patient scoping correctness, practitioner sensitive-field
exclusion at runtime, reminder date/status correctness, message union
correctness, pagination, performance, deployment readiness, provider readiness,
external directory readiness, patient-facing client readiness, or production
readiness.

`tests/test_api_spine_external_read_model_ownership_consolidation.py` validates
this packet by parsing only static markdown/JSON artifacts and selected current
router/schema source files.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_external_read_model_ownership_consolidation.py -q
```
