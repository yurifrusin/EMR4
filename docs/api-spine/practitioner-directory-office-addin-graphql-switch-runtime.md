# Practitioner Directory Office Add-in GraphQL Switch Runtime

Sprint 278 implements the approved Office add-in practitioner selector GraphQL
switch in `docs/diary/diary.js`.

The switch is default-off:

```javascript
const ENABLE_GRAPHQL_PRACTITIONERS = false;
```

With that value, the diary surface uses the existing REST route:

```text
GET /api/v1/practice/practitioners?activeOnly=true&limit=200
```

The GraphQL path is present only behind the source-controlled constant and uses
the approved projection for `Query.practice.practitioners`. There is no
`localStorage`, query-parameter, Office settings, server-config, or hidden user
override.

The implementation adds no backend route, schema change, telemetry endpoint,
write/audit write, provider, memory/RAG/GraphRAG, H15/H-series, historical
diary/trove path, mutation, subscription, deployment claim, production claim,
external-client exposure, readiness promotion, or field expansion.

Next evidence should be route-intercepted browser coverage for default-off REST
behavior and the enabled-path fallback shape.
