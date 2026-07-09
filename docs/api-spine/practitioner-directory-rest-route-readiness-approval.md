# Practitioner Directory REST Route Readiness Approval

Date: 2026-07-09

Decision:
`approved_for_practitioner_directory_rest_route_ready_true`.

Yuri explicitly authorized a separate `rest_route_ready=true` approval payload
for `GET /api/v1/practice/practitioners` only.

## Scope

This approval applies only to the authenticated internal-staff read route:

`GET /api/v1/practice/practitioners`

Approved route scope:

- read-only;
- practice-scoped;
- paginated;
- authenticated internal staff only;
- response excludes practitioner provider numbers, prescriber numbers, AHPRA
  numbers, HPI-I values, and other sensitive implementation fields.

## Criteria Evidence

Sprint 255 required a separate approval payload before any
`rest_route_ready=true` decision. Sprint 258 closed the remaining blocker
evidence:

- isolated runtime route test pass;
- API-spine artifact test pass;
- OpenAPI/consumer contract evidence;
- authn/authz and tenancy evidence;
- anti-enumeration and pagination evidence;
- sensitive-field exclusion evidence;
- deferred internal-route rate-limit decision;
- deployment surface naming without deployment readiness;
- PostgreSQL RLS gap record;
- field-encryption gap record;
- internal-staff-only external-client scope decision.

This document and its JSON payload satisfy the final criterion: the separate
Yuri approval payload exists.

## Not Authorized

This approval does not authorize:

- GraphQL SDL or resolver readiness;
- external read-model runtime readiness beyond this one REST route;
- Access AI, provider, memory, RAG, or GraphRAG wiring;
- H15, H-series, historical diary, or `local_data` runtime import;
- practitioner create, update, delete, or write authority;
- external patient-client exposure;
- deployment or production readiness;
- model-to-database writes.

The following gates must remain false: `graphql_resolver_ready`,
`external_read_model_runtime_ready`, `runtime_or_memory_ready`,
`provider_or_directory_runtime_ready`, `write_authority_ready`,
`deployment_ready`, `production_ready`, and
`external_patient_client_ready`.

## Residual Risks Accepted For This Route Only

Route-specific rate limiting remains deferred for this authenticated
internal-staff read route. The accepted risk is limited to this route posture
and must be revisited before any external or public exposure.

PostgreSQL RLS remains a recorded gap. The current route relies on
application-layer practice scoping and tests; that is not equivalent to
database-level RLS.

Field-level encryption remains a recorded gap for stored practitioner
identifiers. The response schema excludes those identifiers, but API schema
exclusion does not mitigate database-storage exposure.

## Fixture Posture

This payload records approval. It does not itself update the external read-model
readiness snapshot or any runtime code. A follow-up bounded sprint may update
only route-specific readiness evidence if tests prove all adjacent gates remain
false.
