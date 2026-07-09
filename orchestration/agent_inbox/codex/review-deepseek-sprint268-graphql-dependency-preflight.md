# DeepSeek Review - Sprint 268 GraphQL Dependency Preflight

Status: PASS

Reviewer lane: DeepSeek Worker Shen the 5th

Scope reviewed:

- `strawberry-graphql[fastapi]==0.320.3`
- Local `.venv` install/import behavior
- Compatibility with current FastAPI, Pydantic, SQLAlchemy, and Python runtime
- Security/dependency risks before Sprint 269 runtime shell work

Findings:

- `strawberry-graphql[fastapi]==0.320.3` is viable for the approved first
  GraphQL runtime surface.
- `strawberry.fastapi.GraphQLRouter` imports successfully.
- Transitives observed locally are `graphql-core==3.2.11` and
  `cross-web==0.7.0`; no dependency conflicts were found by `pip check`.
- `QueryDepthLimiter`, `MaxAliasesLimiter`, `MaxTokensLimiter`, and
  `DisableIntrospection` are available for the later runtime shell.
- Strawberry fits the FastAPI/Pydantic-v2 code style better than Ariadne or
  Graphene for this first code-first runtime slice.

Security note:

- The review found no new vulnerability introduced by the Strawberry dependency
  pin.
- Two pre-existing unrelated audit findings were noted: `ecdsa 0.19.2
  PYSEC-2026-1325` and `pytest 8.4.2 PYSEC-2026-1845`.

Recommendations:

- Keep the resolver thin over `list_practitioner_directory`.
- Mount `/api/v1/graphql` through a separate GraphQL router module, not by
  adding substantial logic directly to `app/main.py`.
- Use `QueryDepthLimiter(max_depth=6)` and
  `MaxAliasesLimiter(max_alias_count=500)` in the runtime shell.
- Use the existing bearer-token/current-user model for GraphQL context; do not
  add a second token parser.

Verdict:

PASS. Sprint 268 may pin the dependency. Endpoint, schema runtime, and resolver
code remain Sprint 269+ work.
