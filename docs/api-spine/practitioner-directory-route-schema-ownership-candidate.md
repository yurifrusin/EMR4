# Practitioner Directory Route/Schema Ownership Candidate

Date: 2026-07-08

Sprint: 223

## Purpose

This candidate packet follows
`docs/api-spine/practitioner-directory-read-shape-design.md` and the external
read-model implementation-planning review.

It narrows the future ownership discussion for
`Query.practice.practitioners(activeOnly: Boolean = true)` without implementing
anything. It does not add a REST route, GraphQL resolver, GraphQL mutation,
Pydantic schema, database query, provider call, Access AI invocation, RAG,
GraphRAG, runtime FGA client, external patient client, or write authority.

## Candidate Ownership

| Planning item | Candidate | Status | Notes |
|---|---|---|---|
| `route_path` | `GET /api/v1/practice/practitioners` | `candidate_only` | Preferred explicit practice read path; no route exists or is approved here. |
| `router_owner` | new `app/routers/practice.py` with prefix `/api/v1/practice` | `candidate_only` | Avoid overloading diary context routes; final owner needs explicit implementation proposal. |
| `schema_owner` | new `app/schemas/practice.py::PractitionerOut` | `candidate_only` | Keep practice directory schemas out of diary schemas; must not add `PractitionerOut` in this sprint. |
| `graphql_owner` | future external read-model resolver layer | `candidate_only` | Resolver remains blocked until route/read-service ownership and authorization are reviewed. |
| `model_anchor` | `app/models/tenancy.py::Practitioner` | `evidence_only` | Model fields exist, but model evidence is not route/schema implementation. |
| `auth_dependency` | authenticated current user with practice scoping | `candidate_only` | Must filter by `current_user.practice_id` in any future implementation. |

## Candidate Response Shape

| Field | Candidate source | Planning posture |
|---|---|---|
| `id` | `Practitioner.id` | `direct_practice_scoped` |
| `displayName` | `Practitioner.first_name` plus `Practitioner.last_name` | `derive_display_safe` |
| `roleLabel` | `Practitioner.specialty` | `optional_pending_semantics` |
| `active` | `Practitioner.is_active` | `rename_default_true_filter` |
| `defaultLocation` | `Practitioner.default_location_id` plus `PracticeLocation` | `linked_read_pending` |

## Static Preconditions Before Implementation Proposal

Before any implementation sprint may add a practitioner directory route or
schema, a future proposal must document:

- final router module and route path;
- final schema module and class name;
- auth dependency and same-practice filtering;
- default `activeOnly=true` behavior and explicit inactive-inclusion policy;
- display-name derivation and deterministic ordering;
- pagination default and maximum result count, with candidate `default_limit=50`
  and `max_limit=200` recorded as unapproved planning values;
- deterministic ordering by `Practitioner.last_name`, then
  `Practitioner.first_name`, then `Practitioner.id` as an unapproved planning
  value;
- empty result behavior, with candidate `200` plus empty list recorded as an
  unapproved planning value;
- inactive-inclusion error behavior, with candidate admin-only review recorded
  as an unapproved planning value;
- forbidden field list covering provider number, prescriber number, AHPRA,
  HPI-I, email, phone, address, credentials, schedule internals, appointment
  data, and raw model dumps;
- GraphQL resolver owner and resolver authorization plan;
- tests for auth denial, practice scoping, active-only default, display-safe
  fields, deterministic ordering, pagination limits, no provider calls, no
  Access AI invocation, no RAG/GraphRAG, and no writes.

Candidate defaults such as `default_limit=50`, `max_limit=200`, ordering by
last name then first name then `Practitioner.id`, and empty results returning
`200` with an empty list may be proposed later, but they are not approved by
this packet.

## Current Non-Implementation Evidence

- `Practice.practitioners` and `Practitioner.practice_id` exist in
  `app/models/tenancy.py`.
- `Practitioner` contains the candidate display fields and sensitive provider
  identifier fields that must remain excluded.
- `GET /api/v1/diary/template` and `GET /api/v1/diary/roster` can expose
  practitioner context for diary rendering, but those are context reads, not a
  practitioner-directory route.
- `app/schemas/diary.py` contains diary/roster/location schemas but no
  practitioner-directory response schema.

## Deliberate Exclusions

This packet does not map or approve:

- REST route implementation;
- GraphQL resolver or mutation implementation;
- Pydantic runtime schemas;
- database queries, joins, indexes, migrations, or query optimization;
- inactive-practitioner exposure;
- provider number, prescriber number, AHPRA, HPI-I, email, phone, address,
  credentials, schedule internals, appointment data, or raw model dumps;
- provider calls, live provider gates, provider dry-run wiring, Access AI
  invocation, RAG, GraphRAG, memory, or practice-knowledge facts as directory
  authority;
- H15/H-series runtime imports or broad historical diary trove mining;
- external patient clients or runtime FGA clients;
- practitioner create/update/onboarding commands;
- appointment, roster, schedule, diary, billing, result, or clinical write
  authority;
- model-to-database writes outside REST command handlers;
- raw compatibility deprecation mode changes.

## Closed Gates

This candidate does not authorize:

- adding a REST practitioner directory route;
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
- practitioner create/update/onboarding commands;
- appointment, roster, schedule, diary, billing, result, or clinical write
  authority;
- model-to-database writes outside REST command handlers;
- raw compatibility deprecation mode changes.

## Boundary

This is a static ownership candidate packet. It does not prove runtime GraphQL
resolver implementation, REST route authorization, database query correctness,
location join correctness, pagination, inactive-practitioner policy,
performance, deployment readiness, provider readiness, external directory
readiness, patient-facing client readiness, or production readiness.

`tests/test_api_spine_practitioner_directory_ownership_candidate.py` validates
this packet by parsing only this markdown file, the practitioner read-shape
design, implementation-planning review, selected router/schema/model sources,
and the blocked readiness snapshot.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_practitioner_directory_ownership_candidate.py -q
```
