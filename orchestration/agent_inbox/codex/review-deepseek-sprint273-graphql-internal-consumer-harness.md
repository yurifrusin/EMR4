# DeepSeek Review - Sprint 273 GraphQL Internal Consumer Harness

Verdict: PASS.

DeepSeek reviewed the test-only internal consumer harness for
`Query.practice.practitioners` under the Sprint 272 release-boundary approval.
The review confirmed the harness is in scope if it remains under `tests/`, does
not wire production UI, does not change the runtime schema, and does not open
providers, memory/RAG/GraphRAG, H15/trove, writes, mutations, subscriptions,
external clients, deployment, production, or global readiness.

Integrated cautions:

- Assert `FORBIDDEN` as a GraphQL error extension, not HTTP 403.
- Assert `practice(id:)` mismatch as `practice: null`, not an empty list.
- Explicitly serialize `null` variables to exercise `BAD_USER_INPUT`.
- Keep the default query to the approved field set.
- Prove no idempotency key is required.
- Add source guards against provider, memory, H15/trove, write, mutation, and
  subscription paths.
