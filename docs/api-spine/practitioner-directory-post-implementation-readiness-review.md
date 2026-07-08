# Practitioner Directory Post-Implementation Readiness Review

Date: 2026-07-08

Sprint: 235

Status: bounded REST slice reviewed; readiness remains blocked.

## Decision

The approved practitioner-directory REST first slice is implemented at commit
`5b3b9102` and has runtime test evidence for the bounded route:

`GET /api/v1/practice/practitioners`

This review records that implementation evidence, but it does **not** change
the API-spine readiness snapshot. `rest_route_ready`,
`graphql_resolver_ready`, `external_read_model_runtime_ready`,
`runtime_or_memory_ready`, and `write_authority_ready` remain `false`.

## Evidence Surface

Implemented files:

- `app/routers/practice.py`
- `app/schemas/practice.py`
- `app/services/practice/practitioner_directory_read.py`
- `tests/test_practitioner_directory_route.py`

The runtime tests cover:

- authenticated access and inactive-user denial;
- same-practice scoping and anti-enumeration through absence;
- active-only default filtering;
- `activeOnly=false` restricted to `Admin` and `PracticeOwner`;
- sensitive practitioner identifiers and contact fields excluded;
- default-location projection scoped to same-practice active locations only;
- deterministic `last_name`, `first_name`, `id` ordering;
- pagination bounds;
- no practitioner detail route;
- no appointment/audit writes;
- no idempotency key requirement for the read route;
- no provider, Access AI, RAG, GraphRAG, H15/H-series, historical diary, or
  `local_data` imports.

## Readiness Boundary

This packet is a post-implementation review, not a deployment or production
readiness approval.

Still blocked pending separate review:

- changing `rest_route_ready` to `true`;
- adding SDL or GraphQL resolver coverage for `Query.practice.practitioners`;
- adding provider, Access AI, memory, RAG, or GraphRAG wiring;
- adding H15, H-series, historical diary, or `local_data` runtime imports;
- adding write authority, audit writes, or appointment mutation behavior;
- claiming deployment, production, external patient-client, rate-limit, RLS, or
  field-encryption readiness.

## Strategic Position

This sits in Programme 2G / EMR4 API Spine as a post-implementation guardrail
review after the first external read-model REST slice. The sprint size is kept
small because the implementation already exists; the remaining decision is
whether the bounded route evidence is enough to change any readiness gate. It
is not.

The next safe practitioner-directory step is a separate readiness/deployment or
GraphQL/SDL review sprint, not an automatic scope expansion.
