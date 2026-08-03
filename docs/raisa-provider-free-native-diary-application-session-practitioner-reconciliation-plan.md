# Raisa provider-free native-Diary practitioner reconciliation plan

Date: 2026-08-03

Status: provider-free, unmounted, browserless, authored-synthetic

Parent: `provider_free_native_diary_application_session_practitioner_runtime_pass`

## Outcome

Close the accepted runtime's remaining client-race obligation with a pure
JavaScript latest-read-wins gate. Trusted composition code supplies a positive,
monotonically increasing client lifecycle generation. Each read receives an
opaque, instance-bound ticket containing that generation and a local request
revision. The only render egress rejects results whose session was invalidated,
whose generation changed, whose request was superseded, whose ticket is foreign
or replayed, or whose fixed-read response is malformed.

The server authenticates its own session generation but does not expose that
generation in the response. This tranche therefore proves client lifecycle
suppression only. It does not claim cryptographic or server-bound generation,
HTTP/backend freshness, browser integration, a mounted route, or usability.

## Authority and owned paths

Yuri's standing two-lane authority covers this bounded descendant. The tranche
owns only this plan, its security delta, the task-local reconciler, one Node
acceptance harness and one Python regression wrapper. It does not edit
`docs/diary/**`, `app.main`, the accepted server adapter, shared authentication,
GraphQL, routes, models, migrations, API Spine artifacts, manifests, workflows,
harness settings, `docs/branding/**`, protected evidence or protected refs.

Providers/models, memory/RAG, real identity, patient/clinical/document data,
commands, writes, deployment, production, release and default-on product wiring
remain closed.

## Frozen boundary

- `sessionGeneration` is trusted freshness metadata, never authentication,
  authorization, audit or command authority.
- `beginRead()` freezes one object-identity ticket with only
  `sessionGeneration` and a monotonically increasing `requestRevision`.
- A new read supersedes the prior read. Invalidation suppresses all outstanding
  reads. A strictly higher generation starts the later lifecycle and suppresses
  every prior generation.
- `reconcileAndRender()` is the sole egress. It validates provenance, one-use
  state, active lifecycle, current generation, latest revision and the exact
  successful fixed-read shape before exposing rows to a synchronous callback.
- The ticket is consumed before callback invocation, including when that
  callback throws. The reconciler uses weak ticket identity and retains no
  response rows.
- Rejections use only the closed reasons `session_inactive`,
  `session_generation_stale`, `request_superseded`, `ticket_unknown`,
  `ticket_replayed` and `response_not_admissible`.
- Observability contains only generation/revision metadata and bounded counters.
  It contains no rows, cookies, CSRF, session/principal/practice values or raw
  authority material.

The admitted result is exactly `{status: "success", rows: [...]}`. Each row is
exactly `{id, displayName, roleLabel, active, defaultLocation}`; `roleLabel` and
`defaultLocation` may be null as allowed by the accepted GraphQL projection.
Unknown, authority-bearing or malformed fields fail closed.

## Deterministic acceptance

The Node harness exercises latest-wins ordering, late response after generation
advance, late response after a newer read, session invalidation, one-use render,
replay, forged/cross-instance tickets, invalid generation advances, malformed
and authority-bearing responses, nullable display-safe fields, callback failure
consumption, bounded observability and static dependency absence. It writes
sanitized evidence only after every case passes.

The evidence label is exactly
`provider_free_unmounted_client_state_machine`, with
`data_class=authored_synthetic`. It is explicitly not live, browser,
route-intercepted, HTTP/backend/PostgreSQL, mounted-runtime or usability
evidence.

Proposed result:
`provider_free_native_diary_application_session_practitioner_reconciliation_pass`.

## API Spine

The reconciler consumes only the already accepted fixed GraphQL read result.
It adds no query field, mutation, REST command, event actuator, manifest,
database, idempotency or audit path. Backend session authentication,
authorization and required read audit remain authoritative.

## Residual gate

Mounted/default-on native-Diary wiring and non-intercepted browser acceptance
remain later work. If that integration needs server response generation or any
shared-router/auth change, it is an architecture gate and not an extension of
this proof.
