# DeepSeek Review - Sprint 269 GraphQL Runtime Shell

Verdict: PASS.

The DeepSeek sidecar reviewed the planned minimal Strawberry runtime shell for
`/api/v1/graphql`: query-only schema, authenticated context, depth/alias guards,
no `Query.practice.practitioners` resolver, and no provider, memory, H15/trove,
write, deployment, or production gate changes.

Integrated cautions:

- Keep a harmless placeholder query because Strawberry schemas cannot have an
  empty `Query` type.
- Supersede Sprint 267 and Sprint 268 tests that asserted no endpoint or
  Strawberry app imports existed; those were correct for their sprints but are
  obsolete once Sprint 269 mounts the shell.
- `strawberry-graphql==0.320.3` exposes `QueryDepthLimiter`,
  `MaxAliasesLimiter`, and `MaxTokensLimiter`, but no native field-cost
  estimator. Treat the Sprint 269 `500` posture as a token guard and defer a
  custom cost estimator until richer GraphQL fields need it.
- Keep `app/graphql/resolvers/` absent until the practitioner resolver sprint.
- Avoid REST-router imports, provider/memory/H15/trove access, writes, and audit
  writes in the shell modules.

Implementation response:

- Added `app/graphql/context.py`, `app/graphql/schema.py`, and
  `app/graphql/router.py`.
- Mounted `graphql_router` in `app/main.py`.
- Added shell evidence in
  `docs/api-spine/practitioner-directory-graphql-runtime-shell.{json,md}`.
- Added runtime shell tests and updated the earlier gate/preflight assertions
  to allow the shell but continue blocking the practitioner resolver.

