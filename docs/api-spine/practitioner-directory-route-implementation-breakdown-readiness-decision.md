# Practitioner Directory Route Implementation Breakdown Readiness Decision

Date: 2026-07-08

Sprint: 232

## Purpose

This packet converts the practitioner-directory planning chain from Sprints
227-231 into a concrete future implementation breakdown for:

- `GET /api/v1/practice/practitioners`

It is a readiness decision packet, not implementation approval. It does not add
a REST route, GraphQL resolver, GraphQL mutation, GraphQL runtime dependency,
SDL change, Pydantic runtime schema, shared read service, database query, join,
index, migration, provider call, Access AI invocation, RAG, GraphRAG, runtime
FGA client, external patient client, H15/H-series runtime import, broad
historical diary trove access, audit write, readiness-flag change, or write
authority.

The route-code sprint remains blocked until Yuri explicitly gives a go/no-go for
the first REST route.

## Inputs Reviewed

| Input | Sprint | Role |
|---|---:|---|
| `practitioner-directory-read-shape-design.md` | 214 | source/model/read-shape evidence |
| `practitioner-directory-route-schema-ownership-candidate.md` | 223 | route/schema ownership candidate |
| `practitioner-directory-first-runtime-implementation-proposal.md` | 227 | accepted REST route and schema contract |
| `practitioner-directory-graphql-resolver-ownership-plan.md` | 228 | REST-first then shared-read-service then GraphQL sequencing |
| `practitioner-directory-rest-graphql-drift-contract.md` | 229 | canonical projection and known blocked drift |
| `practitioner-directory-security-audit-test-harness-preflight.md` | 230 | authn/authz, tenancy, anti-enumeration, audit/no-write/no-provider contract |
| `practitioner-directory-sdl-pagination-default-location-resolution-proposal.md` | 231 | future SDL convergence for `PracticeLocationBrief` and pagination args |
| `blocked_readiness_status.json` | 221+ | current blocked external read-model readiness snapshot |
| Claude Sprint 232 review | 232 | REST-first task slicing and stop/go points |
| Antigravity Sprint 232 review | 232 | consumer sequencing, location fallback, and SDL/GraphQL gate separation |
| DeepSeek Sprint 232 review | 232 | implementation checklist, risks, and route/test decomposition |

## Gate Verdict

| Gate item | Sprint 232 value |
|---|---|
| `route_breakdown_defined` | `true` |
| `future_rest_route_slice_defined` | `true` |
| `future_read_service_slice_defined` | `true` |
| `future_schema_slice_defined` | `true` |
| `future_runtime_test_matrix_defined` | `true` |
| `rest_route_ready` | `false` |
| `graphql_resolver_ready` | `false` |
| `external_read_model_runtime_ready` | `false` |
| `runtime_code_authorized` | `false` |
| `sdl_changes_authorized` | `false` |
| `readiness_snapshot_decision` | `blocked` |
| `pause_required_before_route_code` | `true` |
| `separate_pause_required_before_sdl_code` | `true` |
| `separate_pause_required_before_graphql_code` | `true` |
| `explicit_yuri_go_no_go_required` | `true` |

Acceptance of this packet is not approval to write route, schema, service,
database, SDL, resolver, provider, or readiness code.

## Pre-Code Readiness Checklist

Before any runtime code is written, a route implementation sprint must prove:

1. Yuri has explicitly approved the Sprint 227 first REST route go/no-go in the
   current sprint closeout.
2. `blocked_readiness_status.json` still has `dag_decision: blocked`,
   `rest_route_ready: false`, `graphql_resolver_ready: false`, and
   `external_read_model_runtime_ready: false`.
3. `docs/api-spine/practitioner-directory-route-schema-ownership-candidate.md`
   still has candidate/evidence posture only and no `approved` or `implemented`
   ownership rows.
