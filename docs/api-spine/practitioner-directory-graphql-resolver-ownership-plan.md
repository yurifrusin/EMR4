# Practitioner Directory GraphQL Resolver Ownership Plan

Date: 2026-07-08

Sprint: 228

Updated: 2026-07-09, Sprint 266, after REST consumer runtime evidence passed
and the non-runtime SDL was aligned to the REST practitioner-directory
projection. GraphQL runtime resolver/server code remains blocked.

## Purpose

This packet defines a static ownership and authorization plan for the future
GraphQL field:

- `Query.practice.practitioners(activeOnly: Boolean = true)`

It follows the Sprint 227 practitioner-directory REST implementation proposal
gate. It is a plan-only gate packet, not resolver approval. It does not add a
GraphQL runtime dependency, GraphQL server, GraphQL resolver, REST route,
Pydantic runtime schema, database query, join, migration, read service,
provider call, Access AI invocation, RAG, GraphRAG, runtime FGA client, external
patient client, broad historical diary trove access, or write authority.

## Inputs Reviewed

| Input | Required posture |
|---|---|
| `docs/api-spine/graphql/appointment-diary-read.graphql` | non-runtime SDL only; no `type Mutation` |
| `docs/api-spine/practitioner-directory-first-runtime-implementation-proposal.md` | REST route code blocked until explicit Yuri go/no-go |
| `docs/api-spine/practitioner-directory-route-schema-ownership-candidate.md` | `graphql_owner` remains `candidate_only` |
| `docs/api-spine/practitioner-directory-read-shape-design.md` | display-safe field design only |
| `docs/api-spine/external-read-model-readiness-dag.json` | `graphql_resolver_wiring` remains `blocked` |
| `tests/fixtures/api_spine_external_readiness/blocked_readiness_status.json` | `graphql_resolver_ready: false`; readiness snapshot blocked |
| Claude Sprint 228 worker review | CLI worker hand-in; review only |
| Antigravity Sprint 228 worker review | CLI worker hand-in; review only |
| DeepSeek Sprint 228 worker review | direct Codex worker hand-in; review only |

## Gate Verdict

| Gate item | Sprint 228 value |
|---|---|
| `graphql_resolver_owner_defined` | `true` |
| `graphql_authorization_plan_defined` | `true` |
| `graphql_runtime_code_authorized` | `false` |
| `graphql_server_dependency_authorized` | `false` |
| `graphql_resolver_ready` | `false` |
| `rest_route_ready` | `false` |
| `external_read_model_runtime_ready` | `false` |
| `readiness_snapshot_decision` | `blocked` |
| `rest_read_route_is_prerequisite` | `true` |
| `rest_read_service_is_sole_data_path` | `true` |
| `pause_required_before_resolver_code` | `true` |
| `explicit_yuri_go_no_go_required` | `true` |

Acceptance of this plan is not approval to add GraphQL runtime code. Resolver
code requires a separate explicit Yuri go/no-go after the REST route/read
service gate has been resolved.

## Sequencing Rule

GraphQL must not become the first path to the practitioner table.

As of Sprint 266, the REST route and named internal REST consumer evidence are
in place. The future resolver may proceed only after:

1. REST consumer runtime evidence passed.
2. `GET /api/v1/practice/practitioners` is implemented, tested, merged, and
   still excludes sensitive fields.
3. A shared practitioner directory read service exists and is used by the REST
   route.
4. A separate explicit Yuri go/no-go authorizes GraphQL runtime dependency and
   resolver work.

Until those events happen, GraphQL resolver work remains plan-only and
`graphql_resolver_ready` remains `false`.

## Resolver Ownership Contract

| Concern | Future owner |
|---|---|
| SDL of record | `docs/api-spine/graphql/appointment-diary-read.graphql` |
| Field | `Practice.practitioners(activeOnly: Boolean = true, limit: Int = 50, offset: Int = 0): [Practitioner!]!` |
| Resolver module | future `app/graphql/resolvers/practice.py` |
| Shared data path | existing `app/services/practice/practitioner_directory_read.py` |
| REST reference | existing `GET /api/v1/practice/practitioners` |
| GraphQL type | runtime subset of SDL `type Practitioner` |
| Default-location projection | display-safe `PracticeLocationBrief { id, name }` only, not the full SDL `PracticeLocation` shape |

The resolver must be a facade over the shared read service. It must not call the
REST route over HTTP, import REST router modules, import future REST Pydantic
schemas as authority, or perform independent SQLAlchemy querying inside a field
resolver. The read service owns practice scoping, ordering, pagination,
inactive inclusion, default-location joins, and field projection.

## Authorization And Tenancy Plan

