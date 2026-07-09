# Antigravity Sprint 278 Office Add-in GraphQL Switch Runtime Review

Verdict: PASS.

Antigravity reviewed the implementation direction for the approved default-off
internal Office add-in practitioner selector GraphQL switch. The actual approved
consumer is the diary surface in `docs/diary/diary.js`.

Integrated guardrails:

- Silent REST fallback when the GraphQL path is disabled or fails.
- Backend-derived `displayName` is rendered directly.
- `defaultLocation = null` is safe and does not crash the selector.
- The dropdown keeps deterministic backend ordering by consuming returned rows
  in order.
- The source must assert `ENABLE_GRAPHQL_PRACTITIONERS = false`.
- No runtime override through query parameters or local storage.
- No live values, latency, throughput, deployment, production, or readiness
  claims.