4. The only approved router surface is `@router.get("/practitioners"` inside
   the `/api/v1/practice` router; there is no
   `@router.get("/practice/practitioners"` duplicate and no detail route.
5. The only approved schema objects are `class PractitionerOut` and
   `class PractitionerDefaultLocationOut`; there is no
   `class PractitionerDirectory`.
6. The only approved production service path is
   `app/services/practice/practitioner_directory_read.py`.
7. No current GraphQL runtime dependency, resolver, or query wiring exists for
   `Query.practice.practitioners`.
8. The Sprint 229 drift items still remain known and blocked until the separate
   SDL/GraphQL gates open.
9. Claude, Antigravity, and DeepSeek worker invocation modes, worktree
   cleanliness, current DeepSeek lane count, reuse/cleanup plan, and any
   substitutions are announced before dispatch.

If any pre-code check fails, the sprint engine must stop the route-code attempt
and report the drift instead of continuing on momentum.

## Implemented REST First Slice

These slices were implemented under the approved REST first-slice gate only.
They do not open SDL, GraphQL, provider, memory, write, deployment, or readiness
gates.

### Slice A - Directory Response Schemas

Implemented file: `app/schemas/practice.py`

Allowed objects after explicit go/no-go:

```python
class PractitionerDefaultLocationOut(BaseModel):
    id: uuid.UUID
    name: str


class PractitionerOut(BaseModel):
    id: uuid.UUID
    displayName: str
    roleLabel: str | None = None
    active: bool
    defaultLocation: PractitionerDefaultLocationOut | None = None
```

Rules:

- define explicit fields only;
- do not reuse `app/schemas/appointments.py::PractitionerBrief`;
- do not serialize raw SQLAlchemy models;
- expose `Practitioner.is_active` only as `active`;
- expose `Practitioner.specialty` only as `roleLabel`;
- expose default location only as `{id, name}`;
- never expose `provider_number`, `prescriber_number`, `ahpra_number`, `hpi_i`,
  `practice_id`, `created_at`, `email`, `phone`, `address`, `password_hash`,
  `credentials`, `schedule_overrides`, `schedules`, `appointments`, clinical
  logs, roster internals, location contact details, or raw model dumps.
- the forbidden-field test must assert the literal categories `clinical logs`,
  `roster internals`, `location contact details`, and `raw model dumps` remain
  absent from response payload keys and schema fields.

### Slice B - Shared Read Service

Implemented file: `app/services/practice/practitioner_directory_read.py`

The service is the sole data path for the REST route and any later GraphQL
facade. It must own:

- `Practitioner.practice_id == current_user.practice_id`;
- `activeOnly=true` as the default filter;
- `activeOnly=false` restricted to `Admin` or `PracticeOwner`, otherwise `403`;
- `limit=50`, `ge=1`, `le=200`;
- `offset=0`, `ge=0`;
- deterministic ordering by `Practitioner.last_name`,
  `Practitioner.first_name`, and `Practitioner.id`;
- display-name derivation from non-empty trimmed name parts;
- role-label derivation from `Practitioner.specialty`;
- same-practice active default-location join:
  `PracticeLocation.id == Practitioner.default_location_id`,
  `PracticeLocation.practice_id == current_user.practice_id`, and
  `PracticeLocation.is_active == true`;
- `defaultLocation: null` when the location is absent, inactive, or outside the
  user's practice;
- no `db.add`;
- no `db.commit`;
- no `db.flush`;
- no `db.delete`;
- no ORM mutation;
- no audit write;
- no provider call;
- no Access AI invocation;
- no RAG;
- no GraphRAG;
- no memory wiring;
- no H15/H-series import;
- no historical diary trove import;
- no runtime FGA client;
- no external patient client;
- no model-to-database write.

### Slice C - REST Route And Mount

Implemented file: `app/routers/practice.py`

Future route:

- router prefix: `/api/v1/practice`;
- route: `GET /practitioners`;
- full path: `GET /api/v1/practice/practitioners`;
- dependencies: existing `get_current_user` and request-scoped database session
  pattern;
