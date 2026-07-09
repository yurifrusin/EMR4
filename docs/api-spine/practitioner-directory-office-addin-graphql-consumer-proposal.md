# Practitioner Directory Office Add-in GraphQL Consumer Proposal

Sprint 274 is a proposal-only Office add-in consumer boundary for
`Query.practice.practitioners`. It does not change `taskpane.js`, add a hidden
flag, switch runtime traffic, change backend routes, change GraphQL schema,
alter readiness flags, add telemetry, or claim deployment or production
readiness.

The existing approval expires on 2026-08-06. Any future taskpane runtime switch
proposal must reference a current release boundary or pause for renewal.

## Approved Query Shape

```graphql
query GetPractitioners($activeOnly: Boolean, $limit: Int, $offset: Int) {
  practice {
    practitioners(activeOnly: $activeOnly, limit: $limit, offset: $offset) {
      id
      displayName
      roleLabel
      active
      defaultLocation {
        id
        name
      }
    }
  }
}
```

The field ceiling is fixed: `id`, `displayName`, `roleLabel`, `active`, and
`defaultLocation { id name }`. Sensitive fields, future convenience fields, and
patient-search fields require a separate field-expansion gate.

## Consumer Model

- HTTP `401` remains the transport-layer auth failure and should use the same
  logout path as the current REST helper.
- GraphQL `extensions.code` errors are response-body errors. `FORBIDDEN` and
  `BAD_USER_INPUT` must not be treated as auth expiry or trigger logout.
- `practice(id:) = null` is the expected no-leak response for a mismatched
  practice.
- Reads do not require an idempotency key, create audit writes, invoke
  providers, or touch memory/RAG/GraphRAG/H15/trove paths.

## Comparison Boundary

The next runtime-facing work should be a developer or staging comparison plan:
REST remains the render source, GraphQL is used only for structural drift checks,
and committed evidence contains no live practitioner values, latency claims,
throughput claims, rate-limit claims, or readiness claims.

Sprint 274 deliberately keeps comparison telemetry out of the product. Before a
real switch, local browser-console-only drift reporting is the maximum posture
unless a separate non-mutating telemetry endpoint is reviewed and approved.

## User Copy Boundary

Future UI work must not display raw GraphQL errors, resolver names, SQL/database
messages, or endpoint names. User copy should remain action-oriented:

- session expiry: ask the user to sign in again;
- access failure: say the user lacks permission for the practitioner directory;
- connection/system failure: ask the user to try again later.

## Sprint 275 Gate

Before any taskpane switch is proposed, the next block should produce a
blocked-by-default fetch-wrapper test plan: mocked GraphQL success, empty list,
HTTP `401`, GraphQL `FORBIDDEN`, GraphQL `BAD_USER_INPUT`, practice-null,
projection drift, and fail-closed feature posture. Runtime traffic still needs a
separate approval.
