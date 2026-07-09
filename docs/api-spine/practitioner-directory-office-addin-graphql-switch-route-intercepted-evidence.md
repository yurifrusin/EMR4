# Practitioner Directory Office Add-in GraphQL Switch Route-Intercepted Evidence

Sprint 279 records route-intercepted browser evidence for the Office add-in
practitioner selector GraphQL switch.

The runtime source remains default-off:

```javascript
const ENABLE_GRAPHQL_PRACTITIONERS = false;
```

## Evidence

Browser evidence lives in `review/test_diary_graphql_practitioner_switch.py`.

It proves:

- default-off runtime makes no GraphQL request and uses
  `GET /api/v1/practice/practitioners?activeOnly=true&limit=200`;
- default-off selector rows still come from the REST practitioner directory;
- sensitive practitioner canary fields are not rendered into the page;
- an enabled GraphQL path, exercised only through a test-harness-served copy of
  `diary.js`, posts the approved `Query.practice.practitioners` variables and
  falls back to REST for `FORBIDDEN`;
- the same enabled test-harness path falls back to REST for `BAD_USER_INPUT`;
- the same enabled test-harness path falls back once to REST for GraphQL
  transport failure;
- `practice: null` returns an empty GraphQL result without REST fallback;
- `defaultLocation: null` preserves the practitioner row without REST fallback.

This is route-intercepted evidence, not live backend evidence.

## Boundary

This sprint does not flip the runtime default, add a user override, add
telemetry, create deployment readiness, create production readiness, expose an
external patient client, grant write authority, add audit writes, connect
providers or memory/RAG/GraphRAG, import H15/H-series or historical diary
material, add GraphQL mutations, add GraphQL subscriptions, or expand the
approved practitioner projection.

GraphQL remains read-only. REST/OpenAPI command authority remains unchanged.

## Follow-On

Moving this selector default-on requires a separate approval packet. Until then,
`ENABLE_GRAPHQL_PRACTITIONERS` must remain false in committed runtime source.
