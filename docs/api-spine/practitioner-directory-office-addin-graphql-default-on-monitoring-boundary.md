# Practitioner Directory Office Add-in GraphQL Default-On Monitoring Boundary

Sprint 285 defines what can be watched after the Office add-in practitioner
selector GraphQL path became default-on. It does not add telemetry or claim
deployment readiness.

## Observable Today

The committed evidence currently consists of route-intercepted browser checks,
a non-intercepted local backend smoke, publication status, and a rollback
packet.

Without adding new instrumentation, operators can still watch user reports,
browser console warnings, selector-empty behavior after authentication, and
GraphQL-specific logout or fallback symptoms.

## Still Blocked

This packet keeps production observability, deployment validation, external
client policy, global GraphQL readiness, broader GraphQL security review, and
any telemetry privacy review as blockers before a readiness claim.

## Boundary

This packet does not claim deployment readiness, production readiness, global
GraphQL readiness, telemetry readiness, external-client readiness, write or
audit-write authority, provider or memory/RAG/GraphRAG readiness, H15/H-series
or historical diary/trove access, GraphQL mutations, GraphQL subscriptions, or
field expansion.
