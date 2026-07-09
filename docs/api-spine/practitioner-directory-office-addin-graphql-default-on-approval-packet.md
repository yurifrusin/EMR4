# Practitioner Directory Office Add-in GraphQL Default-On Approval Packet

Sprint 280 prepares a default-on decision packet for the Office add-in diary
practitioner selector. It is not approval and it does not change runtime code.

Decision:
`pending_yuri_approval_for_office_addin_graphql_practitioner_selector_default_on`.

## Current State

Sprint 278 implemented the switch as default-off:

```javascript
const ENABLE_GRAPHQL_PRACTITIONERS = false;
```

Sprint 279 added route-intercepted browser evidence for:

- default-off REST-only behavior with zero GraphQL requests;
- enabled GraphQL fallback to REST for `FORBIDDEN`, `BAD_USER_INPUT`, and
  transport failure;
- `practice: null` empty/no-fallback behavior;
- `defaultLocation: null` row preservation;
- sensitive practitioner canary fields absent from rendered page text.

## What Later Approval Would Allow

Only after Yuri explicitly approves this packet, a later sprint may change the
single Office add-in diary practitioner selector gate so the GraphQL path is the
default render source for authenticated internal staff.

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

This packet does not approve runtime code changes, live/default-on Office add-in
GraphQL traffic, deployment readiness, production readiness, external patient
clients, write authority, audit writes, provider calls, memory/RAG/GraphRAG,
H15/H-series or historical diary/trove access, GraphQL mutations, GraphQL
subscriptions, telemetry endpoints, server-config flag endpoints, runtime user
overrides, or field expansion.

## Stop Point

Stop for Yuri approval before changing
`ENABLE_GRAPHQL_PRACTITIONERS` to `true` or sending Office add-in GraphQL
traffic by default.
