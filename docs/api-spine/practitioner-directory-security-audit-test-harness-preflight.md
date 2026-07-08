# Practitioner Directory Security/Audit Test Harness Preflight

Date: 2026-07-08

Sprint: 230

## Purpose

This packet defines the static security and audit test-harness preflight for the
future REST read route:

- `GET /api/v1/practice/practitioners`

It follows:

- `docs/api-spine/practitioner-directory-first-runtime-implementation-proposal.md`
- `docs/api-spine/practitioner-directory-graphql-resolver-ownership-plan.md`
- `docs/api-spine/practitioner-directory-rest-graphql-drift-contract.md`
- `docs/api-spine/security/permission-matrix.yaml`
- `orchestration/api_spine_adr.md`

This is a static preflight only. It does not add a REST route, GraphQL resolver,
GraphQL runtime dependency, SDL change, Pydantic runtime schema, shared read
service, database query, join, index, migration, provider call, Access AI
invocation, RAG, GraphRAG, runtime FGA client, external patient client, broad
historical diary trove access, audit write, or write authority.

## Gate Verdict

| Gate item | Sprint 230 value |
|---|---|
| `security_audit_preflight_defined` | `true` |
| `authn_contract_defined` | `true` |
| `authz_contract_defined` | `true` |
| `tenancy_anti_enumeration_contract_defined` | `true` |
| `read_audit_posture_defined` | `true` |
| `future_rls_field_encryption_rate_limit_posture_defined` | `true` |
| `no_write_no_provider_contract_defined` | `true` |
| `runtime_code_authorized` | `false` |
| `rest_route_ready` | `false` |
| `graphql_resolver_ready` | `false` |
| `external_read_model_runtime_ready` | `false` |
| `readiness_snapshot_decision` | `blocked` |
| `pause_required_before_route_or_resolver_code` | `true` |
| `explicit_yuri_go_no_go_required` | `true` |

Acceptance of this preflight is not approval to add route, resolver, schema,
read-service, database, audit, GraphQL runtime, provider, or migration code.

## Authentication Contract

The future route must use the existing auth dependency path:

- `app/dependencies.py::oauth2_scheme`
- `OAuth2PasswordBearer`
- `app/dependencies.py::get_current_user`
- `app/services/auth_service.py::verify_token`

Required future behaviours:

| Scenario | Future response |
|---|---|
| missing `Authorization` header | `401` |
| invalid token | `401` |
| expired token | `401` |
| inactive user | `401` |
| anonymous/public client | no access |

The route must not accept anonymous access, API-key bypass, request-body
practice scope, or client-supplied tenant scope.

## Authorization Contract

The default practitioner directory list is a same-practice operational read.
The future route may allow all authenticated runtime `UserRole` values to read
active practitioners:

- `GP`
- `Receptionist`
- `Nurse`
- `Admin`
- `PracticeOwner`

Inactive inclusion is privileged:

- `activeOnly=false` requires `Admin` or `PracticeOwner`;
- insufficient role returns `403`;
- unknown or unmapped roles fail closed;
- agent and integration principals do not gain human directory-list authority
  by implication.

The static permission matrix is prototype-only and default-deny. If its
lowercase role names drift from runtime `UserRole` names, runtime implementation
must canonicalize on the runtime enum or explicitly update the fixture in a
reviewed sprint. This preflight does not change the permission matrix.

## Tenancy And Anti-Enumeration Contract

The future route is a list route only.

Required rules:

1. Every query filters `Practitioner.practice_id == current_user.practice_id`.
2. Practice scope comes only from the authenticated current user.
3. No `GET /api/v1/practice/practitioners/{id}` detail route is authorized in
   the first slice.
4. Other-practice practitioners are silently absent through the practice filter.
5. Error messages must not reveal whether another-practice practitioner exists.
6. The default-location join filters same-practice active locations only:
   `PracticeLocation.practice_id == current_user.practice_id` and
   `PracticeLocation.is_active == true`.
7. Patient, appointment, roster, schedule, billing, result, reminder, message,
   SMS, clinical-note, and raw diary data are outside the directory contract.

## Read Audit Posture

The practitioner directory is a read-only operational directory. It must not
write appointment audit rows or command audit rows.

Current posture:

- `AppointmentAuditLog` exists for appointment command/write evidence.
- `Access AI` audit exists for AI invocation metadata.
- No general practitioner-directory read-audit table is authorized here.

Future posture:

- no `AppointmentAuditLog` write for `GET /api/v1/practice/practitioners`;
- no `Idempotency-Key` header required for this GET route;
- no staff-confirmation or confirmation payload;
- no row-level clinical read audit for this display-safe directory;
- if a future general read-audit foundation is approved, it may record only
  aggregate metadata such as actor, practice, action, count, parameters, and
  correlation id;
