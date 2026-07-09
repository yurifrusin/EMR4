# Practitioner Directory GraphQL Resolver Runtime

Sprint 270 implements only the approved GraphQL read field:

```graphql
Query.practice.practitioners(activeOnly: Boolean = true, limit: Int = 50, offset: Int = 0)
```

The resolver uses the shared REST read service
`app/services/practice/practitioner_directory_read.py::list_practitioner_directory`.
It does not import the REST router and does not perform its own SQLAlchemy query.

## Runtime Shape

- `Query.practice(id: ID)` returns the current viewer's practice context when
  no ID is supplied or the supplied ID matches the viewer's practice.
- `Query.practice(id: otherPracticeId)` returns `null` without querying or
  leaking the other practice.
- `Practice.practitioners` returns the REST projection only:
  `id`, `displayName`, `roleLabel`, `active`, and
  `defaultLocation { id, name }`.
- `activeOnly=false` is still restricted to `Admin` and `PracticeOwner`.
- `limit` is bounded to `1..200`; `offset` must be `>=0`.

## Error Shape

- Missing or invalid bearer token keeps the existing HTTP 401 auth behavior.
- Invalid `limit` or `offset` raises GraphQL `BAD_USER_INPUT`.
- Unauthorized inactive-directory reads raise GraphQL `FORBIDDEN`.
- Unexpected resolver failures raise GraphQL `INTERNAL_ERROR` without raw stack
  traces or SQL detail.

## Closed Boundaries

Sprint 270 opens only `Query.practice.practitioners`. It does not open GraphQL
mutations, subscriptions, external patient-client use, deployment readiness,
production readiness, write authority, audit writes, provider/Access AI,
memory/RAG/GraphRAG, H15/H-series, historical diary, or trove access.

