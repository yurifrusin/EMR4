# DeepSeek Sprint 274 Office Add-in GraphQL Consumer Proposal Review

Verdict: PASS with mandatory inclusion criteria.

DeepSeek reviewed the planned Office add-in practitioner selector GraphQL
consumer proposal boundary for `Query.practice.practitioners` only. It confirmed
that the Sprint 273 harness and Sprint 272 release boundary create a clean
proposal foundation and that the taskpane currently has no GraphQL practitioner
runtime traffic.

Required guardrails integrated into Sprint 274:

- Do not conflate HTTP `401` transport auth failures with GraphQL
  `extensions.code` response-body failures. `FORBIDDEN` and `BAD_USER_INPUT`
  must not trigger logout.
- Sprint 274 must not introduce a hidden runtime switch: no `localStorage` flag,
  query parameter flag, config toggle, or shadow fetch.
- The approved projection remains fixed to `id`, `displayName`, `roleLabel`,
  `active`, and `defaultLocation { id name }`.
- Writes, audit writes, idempotency keys, mutation/subscription operations,
  provider calls, memory/RAG/GraphRAG, H15/H-series, and trove access remain
  zero.
- REST-vs-GraphQL comparison must be structural and contractual only: no
  response timing, latency, throughput, server-load, readiness, live row-count,
  or practitioner-value claims.
- Antigravity remains the separate consumer/UX review lane and must not be
  substituted by DeepSeek.
- The 2026-08-06 approval expiry must stay visible, and any later runtime switch
  proposal must reference a current release boundary.
