# Practitioner Directory Office Add-in GraphQL Consumer Switch Approval Packet

Sprint 277 prepares the approval packet for a future Office add-in taskpane
switch to `Query.practice.practitioners`. It is not approval and it does not
change runtime code.

Decision: `pending_yuri_switch_approval`.

## What Approval Would Allow

If Yuri approves this packet later, the next sprint may edit only the Office
add-in practitioner selector path to add a default-off GraphQL fetch wrapper for
`Query.practice.practitioners`.

The switch is internal staff only, practice-scoped, and limited to:

- `id`;
- `displayName`;
- `roleLabel`;
- `active`;
- `defaultLocation { id name }`.

No backend route, GraphQL schema, telemetry endpoint, readiness flag, deployment
claim, production claim, external patient-client, write/audit-write path,
provider, memory/RAG/GraphRAG, H15/H-series, historical diary/trove path,
mutation, subscription, or field expansion is approved.

## Gate Mechanism

The approved implementation, if later authorized, must use a source-controlled
build-time constant or equivalent static taskpane config that defaults false.
Runtime user overrides are forbidden: no `localStorage`, query parameter, Office
settings persistence, hidden toggle, or unreviewed server config endpoint.

If the gate is disabled or expired, the taskpane must make zero GraphQL fetches
and render from the existing REST path.

The proposed switch approval consumes the existing release runway and expires on
2026-08-06.

## Fallback And Errors

- HTTP `401`: logout and do not retry GraphQL.
- HTTP non-401, timeout, or connection failure: fall back to REST once and show
  safe system retry copy.
- GraphQL `FORBIDDEN`: no logout, show access-denied copy, fall back to REST
  once.
- GraphQL `BAD_USER_INPUT`: no logout, show invalid-request copy, fall back to
  REST once.
- `practice = null`: distinct no-access empty state, not the same as an empty
  practitioners list.
- `defaultLocation = null`: keep the row and render an empty location shape.
- malformed required row fields: drop the malformed row and continue if any
  valid rows remain.

## Stop Point

Yuri must explicitly approve the payload before any taskpane GraphQL
implementation sprint starts.
