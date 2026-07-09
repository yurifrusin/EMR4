# DeepSeek Review - Sprint 281 Office Add-in GraphQL Default-On Runtime

Reviewer: DeepSeek worker  
Date: 2026-07-09  
Verdict: PASS

## Scope

Sprint 281 applies Yuri's approval of the Sprint 280 default-on packet for one
consumer only: `office_addin_diary_booking_practitioner_selector`.

The only runtime behavior authorized is changing
`ENABLE_GRAPHQL_PRACTITIONERS` to `true` in `docs/diary/diary.js`, while
retaining REST fallback and existing HTTP 401 logout behavior.

No backend route, GraphQL schema, resolver, telemetry endpoint, deployment or
production readiness, external client, write/audit-write authority, provider,
memory/RAG/GraphRAG, H15/H-series, historical diary/trove, mutation,
subscription, server-config flag endpoint, runtime user override, or field
expansion is in scope.

## Findings

- `docs/diary/diary.js` flips only `ENABLE_GRAPHQL_PRACTITIONERS` from `false`
  to `true`.
- The Sprint 280 approval packet records Yuri's approval and authorizes only the
  one-consumer default-on runtime change.
- REST fallback is retained and HTTP 401 rethrow/logout behavior is preserved.
- `review/test_diary_graphql_practitioner_switch.py` includes
  `test_default_on_graphql_401_rethrows_without_rest_fallback_and_clears_token`,
  which intercepts GraphQL HTTP 401, proves one GraphQL request, zero REST
  fallback requests, token clearing, and the session-expired auth banner.
- The runtime evidence JSON lists the 401 test and records
  `graphql_401_rethrows_without_rest_fallback: true`.
- No backend route, schema, resolver, telemetry, deployment/production
  readiness, external client, write authority, provider, memory, H15/trove,
  mutation, subscription, server-config endpoint, runtime user override, or
  field expansion was opened.

## Recommendation

Sprint 281 can close.
