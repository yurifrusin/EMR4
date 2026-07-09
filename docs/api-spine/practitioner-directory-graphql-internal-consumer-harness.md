# Practitioner Directory GraphQL Internal Consumer Harness

Sprint 273 adds a test-only internal consumer harness for the approved
`Query.practice.practitioners` GraphQL field.

The harness lives under `tests/` and does not wire the Office add-in, production
UI, external clients, providers, memory/RAG/GraphRAG, H15/H-series, historical
diary/trove access, writes, mutations, or subscriptions.

It proves an internal authenticated staff consumer can handle:

- authenticated success with the approved practitioner projection;
- missing bearer auth as HTTP 401;
- GraphQL `BAD_USER_INPUT`;
- GraphQL `FORBIDDEN`;
- `practice(id:) = null` on practice mismatch;
- sensitive field rejection;
- read-only access without idempotency keys.
- null GraphQL variables for `activeOnly`, `limit`, and `offset`;
- default active filtering, maximum limit, and offset pagination;
- Admin/PracticeOwner inactive-directory access;
- practice scoping and inactive/cross-practice default-location null behavior;
- no audit-log writes;
- source-level isolation from provider, memory, H15/trove, write, mutation, and
  subscription paths.
- distinct consumer-contract helpers for HTTP auth failure and GraphQL
  `extensions.code` errors, so future internal consumers do not conflate the
  two error surfaces.

This sprint does not authorize a taskpane runtime switch. Sprint 274 should
draft the Office add-in consumer proposal with Antigravity reviewing the
consumer/UX boundary before any runtime wiring.
