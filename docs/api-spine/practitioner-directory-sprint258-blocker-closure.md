# Practitioner Directory Sprint 258 Blocker Closure

Date: 2026-07-09

Sprint: 258

Decision:
`readiness_blockers_closed_except_separate_yuri_approval`.

This packet closes the Sprint 257 evidence and gap-record blockers for
`GET /api/v1/practice/practitioners`, but it does not create a Yuri approval
payload and does not change `rest_route_ready`.

## Test Pass Evidence

The route matrix was run in isolation:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_route.py -q
```

Result: `31 passed`.

The API-spine artifact suite was run in isolation:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_artifacts.py -q
```

Result: `31 passed`.

These isolated records close the Sprint 257 evidence gap caused by relying only
on test existence rather than a recorded run.

## Deferred Rate-Limit Decision

Route-specific rate limiting is deferred for this internal authenticated staff
read route. The route is already authenticated, role-gated, same-practice
scoped, read-only, paginated, and not exposed to external patient clients.

The accepted residual risk is narrow but real: a compromised or malicious
authenticated staff credential could enumerate the practitioner directory at a
high request rate without a route-specific middleware throttle. Current controls
are JWT authentication and expiry, role-gated access, same-practice filtering,
pagination bounds, structured request logging, and Cloud Run request
concurrency as a soft ceiling. Cloud Run concurrency is not per-user rate
limiting.

This deferral does not approve public or external exposure. Before any external
patient-client, public-client, production, or high-volume deployment surface is
opened, rate limiting must be reviewed again.

## Deployment Surface

Current surface:

`FastAPI backend route mounted under /api/v1/practice for authenticated internal staff clients`

Development surface:

`local uvicorn app.main:app development backend, with ngrok used only as a development tunnel for add-in access when needed`

Future approved surface after this packet:

`GCP Cloud Run FastAPI backend internal staff API deployment only`

No public patient-client deployment surface, production readiness, or
deployment readiness is approved here.

## RLS Gap

Current control:

`Practitioner.practice_id == current_user.practice_id`

The route and tests enforce application-layer tenancy filtering. PostgreSQL RLS
is not yet enabled as a database-level backstop for this read model. That gap is
now explicitly recorded as acceptable for a route-readiness approval request,
but it remains a production security follow-up.

The residual risk is that a future ORM query, raw SQL path, migration script, or
route variant could omit the `practice_id` filter and return cross-practice
practitioner data without a database-level backstop. The application-layer
filter is the current control; it is not equivalent to PostgreSQL RLS.

## Field-Encryption Gap

`PractitionerOut` excludes sensitive practitioner identifiers and tests assert
that provider number, prescriber number, AHPRA number, HPI-I, email, phone,
address, and password fields are absent from the response.

The underlying `Practitioner` model may still store `provider_number`,
`prescriber_number`, `ahpra_number`, and `hpi_i` without field-level encryption.
That gap is now explicitly recorded as acceptable for a route-readiness approval
request, because the route does not expose those fields, but it remains a
production security follow-up.

The residual risk is database-level exposure: direct database access, SQL
injection elsewhere, or a compromised database credential could expose these
identifiers in plaintext. API schema exclusion does not mitigate that storage
risk.

## External Client Scope

The route is internal-staff-only. `external_patient_client_ready` remains false.
No public client, patient client, or external integration is approved.

Any future external patient-client, kiosk, booking portal, mobile app, or public
integration exposure would require a separate go/no-go and at least:
PostgreSQL RLS or an approved RLS-equivalent control, route or shared middleware
rate limiting, external-surface CORS/CSRF review, a privacy impact assessment
for exposing practitioner role and location information, patient identity
proofing and authentication distinct from staff auth, and a separate Yuri
approval payload for external-client exposure.

## Still Missing

The separate Yuri approval payload for `rest_route_ready=true` does not exist.
That is intentional. Sprint 258 closes blocker evidence only and stops before
approval-payload creation or readiness-flag change.

The next decision is Yuri's: whether to authorize a separate
`rest_route_ready=true` approval payload for this route only.

## Closed Scope

The following remain false:

- `rest_route_ready`;
- `graphql_resolver_ready`;
- `external_read_model_runtime_ready`;
- `runtime_or_memory_ready`;
- `provider_or_directory_runtime_ready`;
- `write_authority_ready`;
- `deployment_ready`;
- `production_ready`;
- `external_patient_client_ready`.

No route, schema, read-service, SDL, GraphQL resolver, provider, Access AI,
memory/RAG/GraphRAG, H15/H-series, historical diary, external patient client,
write, deployment, or production gate changed in this sprint.