| Check | Future rule |
|---|---|
| Authentication | GraphQL context must authenticate the viewer using the same principal model as REST. |
| Viewer activity | inactive users receive an unauthenticated/forbidden GraphQL error; no partial directory data. |
| Practice root | `Query.practice(id: ID)` defaults to the viewer's practice when `id` is omitted. |
| Practice id mismatch | a supplied `id` that differs from the viewer's practice returns `null` or a generic not-found response, never another practice's directory. |
| Practitioner query | every read filters `Practitioner.practice_id == viewer.practice_id`. |
| Cross-practice leakage | other-practice practitioners are silently absent through the tenancy filter. |
| Inactive inclusion | `activeOnly=false` requires `Admin` or `PracticeOwner` authority. |
| Missing role gate | if the current role model cannot prove admin/owner authority, `activeOnly=false` must fail closed. |
| Error taxonomy | auth failures map to `UNAUTHENTICATED`; role failures map to `FORBIDDEN`; invalid args map to `BAD_USER_INPUT`; raw SQL errors are never exposed. |

The resolver must not accept a client-supplied `practiceId` on the
`practitioners` field. Practice scope comes only from the authenticated viewer
and the validated parent `Practice` object.

## REST Alignment Contract

The GraphQL `Practitioner` projection must remain aligned with the future REST
`PractitionerOut` projection:

- `id`
- `displayName`
- `roleLabel`
- `active`
- `defaultLocation`

The shared read service must apply the same display-name derivation, active
filter, inactive admin gate, deterministic ordering, pagination caps, and
default-location join used by REST. Divergence between REST `PractitionerOut`
and GraphQL `Practitioner` is a contract bug.

If the REST route is not approved or implemented, the GraphQL resolver remains
blocked. GraphQL does not get an independent database path.

## Field Sensitivity

The GraphQL resolver and any future runtime GraphQL type must never expose:

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
- location address, phone, email, billing details, or availability internals

Display-safe fields are limited to:

- `id`
- `displayName`
- `roleLabel`
- `active`
- `defaultLocation` as `{id, name}` only

`defaultLocation` must use a same-practice active-location join:

- `PracticeLocation.id == Practitioner.default_location_id`
- `PracticeLocation.practice_id == viewer.practice_id`
- `PracticeLocation.is_active == true`

If the location is absent, inactive, or from another practice, GraphQL returns
`defaultLocation: null`.

## Pagination, Cost, And Depth Plan

The SDL now reserves `activeOnly`, `limit`, and `offset`; before runtime
resolver work, the resolver must enforce those bounds through the shared read
service:

| Rule | Plan value |
|---|---|
| default page size | `50` |
| maximum page size | `200` |
| offset | default `0`, minimum `0` if offset pagination is used |
| ordering | `last_name`, then `first_name`, then `id` |
| N+1 prevention | pre-join default locations in the read service or batch-load by location id |
| max depth | production runtime must enforce a global depth limit before public use |
| complexity/cost | production runtime must enforce a global complexity/cost budget before public use |
| alias repetition | cost rules must count aliased repetitions of `practice.practitioners` |
| introspection | production introspection remains a separate reviewed deployment decision |

GraphQL runtime work must not ship with an unbounded `[Practitioner!]!` list.

## Required Static Tests Before Resolver Code

The plan should remain guarded by deterministic static tests that do not import
or execute a GraphQL runtime:

1. `test_graphql_sdl_declares_practice_practitioners_without_mutation`
2. `test_graphql_practitioner_field_set_matches_rest_projection`
3. `test_graphql_resolver_gate_verdict_keeps_runtime_false`
4. `test_no_graphql_runtime_dependency_or_import_exists`
5. `test_no_query_practice_practitioners_resolver_exists`
6. `test_readiness_dag_graphql_resolver_wiring_remains_blocked`
7. `test_authorization_and_tenancy_plan_defined`
8. `test_rest_route_and_read_service_are_prerequisites`
9. `test_field_sensitivity_and_default_location_join_match_rest_contract`
10. `test_pagination_cost_depth_and_n_plus_one_plan_defined`
11. `test_closed_gates_preserved`
12. `test_boundary_says_plan_is_not_runtime_or_production_readiness`

Runtime GraphQL execution tests belong only after a separate go/no-go approves
GraphQL server and resolver code.

## Gates Still Closed

This packet does not authorize:

- adding GraphQL resolvers or GraphQL mutations;
- adding a GraphQL runtime dependency or server;
- adding Pydantic runtime schemas;
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

This is a static GraphQL ownership and authorization plan. It proves only that
the future `Query.practice.practitioners` resolver has a reviewed ownership,
sequencing, authorization, sensitivity, and complexity plan. It does not prove
runtime GraphQL authorization, resolver correctness, REST route correctness,
database query correctness, field-level authorization, pagination performance,
deployment readiness, provider readiness, external directory readiness,
patient-facing client readiness, or production readiness.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_practitioner_directory_graphql_resolver_ownership_plan.py -q
```