- query params: `activeOnly: bool = true`, `limit: int = 50`,
  `offset: int = 0`;
- response: bare `list[PractitionerOut]`;
- empty authorized practice: `200 []`;
- missing, invalid, expired, or inactive authenticated user: existing `401`
  behavior;
- cross-practice data: silently absent through the practice filter;
- no `GET /api/v1/practice/practitioners/{id}` detail route.

Mounting the router in `app/main.py` is part of the implemented REST slice
under the explicit go/no-go.

### Slice D - Runtime Test Matrix

The route implementation arrived with tests before merge. The union of Sprint
227 and Sprint 230 requirements was de-duplicated into a single runtime suite
proving:

1. `test_auth_denial_returns_401`
2. `test_invalid_token_returns_401`
3. `test_inactive_user_denied`
4. `test_all_authenticated_roles_can_read_active_directory`
5. `test_active_only_default_excludes_inactive_practitioners`
6. `test_active_only_false_requires_admin_or_practice_owner`
7. `test_unknown_or_unmapped_role_fails_closed`
8. `test_practice_scoping_never_returns_other_practice_practitioners`
9. `test_no_practitioner_detail_route_or_idor_surface`
10. `test_no_cross_practice_existence_leak`
11. `test_display_name_derivation_joins_non_empty_name_parts`
12. `test_response_excludes_sensitive_practitioner_fields`
13. `test_default_location_same_practice_active_only`
14. `test_inactive_or_other_practice_default_location_returns_null`
15. `test_deterministic_ordering_by_last_first_id`
16. `test_limit_default_and_maximum`
17. `test_invalid_limit_and_offset_return_422`
18. `test_empty_practice_returns_200_empty_list`
19. `test_read_does_not_create_appointment_audit_log`
20. `test_read_does_not_require_idempotency_key`
21. `test_get_route_does_not_write_database_state`
22. `test_route_does_not_call_provider_access_ai_rag_or_graphrag`
23. `test_route_does_not_import_h15_h_series_or_historical_diary_material`
24. `test_route_does_not_change_readiness_snapshot`

## Deferred Gates

### Separate SDL Gate

Sprint 231 defines the preferred future SDL shape:

- add `PracticeLocationBrief { id, name }`;
- change `Practitioner.defaultLocation` to `PracticeLocationBrief`;
- add `activeOnly`, `limit=50`, and `offset=0` to
  `Practice.practitioners`;
- preserve the bare `[Practitioner!]!` first-slice return;
- reject `PractitionerListResult` and `PractitionerConnection` for the first
  slice.

These changes require a separate pause and explicit approval. They are not part
of the first REST route implementation.

### Separate GraphQL Runtime Gate

Sprint 228 sequencing remains binding:

1. REST route;
2. shared read service;
3. SDL alignment;
4. GraphQL resolver.

GraphQL must not query the database independently. The future resolver must be a
thin facade over the shared read service and must not add mutations, provider
calls, external service calls, audit writes, memory/RAG/GraphRAG, Access AI,
H15/H-series imports, broad trove access, or write authority.

### Separate Readiness Snapshot Gate

The blocked readiness snapshot must not be changed by the first REST route
implementation. Any future change from `rest_route_ready: false` to `true` needs
a distinct reviewed readiness update after implementation evidence exists.

## Stop / Go Points

| Checkpoint | Required outcome | If not true |
|---|---|---|
| Pre-code | explicit Yuri go/no-go for REST route | stop, keep planning only |
| Pre-code | readiness snapshot remains blocked/false | stop and report drift |
| Pre-code | no existing route/schema/service/resolver | stop and report drift |
| Pre-code | Sprint 229 drift items still blocked | stop and report drift |
| Implementation | schema exposes only five canonical fields | remove leak before merge |
| Implementation | inactive inclusion restricted to `Admin`/`PracticeOwner` | return `403` until role gate is reviewed |
| Implementation | tests prove no writes/provider/memory/trove imports | fix before merge |
| Pre-merge | no SDL, GraphQL runtime, resolver, readiness, provider, or memory changes | revert unrelated gate-opening edits |
| Post-merge | closeout records route evidence without claiming production readiness | correct closeout wording |

