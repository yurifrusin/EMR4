# Practitioner Directory Office Add-in GraphQL Default-On Rollback Packet

Sprint 284 prepares the rollback path for the already default-on Office add-in
practitioner selector GraphQL switch. It does not roll the feature back now.

## Current State

`docs/diary/diary.js` remains default-on for exactly one consumer:
`office_addin_diary_booking_practitioner_selector`.

The existing REST practitioner-directory route remains retained as the fallback
path, and no runtime user override or server config endpoint exists.

## Rollback Action

If rollback is required, the bounded action is one line in `docs/diary/diary.js`:

```javascript
const ENABLE_GRAPHQL_PRACTITIONERS = false;
```

The rollback must not delete the GraphQL query, remove the REST fallback,
unmount `/api/v1/graphql`, remove `Query.practice.practitioners`, change backend
auth/error behavior, or claim broader readiness.

After applying the one-line rollback, use rollback-specific validation rather
than the current default-on baseline suites. The current static runtime tests
correctly assert `ENABLE_GRAPHQL_PRACTITIONERS = true` and would need to be
updated or excluded if the rollback is actually applied.

## Triggers

Appropriate triggers include selector-blocking GraphQL failures, GraphQL-specific
logout loops, sensitive-field exposure, fallback failure, practice-scope leakage,
inactive-practitioner leakage, or material performance regression attributed to
the GraphQL selector path.

## Boundary

This packet does not claim deployment readiness, production readiness, global
GraphQL readiness, telemetry readiness, external-client readiness, write or
audit-write authority, provider or memory/RAG/GraphRAG readiness, H15/H-series
or historical diary/trove access, GraphQL mutations, GraphQL subscriptions, or
field expansion.
