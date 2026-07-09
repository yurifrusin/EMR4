# DeepSeek Review - Sprint 270 GraphQL Practitioners Resolver

Verdict: PASS.

The DeepSeek sidecar reviewed the proposed implementation of only
`Query.practice.practitioners(activeOnly, limit, offset)` on the mounted
Strawberry runtime. The review confirmed the approval chain from Sprints 267-269
and the narrow resolver contract: use
`list_practitioner_directory`, no REST-router import, no independent SQLAlchemy
query, no provider/memory/RAG/GraphRAG/H15/trove access, no writes or audit
writes, and no mutation/subscription/deployment/production/external-client
readiness claim.

Integrated cautions:

- Catch the shared read service's `HTTPException(403)` and expose GraphQL
  `FORBIDDEN`, not a raw FastAPI exception.
- Validate `limit` and `offset` in GraphQL because REST `Query(...)` validation
  does not apply.
- Convert UUIDs to `strawberry.ID` strings.
- Implement `Query.practice(id:)` as a viewer-practice context and return
  `null` for a mismatched practice ID without querying or leaking the other
  practice.
- Keep all other GraphQL fields and adjacent gates closed.

