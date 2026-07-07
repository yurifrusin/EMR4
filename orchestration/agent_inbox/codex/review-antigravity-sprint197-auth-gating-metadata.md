# Review - Sprint 197 Auth-Gating Metadata

| Field | Value |
|---|---|
| Agent | Antigravity/Gemini |
| Branch | `antigravity/current` |
| Kind | Independent backend-readiness review |
| Scope | Static route dependency metadata only |

## Verdict

Antigravity recommended a zero-side-effect dependency-tree check over mounted
`APIRoute` metadata. The review emphasized verifying documented proposal,
confirm, and raw mutation routes without issuing requests or touching runtime
state.

## Recommendations

- Traverse FastAPI route dependency metadata for documented write surfaces.
- Detect the app auth path through `get_current_user`.
- Detect role-gating through the `require_role` checker dependency.
- Keep read routes and H15/dev surfaces outside this sprint's write-surface
  assertion.

## Gates

The check remains safe only while it is metadata-only: no handler execution, no
DB sessions, no providers, no memory/RAG/GraphRAG, no H15/H-series runtime
imports, no GraphQL mutation, and no writes.
