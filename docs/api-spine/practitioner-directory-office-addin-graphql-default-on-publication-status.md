# Practitioner Directory Office Add-in GraphQL Default-On Publication Status

Sprint 282 records publication hygiene for Sprint 281.

Published runtime commit:
`d3dda16e657a4eb51b845a509c5cff071f530c43`.

Both `master` and `handoff/current` were pushed at that commit, and the
integration worktree was clean after publication.

## Scope

The default-on runtime remains limited to
`office_addin_diary_booking_practitioner_selector`.

`ENABLE_GRAPHQL_PRACTITIONERS` is true, GraphQL is attempted first for the
approved practitioner directory query, and REST fallback remains retained.

## Boundary

This status does not claim deployment readiness, production readiness, global
GraphQL readiness, telemetry readiness, external-client readiness, write or
audit-write authority, provider or memory/RAG/GraphRAG readiness, H15/H-series
or historical diary/trove access, GraphQL mutations, GraphQL subscriptions, or
field expansion.
