# Practitioner Directory GraphQL Release Boundary

Sprint 272 closes the approved Sprint 268-272 block with a scoped release
boundary for:

```graphql
Query.practice.practitioners(activeOnly: Boolean = true, limit: Int = 50, offset: Int = 0)
```

## Decision

The field is approved for internal authenticated staff consumer development and
test-harness use through 2026-08-06, against approved contract commit
`d4ed14d3`. Internal UI or integration code may compare it with the existing
REST practitioner directory while using the same staff bearer-token auth model
and the same closed-gate posture.

This is not global GraphQL readiness, not deployment readiness, not production
readiness, not external patient-client readiness, not provider readiness, not
memory/RAG readiness, not H15/trove readiness, not write authority, not mutation
readiness, and not subscription readiness.

## Consumer Constraints

- Use existing bearer-token authentication.
- Handle HTTP 401 for missing or invalid auth.
- Handle GraphQL `BAD_USER_INPUT` for invalid `limit` or `offset`.
- Handle GraphQL `FORBIDDEN` for `activeOnly=false` without Admin or
  PracticeOwner authority.
- Handle `practice(id:) = null` as the no-leak response for a mismatched
  practice ID.
- Request only `id`, `displayName`, `roleLabel`, `active`, and
  `defaultLocation { id name }`.
- Do not treat this field as an external or patient-facing API.

## Still Blocked

Rate-limit review, production introspection posture, deployment smoke,
external-client contracts, global readiness snapshot migration, mutations,
subscriptions, providers, memory/RAG/GraphRAG, H15/H-series, historical diary
trove, write authority, and audit-write authority remain blocked.

## Pitfalls

- `graphql_resolver_ready` remains `false`: the resolver exists and is tested,
  but this packet is not readiness promotion.
- No implied REST consumer approval: Sprint 263 remains the REST runtime
  consumer approval boundary.
- No field expansion: requests outside `id`, `displayName`, `roleLabel`,
  `active`, and `defaultLocation { id name }` need a separate gate.
- No production introspection: production introspection remains blocked.
- No rate-limit bypass: no per-consumer bypass is authorized.
- No mutation or subscription operations may be submitted through this boundary.
- No provider, memory/RAG/GraphRAG, H15, historical diary, or trove pathway is
  authorized.
- Reverse-chaining into another endpoint is out of scope and must be reviewed
  under that consuming endpoint's gate.
- Consumers must not couple behavior to response timing or latency.
- Approval requires an explicit expiry date and a later sunset review before any
  broader GraphQL readiness proposal.
