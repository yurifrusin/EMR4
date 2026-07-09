# Practitioner Directory Office Add-in GraphQL Default-On Approval Packet

Sprint 280 prepared a default-on decision packet for the Office add-in diary
practitioner selector. Yuri approved that packet on 2026-07-09 with:
"I approve the default-on packet."

Decision:
`approved_for_office_addin_graphql_practitioner_selector_default_on`.

## Current State

Sprint 281 may change the single source-controlled gate from default-off to
default-on:

```javascript
const ENABLE_GRAPHQL_PRACTITIONERS = true;
```

Sprint 279 added route-intercepted browser evidence for:

- default-off REST-only behavior with zero GraphQL requests;
- enabled GraphQL fallback to REST for `FORBIDDEN`, `BAD_USER_INPUT`, and
  transport failure;
- `practice: null` empty/no-fallback behavior;
- `defaultLocation: null` row preservation;
- sensitive practitioner canary fields absent from rendered page text.

## What Later Approval Would Allow

The approved Sprint 281 runtime change may make the GraphQL path the default
render source for authenticated internal staff for this one selector.

The approved consumer would remain:
`office_addin_diary_booking_practitioner_selector`.

The approved GraphQL projection would remain:

- `id`;
- `displayName`;
- `roleLabel`;
- `active`;
- `defaultLocation { id name }`.

The existing REST fallback route must remain:
`GET /api/v1/practice/practitioners?activeOnly=true&limit=200`.

## Not Approved

This packet does not approve deployment readiness, production readiness,
external patient clients, write authority, audit writes, provider calls,
memory/RAG/GraphRAG, H15/H-series or historical diary/trove access, GraphQL
mutations, GraphQL subscriptions, telemetry endpoints, server-config flag
endpoints, runtime user overrides, or field expansion.

## Stop Point

Stop before any expansion beyond this one selector. REST fallback must remain.
