# Practitioner Directory First-Runtime Implementation Proposal Gate

Date: 2026-07-08

Sprint: 227

## Purpose

This packet resolves the first-route implementation proposal for the external
read-model surface:

- `GET /api/v1/practice/practitioners`
- future GraphQL read shape `Query.practice.practitioners(activeOnly: Boolean = true)`

It is a gate packet, not implementation approval. It does not add a REST route,
GraphQL resolver, GraphQL mutation, Pydantic runtime schema, database query,
migration, provider call, Access AI invocation, RAG, GraphRAG, runtime FGA
client, external patient client, broad historical diary trove access, or write
authority.

## Inputs Reviewed

| Input | Required posture |
|---|---|
| `docs/api-spine/practitioner-directory-read-shape-design.md` | static design only |
| `docs/api-spine/practitioner-directory-route-schema-ownership-candidate.md` | `candidate_only` and `evidence_only` rows only |
| `docs/api-spine/external-read-model-ownership-consolidation-preflight.md` | recommends `practice_practitioners` as first go/no-go candidate |
| `docs/api-spine/external-read-model-implementation-planning-review.md` | implementation planning is blocked until reviewed |
| `docs/api-spine/external-read-model-combined-readiness-review.md` | combined readiness remains `blocked` |
| `docs/api-spine/external-read-model-readiness-dag.json` | external read-model readiness DAG remains blocked |
| `tests/fixtures/api_spine_external_readiness/blocked_readiness_status.json` | `dag_decision: blocked`; readiness flags false |
| Claude Sprint 227 worker review | CLI worker hand-in; review only |
| Antigravity Sprint 227 worker review | CLI worker hand-in; review only |
| DeepSeek Sprint 227 worker review | direct Codex worker hand-in; review only |

## Gate Verdict

| Gate item | Sprint 227 value |
|---|---|
| `first_candidate` | `practice_practitioners` |
| `implementation_proposal_ready_for_yuri_review` | `true` |
| `runtime_code_authorized` | `false` |
| `rest_route_ready` | `false` |
| `graphql_resolver_ready` | `false` |
| `external_read_model_runtime_ready` | `false` |
| `readiness_snapshot_decision` | `blocked` |
| `pause_required_before_route_code` | `true` |
| `explicit_yuri_go_no_go_required` | `true` |

Implementation of route, schema, query, or router mount code may begin only
after Yuri explicitly gives a go/no-go for this first runtime route. Approval of
this document itself is not approval to write runtime code.

## Preflight Checks

Any implementation sprint must re-run these checks before code:

1. `blocked_readiness_status.json` still has `dag_decision: blocked`,
   `rest_route_ready: false`, `graphql_resolver_ready: false`, and
   `external_read_model_runtime_ready: false`.
2. `docs/api-spine/practitioner-directory-route-schema-ownership-candidate.md`
   still has no `approved` or `implemented` ownership rows.
3. No router declares `@router.get("/practice/practitioners"`,
   `@router.get("/practitioners"`, `def list_practitioners`, or
   `def get_practitioners`.
4. No schema declares `class PractitionerOut` or
   `class PractitionerDirectory`.
5. No GraphQL resolver or query wiring exists for
   `Query.practice.practitioners`.
6. The implementation sprint has Yuri's explicit go/no-go recorded in the
   sprint closeout before route/schema/query code is written.

If any preflight fails, the sprint engine must stop the route-code attempt and
report the drift.

## Accepted Route Contract For Future Code

| Item | Contract |
|---|---|
| Router module | new `app/routers/practice.py` |
| Router prefix | `/api/v1/practice` |
| Route | `GET /practitioners` |
| Full path | `GET /api/v1/practice/practitioners` |
| Router mount | `app/main.py` includes `practice.router` after auth/database dependencies are available |
| Auth dependency | existing `get_current_user` pattern |
| Database dependency | existing request-scoped SQLAlchemy session pattern |
| Practice scoping | every query filters `Practitioner.practice_id == current_user.practice_id` |
| Response type | bare `list[PractitionerOut]` |
| Empty state | `200` plus `[]` |
| Invalid auth | existing `401` behaviour |
| Cross-practice data | silently absent through practice filter; never `403` with leaked existence |

This route is a read-only directory surface. It is not a diary context route,
appointment route, practitioner onboarding route, roster route, or provider
lookup route.

## Accepted Schema Contract For Future Code

