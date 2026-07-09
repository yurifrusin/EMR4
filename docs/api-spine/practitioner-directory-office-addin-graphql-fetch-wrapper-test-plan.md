# Practitioner Directory Office Add-in GraphQL Fetch-wrapper Test Plan

Sprint 275 defines the blocked-by-default tests required before any Office
add-in taskpane runtime switch to `Query.practice.practitioners`.

This is still a plan and guardrail sprint. It does not edit `taskpane.js`, add a
hidden flag, perform a shadow fetch, create telemetry, change backend routes or
schema, or move readiness flags. The current approval expires on 2026-08-06.

## Required Mock Cases

- mocked GraphQL success with exactly `id`, `displayName`, `roleLabel`,
  `active`, and `defaultLocation { id name }`;
- empty practitioner list;
- HTTP `401` transport failure calling the same logout path as REST;
- GraphQL `FORBIDDEN` in `extensions.code` without logout;
- GraphQL `BAD_USER_INPUT` in `extensions.code` without logout;
- `data.practice = null` returning an empty list without leaking practice
  details;
- `defaultLocation = null` preserving the row and rendering an empty location;
- projection drift when an extra field appears;
- expired or disabled gate producing zero GraphQL fetches;
- future comparison/failure posture falling back to REST.

## Copy Boundary

Future tests must assert user-safe copy only. They must not expose GraphQL
operation names, `extensions.code`, raw status strings, resolver names, endpoint
paths, SQL/database text, stack traces, or live practitioner values.

## Files Still Out of Scope

Sprint 275 must not change `EMR4 Sidebar/src/taskpane/taskpane.js`, `app/`,
dependency files, ignored local data, H15 fixtures, H-series fixtures, provider
code, memory/RAG/GraphRAG code, write paths, audit-write paths, mutations, or
subscriptions.

## Switch Gate

A later runtime switch needs a separate consumer switch approval. This test plan
only records the evidence expected before asking for that approval.
