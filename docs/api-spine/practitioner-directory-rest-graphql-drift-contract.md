# Practitioner Directory REST/GraphQL Drift Contract

Date: 2026-07-08

Sprint: 229

Updated: 2026-07-09, Sprint 266, after the REST consumer runtime evidence
passed. The SDL drift items recorded in Sprint 229 are now resolved in the
non-runtime SDL artifact; GraphQL resolver/runtime readiness remains false.

## Purpose

This packet defines the canonical drift contract between the future REST
practitioner directory response and the future GraphQL
`Query.practice.practitioners` facade.

It follows:

- `docs/api-spine/practitioner-directory-first-runtime-implementation-proposal.md`
- `docs/api-spine/practitioner-directory-graphql-resolver-ownership-plan.md`
- `docs/api-spine/graphql/appointment-diary-read.graphql`

This is a static contract only. It does not add a REST route, GraphQL resolver,
GraphQL runtime dependency, Pydantic runtime schema, shared read service,
database query, join, index, migration, provider call, Access AI invocation,
RAG, GraphRAG, runtime FGA client, external patient client, broad historical
diary trove access, or write authority.

## Gate Verdict

| Gate item | Sprint 229 value |
|---|---|
| `rest_graphql_drift_contract_defined` | `true` |
| `canonical_projection_field_set_defined` | `true` |
| `sensitive_exclusion_parity_defined` | `true` |
| `shared_read_service_invariants_defined` | `true` |
| `default_location_shape_status` | `sdl_aligned_to_brief_shape` |
| `graphql_pagination_shape_status` | `sdl_aligned_with_limit_offset` |
| `shared_read_service_exists` | `true` |
| `runtime_code_authorized` | `false` |
| `rest_route_ready` | `false` |
| `graphql_resolver_ready` | `false` |
| `external_read_model_runtime_ready` | `false` |
| `readiness_snapshot_decision` | `blocked` |
| `pause_required_before_route_or_resolver_code` | `true` |
| `explicit_yuri_go_no_go_required` | `true` |

Acceptance of this drift contract is not approval to add route, resolver,
schema, read-service, database, or GraphQL runtime code.

## Canonical Projection

Both future surfaces must expose exactly the same logical practitioner
directory projection:

| Canonical field | REST `PractitionerOut` | GraphQL `Practitioner` | Source | Rule |
|---|---|---|---|---|
| `id` | `UUID` | `ID!` | `Practitioner.id` | practice-scoped direct field |
| `displayName` | `str` | `String!` | `Practitioner.first_name` plus `Practitioner.last_name` | join non-empty, trimmed name parts with one space |
| `roleLabel` | `string or null` | `String` | `Practitioner.specialty` | nullable passthrough for first implementation |
| `active` | `bool` | `Boolean!` | `Practitioner.is_active` | renamed display field |
| `defaultLocation` | `PractitionerDefaultLocationOut or null` | restricted brief location or null | `Practitioner.default_location_id` plus `PracticeLocation` | same-practice active join; `{id, name}` only |

The canonical field set is:

- `id`
- `displayName`
- `roleLabel`
- `active`
- `defaultLocation`

Adding, removing, or renaming a field on only one surface is a drift defect. The
model field `is_active` must never leak as `is_active` on either surface.

## Resolved SDL Drift

Two former SDL/document mismatches recorded in Sprint 229 have been resolved in
the non-runtime SDL artifact:

1. `Practitioner.defaultLocation` now points to `PracticeLocationBrief`, whose
   fields are exactly `id` and `name`.
2. `Practice.practitioners` now declares reviewed `limit` and `offset`
   arguments:
   `practitioners(activeOnly: Boolean = true, limit: Int = 50, offset: Int = 0)`.

These SDL changes do not authorize GraphQL runtime dependencies, a GraphQL
server, resolver code, production introspection, deployment readiness, or
readiness-flag changes.

## Shared Read-Service Invariants

Future REST and GraphQL code must both call the same shared read service, named
by Sprint 228 as future `app/services/practice/practitioner_directory_read.py`.
The shared service is the sole data path and owns:

1. `Practitioner.practice_id == viewer.practice_id` practice scoping.
2. `displayName` derivation.
3. `activeOnly=true` default filtering.
4. `activeOnly=false` admin/owner gate.
5. deterministic ordering by `Practitioner.last_name`, then
   `Practitioner.first_name`, then `Practitioner.id`.
6. pagination defaults and caps: `limit=50`, maximum `200`, `offset=0`,
   minimum offset `0`.
7. same-practice active default-location join.
8. display-safe `{id, name}` default-location projection.
9. sensitive-field exclusion.
10. provider/Access AI/RAG/GraphRAG/trove prohibition.
11. no write authority.