Future code may add `app/schemas/practice.py::PractitionerOut` only after the
explicit go/no-go. The response schema is intentionally smaller than diary
schemas and must not reuse `app/schemas/appointments.py::PractitionerBrief` or
a full diary/location schema that leaks identifiers or contact details.

| Field | Type | Source | Rule |
|---|---|---|---|
| `id` | `UUID` | `Practitioner.id` | practice-scoped direct field |
| `displayName` | `str` | `Practitioner.first_name` plus `Practitioner.last_name` | join non-empty name parts server-side |
| `roleLabel` | `string or null` | `Practitioner.specialty` | display label only |
| `active` | `bool` | `Practitioner.is_active` | renamed display field |
| `defaultLocation` | `PractitionerDefaultLocationOut or null` | `Practitioner.default_location_id` plus `PracticeLocation` | `{id, name}` only, same-practice and active only |

`PractitionerDefaultLocationOut` must be a new display-safe nested schema with
only `id` and `name`. It must not expose location address, phone, email,
provider identifiers, internal metadata, or broad location configuration.

## Sensitive Field Exclusions

`PractitionerOut` and `PractitionerDefaultLocationOut` must never expose:

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

The implementation test suite must assert forbidden response keys, not merely
rely on visual review.

## Query Parameters And Policy

| Parameter | Future contract |
|---|---|
| `activeOnly` | `bool`, default `true`, alias preserved as camelCase |
| `limit` | `int`, default `50`, `ge=1`, `le=200` |
| `offset` | `int`, default `0`, `ge=0` |

Default ordering must be deterministic:

1. `Practitioner.last_name` ascending
2. `Practitioner.first_name` ascending
3. `Practitioner.id` ascending

Inactive inclusion policy: `activeOnly=false` is admin-only. A caller without
`Admin` or `PracticeOwner` authority must receive `403` rather than an inactive
directory. If the current role model cannot enforce that cleanly when the route
is implemented, the implementation must keep inactive inclusion unavailable and
return `403` for `activeOnly=false` until a reviewed role gate exists.

## Default Location Join Policy

The first implementation may include `defaultLocation`, but only as a
display-safe nested `{id, name}` object.

The join must be a same-practice active-location join:

- `PracticeLocation.id == Practitioner.default_location_id`
- `PracticeLocation.practice_id == current_user.practice_id`
- `PracticeLocation.is_active == true`

If the location is absent, inactive, or from another practice, the response must
return `defaultLocation: null`. It must not expose location address, phone,
email, billing details, availability internals, or raw location models.

## Required Runtime Tests Before Code Is Accepted

Future route code must arrive with deterministic tests covering:

1. `test_auth_denial_returns_401`
2. `test_invalid_token_returns_401`
3. `test_practice_scoping_never_returns_other_practice_practitioners`
4. `test_active_only_default_excludes_inactive_practitioners`
5. `test_active_only_false_requires_admin_or_practice_owner`
6. `test_display_name_derivation_joins_non_empty_name_parts`
7. `test_response_excludes_sensitive_practitioner_fields`
8. `test_default_location_same_practice_active_only`
9. `test_inactive_or_other_practice_default_location_returns_null`
10. `test_deterministic_ordering_by_last_first_id`
11. `test_limit_default_and_maximum`
12. `test_invalid_limit_and_offset_return_422`
13. `test_empty_practice_returns_200_empty_list`
14. `test_get_route_does_not_write_database_state`
15. `test_route_does_not_call_provider_access_ai_rag_or_graphrag`

## GraphQL Boundary

This proposal does not authorize GraphQL resolver implementation.

`Query.practice.practitioners` remains a future read-model resolver candidate.
A separate GraphQL implementation proposal must define resolver ownership,
authorization, cost/depth posture, field-level sensitivity, and the relationship
between the REST read route and GraphQL facade before any resolver code is
written. GraphQL mutations remain prohibited.

## Gates Still Closed

This packet does not authorize:

- adding a REST practitioner directory route;
- adding GraphQL resolvers or GraphQL mutations;
- adding Pydantic runtime schemas;
- adding database queries, joins, indexes, migrations, or query services;
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

This is a static implementation-proposal gate packet. It proves only that the
first practitioner-directory runtime route has a reviewed contract ready for
Yuri's explicit go/no-go. It does not prove runtime REST authorization,
database query correctness, GraphQL resolver implementation, field-level
authorization, pagination performance, deployment readiness, provider readiness,
external directory readiness, patient-facing client readiness, or production
readiness.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_practitioner_directory_implementation_proposal.py -q
```