- audit/log metadata must never include provider numbers, prescriber numbers,
  AHPRA numbers, HPI-I, email, phone, address, location contact details, raw
  SQLAlchemy model dumps, or provider/model payloads.

Correlation id continuity is useful for tracing, but adding or enforcing an
`X-Correlation-Id` runtime middleware is not authorized by this preflight.

## Future Defensive Posture

These items remain future/gated. They are documented so the first route does not
over-claim production readiness:

| Concern | Sprint 230 posture |
|---|---|
| PostgreSQL RLS | not implemented here; RLS or an RLS-equivalent milestone remains required before external patient clients or live-provider production scope |
| field-level encryption | not implemented here; regulated practitioner identifiers remain excluded from the directory projection and encryption remains a separate ADR/workstream |
| rate limiting | not implemented here; future shared middleware required before patient-facing or broad external exposure |
| runtime FGA / OpenFGA / Auth0 | blocked; `docs/access-ai-enterprise-auth-fga-boundary.md` remains static design only |
| external patient clients | blocked pending authentication, anti-enumeration, RLS/RLS-equivalent, CORS/CSRF, privacy impact, and patient identity review |

## No-Write / No-Provider Assertions

The future implementation must prove:

- no `db.add`;
- no `db.commit`;
- no `db.flush`;
- no `db.delete`;
- no ORM mutation;
- no database migration;
- no provider call;
- no Access AI invocation;
- no RAG;
- no GraphRAG;
- no memory runtime wiring;
- no H15/H-series runtime import;
- no historical diary trove import;
- no practice-knowledge authority;
- no external patient client;
- no runtime FGA client;
- no practitioner create/update/delete/onboarding command.

These are future runtime tests after explicit approval. Sprint 230 only defines
the static preflight and confirms no such runtime surface exists today.

## Required Future Runtime Tests

When Yuri explicitly approves route implementation, the runtime PR must include
tests for:

1. `test_unauthenticated_request_returns_401`
2. `test_invalid_token_returns_401`
3. `test_inactive_user_denied`
4. `test_all_authenticated_roles_can_read_active_directory`
5. `test_active_only_false_requires_admin_or_practice_owner`
6. `test_unknown_or_unmapped_role_fails_closed`
7. `test_practice_scoping_excludes_other_practice_practitioners`
8. `test_no_practitioner_detail_route_or_idor_surface`
9. `test_no_cross_practice_existence_leak`
10. `test_default_location_same_practice_active_only`
11. `test_response_excludes_sensitive_fields`
12. `test_read_does_not_create_appointment_audit_log`
13. `test_read_does_not_require_idempotency_key`
14. `test_read_does_not_write_database_state`
15. `test_read_does_not_call_provider_access_ai_rag_graphrag`

## Static Preflight Tests

This sprint is guarded by static tests that parse markdown, YAML, JSON, and
selected source text only. They must not import or execute a FastAPI app,
GraphQL runtime, database session, read service, provider, Access AI, RAG,
GraphRAG, or H15/H-series material.

Required static checks:

1. `test_security_preflight_gate_verdict_keeps_runtime_blocked`
2. `test_authn_contract_uses_existing_oauth2_and_get_current_user`
3. `test_authn_dependency_filters_inactive_users`
4. `test_authz_roles_and_inactive_admin_gate_documented`
5. `test_tenancy_and_anti_enumeration_contract_defined`
6. `test_read_audit_posture_excludes_appointment_audit_writes`
7. `test_future_rls_field_encryption_rate_limit_posture_documented`
8. `test_no_write_no_provider_assertions_documented`
9. `test_required_future_runtime_tests_are_listed`
10. `test_current_code_has_no_route_schema_service_or_resolver`
11. `test_readiness_snapshot_remains_blocked`
12. `test_closed_gates_preserved`
13. `test_boundary_says_preflight_is_not_runtime_or_production_readiness`

## Gates Still Closed

This packet does not authorize:

- adding a REST practitioner directory route;
- adding GraphQL resolvers or GraphQL mutations;
- adding a GraphQL runtime dependency or server;
- changing the SDL;
- adding Pydantic runtime schemas;
- adding `app/services/practice/` or a practitioner directory read service;
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

This is a static security/audit test-harness preflight. It proves only that the
future practitioner directory route has reviewed authn/authz, tenancy,
anti-enumeration, read-audit, future defensive posture, and no-write/no-provider
test requirements. It does not prove runtime REST authorization, GraphQL
authorization, resolver correctness, route correctness, database query
correctness, field-level authorization, audit implementation, RLS, field
encryption, rate limiting, pagination performance, deployment readiness,
provider readiness, external directory readiness, patient-facing client
readiness, or production readiness.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_practitioner_directory_security_audit_preflight.py -q
```