The future GraphQL resolver must not call the REST route over HTTP, import REST
router modules, import REST Pydantic schemas as authority, or perform
independent SQLAlchemy queries inside a field resolver. The future REST route
must not contain independent query logic that can diverge from GraphQL.

## Sensitive Exclusion Parity

This is the canonical forbidden field list for both surfaces:

- `provider_number`
- `prescriber_number`
- `ahpra_number`
- `hpi_i`
- `practice_id`
- `created_at`
- `email`
- `phone`
- `address`
- `password_hash`
- `credentials`
- `schedule_overrides`
- `schedules`
- `appointments`
- clinical logs
- roster internals
- raw SQLAlchemy model dumps
- location address
- location phone
- location email
- location billing details
- availability internals

The future REST and GraphQL test suites must assert forbidden response keys. The
directory projection must stay distinct from appointment/diary supervised
booking schemas such as `PractitionerBrief` or Bernie practitioner evidence
shapes that may contain booking-context-only identifiers.

## Parameter And Error Parity

| Concern | Canonical rule |
|---|---|
| `activeOnly` | default `true`; camelCase preserved on both surfaces |
| inactive inclusion | `activeOnly=false` requires `Admin` or `PracticeOwner`; if authority cannot be proved, fail closed |
| REST role failure | `403` |
| GraphQL role failure | `FORBIDDEN` |
| unauthenticated | REST `401`; GraphQL `UNAUTHENTICATED` |
| invalid arguments | REST `422`; GraphQL `BAD_USER_INPUT` |
| raw SQL errors | never exposed on either surface |
| ordering | `last_name`, then `first_name`, then `id` |
| empty result | REST `200 []`; GraphQL empty list under authorized practice context |
| cross-practice data | silently absent through tenancy filtering; no existence leak |

## Current Non-Implementation Evidence

Current source remains non-runtime for GraphQL:

- `app/routers/practice.py` exists for the REST route;
- `app/schemas/practice.py` exists for the REST response contract;
- `app/services/practice/practitioner_directory_read.py` exists as the shared
  read-service data path;
- `class PractitionerOut` exists;
- `class PractitionerDefaultLocationOut` exists;
- no `def list_practitioners`;
- no `Query.practice.practitioners` resolver;
- no GraphQL runtime dependency or server wiring;
- `blocked_readiness_status.json` remains `blocked` with
  `rest_route_ready=false`, `graphql_resolver_ready=false`, and
  `external_read_model_runtime_ready=false`.

## Drift Detection Tests

This contract is guarded by static tests that parse markdown, SDL, JSON, and
selected source text only. They must not import or execute a GraphQL runtime,
FastAPI route, database session, read service, provider, Access AI, RAG,
GraphRAG, or H15/H-series material.

Required static checks:

1. `test_drift_contract_gate_verdict_keeps_runtime_blocked`
2. `test_canonical_projection_is_exactly_five_fields`
3. `test_sdl_practitioner_field_set_matches_projection`
4. `test_default_location_shape_is_sdl_aligned_to_brief`
5. `test_graphql_pagination_shape_is_sdl_aligned`
6. `test_shared_read_service_invariants_are_defined_and_implemented`
7. `test_sensitive_exclusion_parity_is_canonical`
8. `test_active_only_pagination_ordering_and_error_parity_defined`
9. `test_current_code_has_rest_slice_but_no_graphql_resolver`
10. `test_readiness_snapshot_remains_blocked`
11. `test_closed_gates_preserved`
12. `test_boundary_says_contract_is_not_runtime_or_production_readiness`

## Gates Still Closed

This packet does not authorize:

- adding GraphQL resolvers or GraphQL mutations;
- adding a GraphQL runtime dependency or server;
- adding GraphQL runtime database queries, joins, indexes, migrations, read
  services, or query services outside the existing shared REST read service;
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
- practitioner create/update/onboarding commands;
- appointment, roster, schedule, diary, billing, result, reminder, message,
  SMS, or clinical write authority;
- model-to-database writes outside REST command handlers;
- raw compatibility deprecation mode changes.

## Boundary

This is a static REST/GraphQL drift contract. It proves only that the future
practitioner directory REST and GraphQL surfaces have a reviewed parity
contract and that current mismatches are known and blocked before runtime. It
does not prove runtime REST authorization, GraphQL authorization, resolver
correctness, route correctness, database query correctness, field-level
authorization, pagination performance, deployment readiness, provider
readiness, external directory readiness, patient-facing client readiness, or
production readiness.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_practitioner_directory_rest_graphql_drift_contract.py -q
```