## API Consumer Notes

Future UI or API clients should treat this as an authenticated internal
practice-directory read:

- initial request: `GET /api/v1/practice/practitioners?activeOnly=true&limit=50&offset=0`;
- render `displayName` directly instead of reconstructing names client-side;
- display a neutral fallback when `defaultLocation` is `null`;
- show inactive-practitioner controls only for users known to have admin/owner
  authority;
- treat `403` on `activeOnly=false` as a normal permission failure;
- do not infer other-practice existence from empty lists or permission errors;
- do not use this route as a roster, appointment, billing, clinical, provider,
  or practitioner-onboarding API.

## Static Tests For Sprint 232

This sprint is guarded by static tests that parse markdown, JSON, SDL, and
source text only. They must not import FastAPI app code, execute database
sessions, run route handlers, add GraphQL dependencies, call providers, or read
H15/H-series/local diary material.

Required static checks:

1. `test_route_breakdown_gate_verdict_keeps_runtime_blocked`
2. `test_inputs_reviewed_cover_sprints_214_223_227_to_231`
3. `test_pre_code_readiness_checklist_requires_yuri_and_current_absence`
4. `test_future_schema_slice_is_minimal_and_sensitive_fields_excluded`
5. `test_future_read_service_slice_captures_tenancy_pagination_location_and_no_side_effects`
6. `test_future_rest_route_slice_is_explicit_but_current_code_absent`
7. `test_future_runtime_test_matrix_unifies_sprint_227_and_230_requirements`
8. `test_deferred_sdl_and_graphql_gates_remain_separate`
9. `test_stop_go_points_and_consumer_notes_are_documented`
10. `test_readiness_snapshot_remains_blocked`
11. `test_boundary_says_packet_is_not_runtime_or_production_readiness`

## Gates Still Closed

This packet does not authorize:

- adding a REST practitioner directory route;
- adding `app/routers/practice.py`;
- adding `app/schemas/practice.py`;
- adding `app/services/practice/`;
- adding `app/services/practice/practitioner_directory_read.py`;
- adding GraphQL resolvers or GraphQL mutations;
- adding a GraphQL runtime dependency or server;
- changing the SDL;
- adding `PracticeLocationBrief` to the SDL;
- changing `Practitioner.defaultLocation`;
- adding `limit` or `offset` arguments to `Practice.practitioners`;
- adding Pydantic runtime schemas;
- adding database queries, joins, indexes, migrations, read services, or query
  services;
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
- historical diary candidate builders or ignored local outputs;
- Access AI invocation wiring;
- source manifests as approved runtime configuration;
- RACGP or Cochrane content ingestion, indexing, caching, embedding, scraping,
  live lookup, or sync jobs;
- practitioner create/update/delete/onboarding commands;
- appointment, roster, schedule, diary, billing, result, reminder, message,
  SMS, or clinical write authority;
- model-to-database writes outside REST command handlers;
- raw compatibility deprecation mode changes.

## Boundary

This is a static route implementation breakdown and readiness decision packet.
It proves only that Sprints 227-231 form a coherent future implementation plan
with explicit slices, prerequisites, tests, deferred gates, stop/go points, and
consumer notes. It does not prove runtime REST authorization, route correctness,
database query correctness, field-level authorization, audit implementation,
SDL correctness after edit, GraphQL authorization, resolver correctness, RLS,
field encryption, rate limiting, pagination performance, deployment readiness,
provider readiness, external directory readiness, patient-facing client
readiness, or production readiness.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_practitioner_directory_route_breakdown_readiness_decision.py -q
```
