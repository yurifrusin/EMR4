# Review - Sprint 197 Auth-Gating Metadata

| Field | Value |
|---|---|
| Agent | Claude |
| Branch | `claude/current` |
| Kind | Bounded backend-readiness review |
| Scope | Static auth-gating metadata for documented Diary write surfaces |

## Verdict

Proceed with a static test over mounted `APIRoute` dependency metadata. The
current route-contract tests prove paths and methods exist, but do not prove
documented write surfaces are authenticated.

## Recommended Signal

- Use `fastapi.dependencies.utils.get_flat_dependant(route.dependant)`.
- Assert the flattened dependency graph contains `app.dependencies.get_current_user`.
- For write surfaces, also assert a `require_role.<locals>.checker` dependency
  is present.
- Iterate by mounted `(path, method)` row, not path-only, because some paths
  have multiple handlers.

## Boundary

No `TestClient`, HTTP requests, route handler execution, database sessions,
provider calls, memory/RAG/GraphRAG, H15/H-series runtime imports, GraphQL
mutation, or writes are needed.
