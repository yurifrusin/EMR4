# Practitioner Directory SDL Pagination/DefaultLocation Resolution Proposal

Date: 2026-07-08

Sprint: 231

## Purpose

This packet proposes a future SDL-only resolution for the two
`known_and_blocked_drift` findings recorded in Sprint 229:

1. `Practitioner.defaultLocation` currently points to full SDL
   `PracticeLocation`, while the REST directory projection allows `{id, name}`
   only.
2. `Practice.practitioners(activeOnly: Boolean = true): [Practitioner!]!`
   currently has no pagination arguments, while the REST route contract uses
   `activeOnly`, `limit=50`, maximum `200`, and `offset=0`.

This is a static proposal only. It does not change the SDL, add GraphQL runtime
dependencies, add GraphQL resolvers, add REST routes, add Pydantic runtime
schemas, add shared read services, add database queries, joins, indexes,
migrations, provider calls, Access AI invocation, RAG, GraphRAG, runtime FGA
clients, external patient clients, broad historical diary trove access, audit
writes, or write authority.

## Gate Verdict

| Gate item | Sprint 231 value |
|---|---|
| `sdl_resolution_proposal_defined` | `true` |
| `practice_location_brief_recommended` | `true` |
| `offset_pagination_args_recommended` | `true` |
| `bare_list_return_preserved_for_first_slice` | `true` |
| `connection_or_wrapper_rejected_for_first_slice` | `true` |
| `current_default_location_drift_still_present` | `true` |
| `current_pagination_drift_still_present` | `true` |
| `sdl_changes_authorized` | `false` |
| `runtime_code_authorized` | `false` |
| `rest_route_ready` | `false` |
| `graphql_resolver_ready` | `false` |
| `external_read_model_runtime_ready` | `false` |
| `readiness_snapshot_decision` | `blocked` |
| `pause_required_before_sdl_or_runtime_code` | `true` |
| `explicit_yuri_go_no_go_required` | `true` |

Acceptance of this proposal is not approval to edit the SDL or add runtime
code.

## Current SDL Facts

The current non-runtime SDL remains unchanged:

- `schema { query: Query }` has no `Mutation`;
- `Practice.practitioners(activeOnly: Boolean = true): [Practitioner!]!`;
- `Practitioner.defaultLocation: PracticeLocation`;
- `PracticeLocation` fields are `id`, `name`, `displayOrder`, and `active`;
- there is no `PracticeLocationBrief`;
- there is no `PractitionerListResult`;
- there is no `PractitionerConnection`;
- there are no `limit`, `offset`, `first`, `after`, `last`, or `before`
  arguments on `Practice.practitioners`.

Those facts are expected until Yuri explicitly approves an SDL-resolution sprint.

## Proposed DefaultLocation Resolution

Future SDL should introduce a practitioner-directory-specific brief type:

```graphql
"Display-safe location reference for practitioner directory read shapes."
type PracticeLocationBrief {
  id: ID!
  name: String!
}

type Practitioner {
  id: ID!
  displayName: String!
  roleLabel: String
  active: Boolean!
  defaultLocation: PracticeLocationBrief
}
```

Rationale:

- it makes `{id, name}` directory minimality a type-level guarantee;
- it prevents `displayOrder` and `active` from being selectable through
  practitioner-directory `defaultLocation`;
- it mirrors REST `PractitionerDefaultLocationOut`;
- it leaves full `PracticeLocation` untouched for diary, room, roster,
  appointment, and scheduling contexts where `displayOrder` and `active` remain
  meaningful;
- it preserves the canonical five-field practitioner projection from Sprint 229.

Rejected alternatives:

- keeping `defaultLocation: PracticeLocation` and asking the resolver to hide
  fields, because GraphQL clients can still select non-null `displayOrder` and
  `active`;
- narrowing full `PracticeLocation`, because it is reused by diary and
  appointment read shapes outside the practitioner directory;
- using directives/deprecation only, because that leaves the drift selectable.

## Proposed Pagination Resolution

Future SDL should add explicit offset pagination arguments that match the REST
contract:

```graphql
type Practice {
  practitioners(
    activeOnly: Boolean = true
    limit: Int = 50
    offset: Int = 0
  ): [Practitioner!]!
}
```

Argument contract:

| Argument | Type | Default | Bounds | Rule |
|---|---|---|---|---|
| `activeOnly` | `Boolean` | `true` | boolean | `false` requires `Admin` or `PracticeOwner` |
| `limit` | `Int` | `50` | `1..200` | same cap as REST |
| `offset` | `Int` | `0` | `>=0` | same offset as REST |

Rationale:

- it mirrors REST `activeOnly`, `limit`, and `offset` exactly;
- it avoids a resolver-only translation layer;
- it keeps the future GraphQL facade a thin facade over the shared read service;
- it exposes the cap to clients rather than relying on silent server truncation;
- it keeps the first slice consistent with the Sprint 227 bare
  `list[PractitionerOut]` REST response.

Rejected alternatives:

- `PractitionerListResult { items, totalCount, hasMore }`, because it introduces
  a GraphQL-only response envelope that no longer mirrors the first REST route's
  bare-list response;
