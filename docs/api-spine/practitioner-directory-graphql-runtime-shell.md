# Practitioner Directory GraphQL Runtime Shell

Sprint 269 mounts the first GraphQL runtime shell at `/api/v1/graphql`.

This is deliberately smaller than the approved Sprint 268-272 block: it proves
the Strawberry runtime can sit inside the FastAPI app with the existing EMR4
auth dependency and basic query guards, but it does not implement
`Query.practice.practitioners`.

## Runtime Surface

- Dependency: `strawberry-graphql[fastapi]==0.320.3`.
- Router: `app/graphql/router.py`.
- Schema: `app/graphql/schema.py`.
- Context: `app/graphql/context.py`.
- Endpoint: `/api/v1/graphql`.
- Current query field: `graphqlHealth`.
- Mutations and subscriptions: absent.

`graphqlHealth` exists only because Strawberry requires at least one query
field. It returns authenticated shell status and is not a practitioner-directory
read model.

## Auth And Guards

The context getter reuses `app.dependencies.get_current_user` and
`app.dependencies.get_db`, so the shell does not add a second token parser or a
parallel user lookup path. Missing or invalid bearer tokens fail before query
execution with the existing HTTP 401 behavior.

The shell configures:

- `QueryDepthLimiter(max_depth=6)`.
- `MaxAliasesLimiter(max_alias_count=500)`.
- `MaxTokensLimiter(max_token_count=500)`.

Strawberry `0.320.3` exposes depth, alias, and token limiters, but not a native
field-cost estimator extension. Sprint 269 therefore records the gate's
`500` posture as a token-budget guard for the shell, with custom cost estimation
deferred until it is actually needed by richer GraphQL fields.

## Closed Boundaries

No `Practice` GraphQL type, `practitioners` field, practitioner resolver module,
REST-router import, provider call, memory/RAG/GraphRAG path, H15/H-series/trove
path, write path, audit write, deployment readiness, production readiness, or
external-client readiness is opened by this sprint.

## Verification

Sprint 269 adds
`tests/test_practitioner_directory_graphql_runtime_shell.py` and updates the
Sprint 267/268 guards so they now assert the runtime shell exists while
`Query.practice.practitioners` still does not.

Next allowed step: Sprint 270 can add the `Query.practice.practitioners` schema
types and resolver against `list_practitioner_directory`, with the same
closed-gate posture for everything outside that field.

