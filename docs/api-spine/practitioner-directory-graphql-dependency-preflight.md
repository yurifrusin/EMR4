# Practitioner Directory GraphQL Dependency Preflight

Sprint 268 pins the approved GraphQL runtime dependency for the first EMR4
GraphQL surface.

Dependency:

- `strawberry-graphql[fastapi]==0.320.3`

Observed local install:

- `pip check`: no broken requirements
- `strawberry-graphql`: `0.320.3`
- `graphql-core`: `3.2.11`
- `cross-web`: `0.7.0`
- `from strawberry.fastapi import GraphQLRouter`: passed
- `QueryDepthLimiter`, `MaxAliasesLimiter`, and `DisableIntrospection`:
  available for the later runtime shell.

DeepSeek dependency/security review returned PASS. It noted two pre-existing
unrelated audit findings, `ecdsa 0.19.2 PYSEC-2026-1325` and
`pytest 8.4.2 PYSEC-2026-1845`; neither is introduced by this dependency.

This follows the Sprint 267 gate packet. It does not mount `/api/v1/graphql`,
add schema runtime code, add resolver code, or change readiness flags.

Next allowed step: Sprint 269 may add a minimal GraphQL runtime shell without
the practitioner resolver, keeping mutations, providers, memory, H15/trove,
writes, deployment, and production gates closed.
