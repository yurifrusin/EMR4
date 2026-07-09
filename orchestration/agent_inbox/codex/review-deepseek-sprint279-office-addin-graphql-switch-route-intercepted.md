# DeepSeek Review - Sprint 279 Office Add-in GraphQL Switch Route-Intercepted Evidence

Reviewer: DeepSeek worker  
Date: 2026-07-09  
Verdict: PASS

## Findings

- The committed runtime file keeps `const ENABLE_GRAPHQL_PRACTITIONERS = false;`
  in `docs/diary/diary.js`.
- No runtime `true` variant or override mechanism exists through localStorage,
  query parameters, Office settings, or server config.
- The enabled path is exercised only through a test-harness-served copy of
  `diary.js` in `review/test_diary_graphql_practitioner_switch.py`.
- The evidence JSON/Markdown labels the proof as route-intercepted and not live
  backend evidence.
- The evidence covers default-off REST only, `FORBIDDEN`, `BAD_USER_INPUT`,
  transport failure, `practice: null`, and `defaultLocation: null`.
- Sensitive canary fields are included in intercepted test data and asserted
  absent from rendered page text.
- All `must_remain_false` gates stay false: deployment, production,
  external-client, write/audit-write, provider, memory/RAG/GraphRAG,
  H15/H-series, historical diary/trove, mutation/subscription, telemetry,
  schema expansion, default-on, and live GraphQL traffic.
- The evidence schema test cross-checks the JSON test list, the review test
  file, and the runtime source file.

## Recommendation

Sprint 279 can close. Moving the selector default-on still requires a separate
approval packet and must not be inferred from this route-intercepted evidence.
