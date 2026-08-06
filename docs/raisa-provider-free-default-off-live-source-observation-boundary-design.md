# Provider-free default-off live-source observation boundary design

Date: 2026-08-06

Status: frozen architecture-only design

## Boundary classification

This design defines the authority membrane around a future async/event
observer. It does not build the observer. A committed change notice is a
patient-free control signal saying only that previously assembled context may
be stale. GraphQL remains a read graph, REST/OpenAPI remains the command plane
and the accepted temporal and fresh-generation protocols retain ownership of
invalidation and replacement context.

The observer is not truth. The database/read model remains truth; the
observation proves only that a separately authorised current read may now be
required.

## Authority graph

`LiveSourceObservationPolicy` is declarative input. A backend security boundary
authenticates an integration principal and may issue one
`LiveSourceObserverBinding`. The binding can authorize only receipt and
normalization of allowlisted payload-free metadata for one practice and source.

The observation plane produces `CommittedChangeObservation` plus
`ObservationAdmissionDecision`. Only `ADMIT_SIGNAL` may cross an exact
`ObservationToTemporalSignalTrace` into the existing pure temporal processor.
The temporal processor—not the observer—uses each session's manifest and watch
lease to decide relevance and retire a frame set.

The resulting `ContextReassemblyRequirement` and
`FreshContextReassemblyInstruction` stay inert. A different execution boundary
must reauthenticate the current human/session/practice/purpose and derive a new
no-wider read grant. There is no transitive authority edge from observer to
read, provider or command.

## Principal and tenancy separation

The integration principal is not a receptionist, clinician, Bureau agent or
application session. Its digest, authentication kind, source system, practice
binding, observer generation, policy and expiry must be checked before any
event identity affects deduplication, cursor or revision state.

A practice observer may normalize one signal once and fan out only that exact
payload-free value. It cannot see which users or Bureaus have active frames.
Each session-bound `TemporalWatchLease` separately rechecks practice, session
generation, binding, purpose, selectors, expiry, deduplication and dependency
intersection. Cross-practice or cross-session context is never aggregated in
the observer.

## Payload-free normalization

Normalization is strict structural mapping, not a source read. Allowlisted
metadata is limited to stable identity, event/schema/source coordinates,
practice binding, opaque aggregate and selector references, positive revision,
monotonic transaction position, safe times, sensitivity and reason codes.

Unknown fields, arbitrary nested objects, arrays beyond fixed selector/reason
limits, direct identifiers, free text, before/after values, appointment or
waiting-room state and provider/credential material block admission. Hashing,
aliasing or encrypting a prohibited payload does not make it eligible metadata.
Practitioner, location and appointment-time values are prohibited too; only an
already-authorised sealed selector digest may identify a dependency.

## Ordering and atomicity

`occurred_at`, `received_at` and insertion time are useful audit/freshness
metadata but cannot prove stream completeness. The future source must expose a
strictly monotonic transaction/outbox position. The observation decision binds
the prior coordinate, received coordinate and expected next semantics.

The later mounted implementation must atomically persist the decision,
monotonic invalidation state and next committed checkpoint before scheduling
or attempting any fresh read. Merely observing a cursor is not a checkpoint.
Crash before the atomic commit permits redelivery; crash afterward preserves
deduplication and invalidation. Any uncertain state forces a new baseline and
full invalidation.

The current Diary polling cursor based on `(occurred_at, event_id)` is not such
a coordinate and cannot support a no-loss claim or be inherited as this
observer boundary.

## Baseline and generation

Observer generation distinguishes principal/policy/baseline epochs. A new
generation establishes its monotonic source baseline before a new frame set
and temporal manifest cite it. Existing current frames assembled without that
proven coordinate cannot be silently adopted; they must be invalidated and
rebuilt.

Revocation, expiry, authentication change, policy version change, practice
change, source reset, cursor loss or checkpoint loss consumes the generation.
A successor cannot reuse its deduplication set, checkpoint or watch leases
without explicit verified continuity.

Disablement or recovery cannot return retired context to `CURRENT`; only a
new independently authorised and fully admitted frame generation may become
current.

## Backpressure and failure

The policy declares maximum event rate, batch size and unclassified backlog.
An overflow does not license dropping or sampling relevant change metadata.
The safe result is stop admission, record a privacy-safe overflow reason and
fully invalidate all potentially affected active manifests. Recovery requires
a new baseline and fresh frame generations.

Malformed, unauthenticated, foreign or non-allowlisted observations are blocked
before they influence ordering state. Duplicate and exact replay are suppressed
without renewing any lease. A gap, revision jump or late newer aggregate
revision invalidates rather than interpolates.

Exactly one pending requirement exists for a frame-set generation. Further
relevant observations coalesce as bounded privacy-safe cause digests; they
cannot create an unbounded read loop. Dependency impact comes from the sealed
manifest, never an event-supplied dependency or field list.

## Audit posture

The architecture requires audit of observer enable/disable, principal binding
and revocation, policy/generation changes, authentication failures, continuity
gaps, overflow and recovery baseline. Audit entries use digests, safe codes and
counts only. They do not contain event payload, patient/product fields or
become Bureau Memory, current context, read grants or command evidence merely
because they are audited.

## Default-off control

The default-off switch is backend-owned and practice/source scoped. A UI flag,
manifest alone, environment accident, active user session or existing Diary
polling exception cannot enable the Context Fabric observer. A later runtime
gate must prove feature configuration, principal binding, database isolation,
start/stop/restart behavior, checkpoint durability and cleanup before any live
claim.

While disabled there is zero source connection, credential acquisition,
admission, cursor movement or read request. This plan does not acknowledge an
event, persist a checkpoint, retain observations, schedule a retry or claim
crash recovery.

## Non-authority statement

The design does not establish a live integration, event delivery, database
truth, patient-data handling, durable checkpoint, fresh read, model context,
command, deployment or production operation. It only fixes how those future
boundaries must remain separate and fail closed.
