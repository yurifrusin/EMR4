# Ariadne Synaptic Event Router - Protocol Design

Date: 2026-07-22

Status: bounded repository-local non-executing protocol

## Relationship to the accepted sandbox DAG

This protocol is a descendant of the accepted Ariadne Sandbox DAG design, not
a second messaging system. It retains the predecessor's separation:

- the orchestrator remains the control plane that fixes graph, capability and
  communication policy; and
- declared links carry typed data or control frames without turning ambient
  shared state into an authority source.

The predecessor canonical example remains intact at 13 immutable nodes and 13
typed exchanges. Its bilateral direct availability-to-ranking data link,
forward-only context round trip, restart lineage, fan-out/fan-in and terminal
human-authority gate are unchanged.

The new router adds one typed control-plane exchange shape. A validated
committed event may cause a `scope-change-notice` from the `synaptic-router`
instance to a declared node mailbox. Like every accepted exchange, the notice
names workflow and graph revision, immutable sender and recipient, channel,
kind, correlation, frame, provenance and freshness. It is a staleness signal,
not a database row, a fresh read, display truth or command.

## Two graphs remain separate

The repository Continuity graph records programme decisions and evidence. The
operational DAG described here contains authored-synthetic node, lease, event,
mailbox and checkpoint coordinates. No operational or patient state is written
to the development Continuity graph.

The operational graph is an inert document in this tranche. No graph store,
registry, listener or delivery process exists.

## Bilateral route declaration

The route is authorised only when two immutable declarations agree:

1. the static router policy names the `synaptic-router` sender, `control`
   channel, `scope-change-notice` kind, event type/schema, steering frame and
   sensitivity ceiling; and
2. the node's scope lease names the same router, channel, kind and frame, as
   well as the exact event/schema and bounded scope selectors.

This mirrors the predecessor's bilateral peer rule. A unilateral router rule or
over-permissive node lease cannot create a route. Direct sandbox-to-sandbox
control messages remain forbidden; the notice comes from the declared router
control-plane instance.

## Scope lease

A lease is a minimal time-bounded claim about what can make one node's context
stale. It binds practice, principal, immutable node/instance/attempt, container
generation, policy revision, mailbox, checkpoint, accepted event and frame
types, resource selectors, minimum aggregate revision, sensitivity ceiling,
expiry, handling policy and fresh-read-grant coordinate.

Selectors cover appointment aggregate, practitioner, location, projection,
proposal and bounded time window. They contain authored-synthetic opaque
references only.

Communication policy remains immutable for a container generation. A later
lease revision in the same generation may only narrow an existing lease: remove
accepted types or selectors, shrink the time window or reduce the sensitivity
ceiling. It cannot change practice, principal, node, peer, channel, kind, frame,
mailbox, checkpoint, handling policy or container policy. Any expansion
requires a later container generation, higher policy revision and exact restart
lineage.

## Deterministic routing

The router is a pure function over one authored-synthetic document. It checks,
in a fixed order:

1. committed status and declared event type/schema;
2. current, non-expired node and lease generation;
3. practice and principal equality;
4. exact policy revision and bilateral router/channel/kind/frame declaration;
5. event sensitivity against policy and lease ceilings;
6. monotonic aggregate and mailbox checkpoint revisions;
7. intersection of every declared selector dimension; and
8. the deduplication coordinate.

A success emits one minimal notice. A failure emits one privacy-safe reason
code. The canonical proof has 11 route attempts: two deliveries fan out to the
availability and ranking nodes, while nine attempts demonstrate replay,
cross-practice, scope, stale-generation, expiry, revision, sensitivity,
undeclared-frame and undeclared-event suppression.

The deduplication coordinate is event ID, lease ID/revision, container
generation and steering frame. At-least-once transport is not implemented, but
the protocol makes duplicate mailbox effects unrepresentable in the trace.

## Mailbox boundary and fresh reads

The mailbox is an inert ordered evidence surface. Delivery happens only at the
declared mailbox/checkpoint boundary; there is no invisible mid-reasoning state
injection. A notice includes affected coordinates and requires a linked
fresh-read grant.

The grant names exact practice, principal, role, read action, resource
selectors, context-frame type, source event/revision and expiry. It explicitly
sets `execution_enabled: false` and `returns_data: false`. It performs no read
and contains no returned data. A future runtime would still need to enforce
role/action/resource checks and obtain fresh authoritative context.

## Reconciliation and supersession

The receiving lease chooses one static handling policy:

- `reconcile-at-boundary` marks the affected context stale and stops at
  `awaiting-fresh-read`; or
- `cancel-and-supersede` records a later immutable attempt with the same
  practice, principal, instance and checkpoint, incremented attempt/container
  generation, higher policy revision, exact `superseded_from` lineage and
  bindings to the notice and grant.

The canonical ranking trace uses supersession. A completion from its earlier
generation is explicitly `rejected-stale-generation`. Neither reconciliation
path can confirm, write, dispatch or execute a candidate.

## Dry-run compiler

The compiler is another pure transform over the same document. It produces:

- an inspectable start-up policy containing statically eligible leases and
  privacy-safe reasons for rejected leases;
- an inspectable subscription policy containing exact event/schema/frame
  declarations with no connection details; and
- a restart policy describing narrow-only same-generation changes, expansion
  through restart, checkpoint lineage and stale-completion rejection.

The artifact is byte-deterministic, source-hashed, default-deny and explicitly
non-executing. It contains no endpoint, DSN, topic, credential, product command
or container command. It starts nothing.

## What remains unproved

This protocol does not prove event-feed integration, authentication,
operational authorization, delivery ordering, durable deduplication,
concurrency, persistence, retries, backpressure, dead letters, retention, RLS,
encryption, container enforcement, model interruption or product behaviour.
Those remain separate architecture and authority decisions.
