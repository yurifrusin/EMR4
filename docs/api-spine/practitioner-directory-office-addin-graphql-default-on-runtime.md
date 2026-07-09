# Practitioner Directory Office Add-in GraphQL Default-On Runtime

Sprint 281 applies Yuri's approval of the Sprint 280 default-on packet for one
consumer only: the Office add-in diary booking practitioner selector.

The committed runtime gate is now:

```javascript
const ENABLE_GRAPHQL_PRACTITIONERS = true;
```

The selector attempts `POST /api/v1/graphql` first for
`Query.practice.practitioners`, then retains the existing REST fallback:

```text
GET /api/v1/practice/practitioners?activeOnly=true&limit=200
```

## Evidence

Route-intercepted browser evidence remains in
`review/test_diary_graphql_practitioner_switch.py`.

It proves:

- default-on GraphQL success populates the selector without REST fallback;
- approved variables are sent: `activeOnly=true`, `limit=200`, `offset=0`;
- `FORBIDDEN`, `BAD_USER_INPUT`, and transport failure fall back to REST once;
- GraphQL HTTP `401` uses the existing logout path and does not fall back to
  REST;
- `practice: null` returns empty rows without REST fallback;
- `defaultLocation: null` preserves the practitioner row without REST fallback;
- sensitive practitioner canary fields are absent from rendered page text.

## Boundary

This sprint does not add telemetry, deployment readiness, production readiness,
external patient clients, write or audit-write authority, provider calls,
memory/RAG/GraphRAG, H15/H-series or historical diary/trove access, GraphQL
mutations, GraphQL subscriptions, server-config flag endpoints, runtime user
overrides, or field expansion.