- Relay-style `PractitionerConnection`, because cursor encoding is unnecessary
  for this small, practice-scoped directory and would add a GraphQL-only
  translation layer before any consumer requires it;
- a server-capped list with no args, because it can silently truncate clients
  and does not resolve the Sprint 229 pagination drift.

If a future consumer genuinely needs `totalCount` or cursor semantics, that
should be a separate reviewed GraphQL evolution after the first REST route and
shared read service are implemented and stable.

## GraphQL Error And Pagination Semantics

The future resolver must use the existing REST/GraphQL error taxonomy:

| Scenario | GraphQL outcome |
|---|---|
| unauthenticated or inactive viewer | `UNAUTHENTICATED` |
| `activeOnly=false` without `Admin` or `PracticeOwner` | `FORBIDDEN` |
| `limit < 1` | `BAD_USER_INPUT` |
| `limit > 200` | `BAD_USER_INPUT` |
| `offset < 0` | `BAD_USER_INPUT` |
| empty authorized practice | `[]` |
| cross-practice practitioners | silently absent through tenancy filter |
| inactive or other-practice default location | `defaultLocation: null` |
| raw SQL errors | never exposed |

Ordering remains identical to REST:

1. `Practitioner.last_name` ascending
2. `Practitioner.first_name` ascending
3. `Practitioner.id` ascending

Global GraphQL depth/cost and alias limits remain future runtime requirements
from Sprint 228. They are not implemented by this proposal.

## Relationship To Prior Contracts

| Prior contract | Relationship |
|---|---|
| Sprint 227 REST proposal | Proposed `limit`, `offset`, `activeOnly`, empty-list behaviour, and `{id, name}` default-location shape mirror REST. |
| Sprint 228 GraphQL resolver ownership plan | Sequencing remains REST route -> shared read service -> SDL/resolver; GraphQL remains a facade, not the first database path. |
| Sprint 229 drift contract | Sprint 266 implemented this proposal in the non-runtime SDL artifact, resolving both former drift findings while keeping resolver/runtime gates closed. |
| Sprint 230 security/audit preflight | Authn/authz, tenancy, anti-enumeration, no audit write, and no-write/no-provider posture are unchanged. |

## Required Future Runtime/SDL Tests

Sprint 266 implemented the SDL portion of this proposal. Runtime resolver work
must still add execution tests proving:

1. `PracticeLocationBrief` exists and has exactly `id` and `name`;
2. `Practitioner.defaultLocation` points to `PracticeLocationBrief`;
3. full `PracticeLocation` remains available for diary/appointment contexts;
4. `Practice.practitioners` includes `activeOnly`, `limit`, and `offset`;
5. `limit` defaults to `50` and rejects values outside `1..200`;
6. `offset` defaults to `0` and rejects negative values;
7. `activeOnly=false` returns `FORBIDDEN` without `Admin` or `PracticeOwner`;
8. empty authorized practices return an empty list;
9. other-practice practitioners remain silently absent;
10. inactive or other-practice default locations return `null`;
11. ordering matches REST `last_name`, `first_name`, `id`;
12. no GraphQL mutations are introduced.

## Static Proposal Tests

Sprint 231 is guarded by static tests that parse markdown, SDL, JSON, and source
text only. They must not import or execute GraphQL runtime code, FastAPI route
code, database sessions, read services, providers, Access AI, RAG, GraphRAG, or
H15/H-series material.

Required static checks:

1. `test_sdl_resolution_gate_verdict_keeps_runtime_blocked`
2. `test_current_sdl_default_location_is_aligned`
3. `test_current_sdl_pagination_is_aligned`
4. `test_proposal_recommends_practice_location_brief`
5. `test_proposal_recommends_offset_pagination_args_matching_rest`
6. `test_proposal_rejects_wrapper_and_connection_for_first_slice`
7. `test_error_and_pagination_semantics_documented`
8. `test_relationship_to_prior_contracts_documented`
9. `test_future_runtime_sdl_tests_are_listed`
10. `test_current_code_has_sdl_and_rest_slice_but_no_graphql_resolver_changes`
11. `test_readiness_snapshot_remains_blocked`
12. `test_closed_gates_preserved`
13. `test_boundary_says_proposal_is_not_runtime_or_production_readiness`

## Gates Still Closed

This packet does not authorize:

- adding `PractitionerListResult` or `PractitionerConnection`;
- adding GraphQL resolvers or GraphQL mutations;
- adding a GraphQL runtime dependency or server;
- adding GraphQL runtime database queries, joins, indexes, migrations, read
  services, or query services outside the existing shared REST read service;
- adding audit writes or audit migrations;
- adding rate-limiting middleware;
- adding field-encryption code;
- adding RLS migrations or policies;
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

This is a static SDL resolution proposal. It proves only that the two current
SDL drift findings have a reviewed preferred future shape. It does not prove
runtime REST authorization, GraphQL authorization, resolver correctness, route
correctness, database query correctness, field-level authorization, audit
implementation, SDL correctness after edit, RLS, field encryption, rate
limiting, pagination performance, deployment readiness, provider readiness,
external directory readiness, patient-facing client readiness, or production
readiness.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_practitioner_directory_sdl_resolution_proposal.py -q
```
