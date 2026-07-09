# Practitioner Directory Readiness Criteria

Date: 2026-07-09

Sprint: 255

Decision: `criteria_defined_readiness_not_approved`.

This packet defines what would be required before the practitioner-directory
REST first slice could change `rest_route_ready` from `false` to `true`.

It does not approve that change.

## Target

- Route: `GET /api/v1/practice/practitioners`
- Current readiness flag: `rest_route_ready=false`
- Approved readiness value after this packet: `false`

## Required Before `rest_route_ready=true`

- Runtime test matrix passes in an isolated run.
- API-spine artifact tests pass.
- OpenAPI/consumer contract snapshot matches the runtime route.
- Authn/authz/tenancy, anti-enumeration, sensitive-field exclusion,
  pagination, and error semantics are current.
- Rate-limit posture is either implemented or explicitly deferred for this
  internal read route.
- Deployment surface is named.
- PostgreSQL RLS or an RLS-equivalent gap is recorded.
- Field-encryption gap is recorded.
- External patient-client exposure remains blocked or is separately decided.
- A separate Yuri approval payload exists with reviewer, contract commit,
  expiry date, and all non-REST-slice scope fields false.

## Still Closed Even If This Route Becomes Ready

Changing `rest_route_ready` for this route must not imply GraphQL readiness,
external read-model runtime readiness, provider readiness, memory/RAG/GraphRAG
readiness, write authority, deployment readiness, production readiness, or
external patient-client readiness.

The next safe sprint is an OpenAPI/consumer contract check. It should inspect
the real FastAPI route shape and response schema without changing readiness
flags.
