# H15 Read-Only Explanation Preview Endpoint

Date: 2026-07-06

Sprint: H34

## Decision

H34 adds one dev-only, auth-gated preview endpoint:

`GET /api/v1/appointments/dev/h15-read-only-explanation-preview`

The endpoint returns static authored synthetic metadata describing the approved
H15 read-only explanation boundary. It is a route-level contract preview, not a
runtime historical-diary integration.

## Allowed

- Static metadata only.
- `action_name: explain_schedule`.
- `dispatch: route_read_only`.
- Explicit flags showing no slot search, candidate offering, proposal
  preparation, confirmation, or diary mutation authority.
- Existing dev-route environment gate and standard authenticated user gate.

## Still Blocked

- Importing committed H15 semantic candidate fixtures into runtime routers.
- Reading ignored `local_data` payloads.
- Calling the historical diary semantic candidate builder.
- Calling provider clients.
- Persisting memory, RAG, or GraphRAG state.
- Writing database, appointment, or audit rows.
- Treating H15-derived material as availability, roster, no-slot, proposal, or
  confirmation authority.
- Broad full-trove processing.

## Verification Contract

`tests/test_bernie_dev_fixtures.py` checks that the endpoint:

- Requires auth.
- Returns 404 outside `ENVIRONMENT=dev`.
- Returns only advisory/read-only/static boundary metadata.
- Does not write appointment or audit rows.
- Does not couple the dev router to local payloads, H15 fixture imports,
  historical-diary builder code, or provider imports.

This complements H33's route-boundary tests, which prove H15 advisory frames
remain non-authoritative in Bernie reception-context decisions.
