# Practitioner Directory Office Add-in GraphQL Default-On Local Backend Smoke

Sprint 283 adds a narrow non-intercepted backend smoke check after the Office
add-in practitioner selector GraphQL path became default-on.

The test extracts the committed GraphQL document from `docs/diary/diary.js` and
posts it to the local FastAPI `TestClient` `/api/v1/graphql` route with
authenticated fake staff context and local fake database rows.

## Scope

This is local backend evidence only. It proves the committed Office add-in query
shape is accepted by the local GraphQL endpoint and returns the approved
practitioner-directory projection for fake data.

The smoke check covers practice scoping, active-only filtering, default-location
projection, sensitive canary absence, and no appointment audit writes.

## Boundary

This status does not claim deployment readiness, production readiness, global
GraphQL readiness, telemetry readiness, external-client readiness, write or
audit-write authority, provider or memory/RAG/GraphRAG readiness, H15/H-series
or historical diary/trove access, GraphQL mutations, GraphQL subscriptions, or
field expansion.
