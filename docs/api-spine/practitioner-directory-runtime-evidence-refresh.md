# Practitioner Directory Runtime Evidence Refresh

Date: 2026-07-09

Sprint: 254

Decision: `runtime_evidence_refreshed_readiness_blocked`.

This packet refreshes evidence for the already implemented practitioner
directory REST first slice:

`GET /api/v1/practice/practitioners`

It does not change route code, schemas, services, readiness flags, SDL, GraphQL,
providers, Access AI, memory/RAG/GraphRAG, H15/H-series runtime imports,
historical diary runtime imports, external patient-client exposure, or write
authority.

## Evidence Surface

- Router: `app/routers/practice.py`
- Schema: `app/schemas/practice.py`
- Read service: `app/services/practice/practitioner_directory_read.py`
- Runtime tests: `tests/test_practitioner_directory_route.py`
- Post-implementation review:
  `docs/api-spine/practitioner-directory-post-implementation-readiness-review.json`
- Approved gate:
  `docs/api-spine/practitioner-directory-approved-gate.json`

The runtime evidence covers authentication, inactive-user denial, role coverage,
same-practice scoping, anti-enumeration, inactive inclusion restricted to Admin
or PracticeOwner, sensitive-field exclusion, default-location scoping,
deterministic ordering, pagination bounds, empty-practice behavior, no
practitioner detail route, no appointment/audit write, no idempotency key
requirement for this read, no provider/Access AI/RAG/GraphRAG imports, no
H15/H-series/historical diary imports, and no readiness snapshot change.

## Readiness Boundary

The route remains implemented but not readiness-approved. The following remain
false: `rest_route_ready`, `graphql_resolver_ready`,
`external_read_model_runtime_ready`, `runtime_or_memory_ready`,
`provider_or_directory_runtime_ready`, `write_authority_ready`,
`deployment_ready`, and `production_ready`.

The next safe sprint is a readiness criteria packet, not a readiness-flag flip.
