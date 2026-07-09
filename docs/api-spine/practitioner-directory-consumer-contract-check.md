# Practitioner Directory Consumer Contract Check

Date: 2026-07-09

Sprint: 256

Decision: `consumer_contract_checked_readiness_blocked`.

This check introspects the FastAPI OpenAPI schema for
`GET /api/v1/practice/practitioners` and records the consumer-facing contract
without changing route code or readiness flags.

## Contract

- Method/path: `GET /api/v1/practice/practitioners`
- Security: declared in OpenAPI.
- Query parameters:
  - `activeOnly`: boolean, default `true`
  - `limit`: integer, default `50`, minimum `1`, maximum `200`
  - `offset`: integer, default `0`, minimum `0`
- Response: `200` returns an array of `PractitionerOut`.
- `PractitionerOut` fields: `id`, `displayName`, `roleLabel`, `active`,
  `defaultLocation`.
- `defaultLocation` fields: `id`, `name`.
- Sensitive practitioner fields are absent.
- No practitioner detail route is present.

## Boundary

This is an OpenAPI/consumer contract check only. It does not approve GraphQL
delivery, provider/Access AI/memory/RAG/GraphRAG wiring, external patient-client
exposure, deployment readiness, production readiness, write authority, or any
readiness flag change.
