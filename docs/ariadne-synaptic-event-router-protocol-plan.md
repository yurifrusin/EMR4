# Ariadne Synaptic Event Router - Protocol Tranche Plan

Date: 2026-07-22

Owner: Yuri / GPT Sol Extra High

Decision: `approved_scope_frozen_for_non_executing_synaptic_event_router_protocol`

## 1. Purpose

Yuri authorised the bounded, repository-local, non-executing protocol tranche
recorded in `docs/ariadne-synaptic-event-router-candidate-plan.md`. The tranche
will prove that one authored-synthetic committed event can be compared with
typed operational-DAG scope leases, routed or suppressed by deterministic
rules, delivered as a minimal steering notice to an inert node mailbox, and
reconciled through a fresh-read grant or immutable supersession trace.

It will also compile the declarations into inspectable dry-run start-up,
subscription and restart-policy manifests. Compilation is a pure transform; it
does not start, configure, contact or control any runtime.

Exact target result: `ariadne_synaptic_event_router_protocol_pass`.

## 2. Authority and inherited boundaries

This tranche may:

- define a separate versioned operational-DAG routing document and JSON Schema;
- add a standard-library Python validator, deterministic routing projection,
  dry-run manifest compiler and Markdown renderer;
- use only authored-synthetic practice, aggregate, practitioner, location, time,
  proposal and node coordinates;
- model static route policy, versioned scope leases, mailbox envelopes,
  deduplication, suppression, replay, supersession and fresh-read grants as inert
  data;
- model the existing `diary.appointment_rescheduled` event shape as an
  authored-synthetic input fixture without reading or connecting to its feed;
- add deterministic positive and negative artifact tests; and
- register a metadata-only Continuity Engine descendant after acceptance.

It may not:

- connect to PostgreSQL, a transactional outbox, `LISTEN/NOTIFY`, the accepted
  Diary event feed, a product API, GraphQL, REST/OpenAPI or any product module;
- invoke or select a model, provider, plugin, worker, external service, browser,
  server, container, agent, subprocess or live mailbox;
- execute a read, command, appointment mutation, Git action, deployment or
  release from a protocol document or compiled manifest;
- store PII, clinical content, free text, prompts, transcripts, credentials,
  secrets, database rows, provider output, protected evidence or historical
  Diary material; or
- add an event family, API subscription, database watcher, operational registry,
  broker, delivery transport, persistence layer, retry worker or retention
  scheduler.

All existing closed boundaries remain closed. The local Reception One runtime
exception is evidence of an architectural pattern only and grants no adapter
authority to this tranche.

## 3. Boundary classification and API Spine pattern

Boundary classification:
`non_executing_async_event_scope_routing_and_manifest_protocol`.

The accepted API Spine pattern is preserved:

- an event is a committed change signal, never command authority;
- the event payload is minimal and cannot substitute for a fresh authorised
  read;
- GraphQL remains read-only and receives no mutation or subscription;
- REST/OpenAPI remains the only future command boundary;
- context and steering frames are typed, minimal, source-labelled,
  freshness-bound and non-authoritative; and
- JSON manifests are declarative dry-run outputs; typed code validates them,
  but this tranche has no runtime enforcement surface.

No `docs/api-spine/` artifact changes are required. Compatibility will be
verified against the existing API Spine tests.

## 4. Frozen protocol decisions

### 4.1 Static policy and scope leases

The authored-synthetic document has one per-practice operational graph, one
static route policy revision and immutable node/container generations. A scope
lease binds:

- practice and authorised-principal coordinates;
- node, instance, attempt and container generation;
- accepted event types, schema versions and steering frame types;
- aggregate, practitioner, location, bounded time-window, projection and
  proposal selectors;
- minimum aggregate revision, sensitivity ceiling and expiry;
- mailbox and checkpoint coordinates; and
- one handling policy: `reconcile-at-boundary` or `cancel-and-supersede`.

The canonical trace compiles leases at node start. Within the same container
generation a later lease revision may only narrow a lease by removing accepted
types/selectors or shrinking a time window. It must preserve practice,
principal, node, instance, mailbox, checkpoint lineage, sensitivity ceiling and
static policy revision. Expansion requires a later container generation,
higher policy revision and exact `restarted_from` lineage. Expired,
superseded, broadened, stale-generation or unauthorised leases fail closed.

This extends, rather than replaces, the accepted sandbox-DAG grammar. The route
policy is the router's immutable outbound declaration; the node lease is the
recipient's immutable inbound declaration. Both must name the router instance,
`control` channel, `scope-change-notice` kind and exact frame. A lease narrowing
cannot amend peer, channel, kind or frame policy. Every delivery carries the
accepted workflow/graph revision, immutable sender/recipient, correlation,
provenance and freshness fields from the canonical sandbox-DAG exchange shape.

### 4.2 Deterministic route decision

Routing is pure deterministic code. A delivery requires all of:

1. a validated committed authored-synthetic event;
2. the same practice and authorised-principal boundary;
3. an allowed exact event type and schema version;
4. an intersection with a declared aggregate/resource selector and, when
   declared, practitioner, location, time, projection or proposal selectors;
5. a current non-expired node/container and lease revision;
6. a route-policy rule that permits the exact event-to-steering-frame mapping;
7. event sensitivity at or below the lease ceiling; and
8. a strictly newer acceptable aggregate revision with no duplicate delivery
   coordinate.

Every considered event/lease pair produces one privacy-safe reason code. The
canonical example proves exact match, fan-out, cross-practice suppression,
non-intersection, stale-generation suppression, expiry, replay suppression,
aggregate-revision suppression, undeclared-frame denial and sensitivity denial.

### 4.3 Mailbox and fresh-read grants

A matched route produces a minimal `scope-change-notice` envelope containing
only workflow/graph revision, immutable router sender and node recipient,
control channel, notice kind, correlation, event identity/type/version,
affected typed coordinates, aggregate revision, freshness/provenance, route
reason, lease/mailbox/generation coordinates and an allowed fresh-read-grant
identifier. It contains no row, display truth, PII, free text or command
payload. Router-to-node steering is a control-plane message; the accepted v1
prohibition on direct sandbox-peer control messages remains unchanged.

The mailbox is an inert ordered list in the authored-synthetic document. The
deduplication coordinate is `(event_id, lease_id, lease_revision,
container_generation, steering_frame_type)`. Replaying that coordinate is
suppressed and cannot create a second visible or command effect.

A fresh-read grant describes a future permitted reread surface with exact
practice, principal, role, action, resource selectors, context-frame type,
event/revision basis, issue/expiry time and `execution_enabled: false`. It
contains no returned data and performs no read. A notice cannot refer to a
missing, stale, cross-practice, broader-resource or action-capable grant.

### 4.4 Reconciliation and supersession

For `reconcile-at-boundary`, the current node generation marks the relevant
context coordinate stale and may continue only after a matching fresh-read
grant is represented at a declared mailbox/checkpoint boundary.

For `cancel-and-supersede`, the current attempt becomes superseded and a later
immutable attempt resumes from an exact checkpoint. The later attempt must keep
the same practice, principal and instance, increment attempt and container
generation, name `superseded_from`, use a higher policy revision, and bind the
notice and fresh-read grant. A completion emitted by an earlier generation is
rejected as stale. Neither path may confirm, commit, dispatch or execute a
candidate.

### 4.5 Dry-run manifests

The compiler emits one canonical JSON artifact with:

- a start-up manifest containing static policy, current node generations,
  compiled scope leases and mailbox contracts;
- a subscription manifest containing exact event types, schema versions,
  practice partition placeholders, steering frames and default-deny rules; and
- a restart-policy manifest containing narrowing rules, expansion-through-
  restart rules, supersession/checkpoint requirements and stale-completion
  rejection.

Every manifest declares `dry_run: true`, `execution_enabled: false`,
`default_decision: deny`, no endpoint/DSN/topic/command, and the source-document
SHA-256. Recompilation must be byte-deterministic and equal the committed
artifact.

Runtime retention is deliberately not designed. The committed routing evidence
contains only authored-synthetic coordinates and reason codes; no operational
retention schedule is authorised.

## 5. Exact implementation surface

Implementation is limited to:

- `scripts/ariadne_synaptic_event_router.py`;
- `docs/ariadne-synaptic-event-router-protocol-plan.md`;
- `docs/ariadne-synaptic-event-router-protocol-design.md`;
- `docs/security/ariadne-synaptic-event-router-threat-model-delta.md`;
- `orchestration/continuity/ariadne-synaptic-event-router.schema.json`;
- `orchestration/continuity/ariadne-synaptic-event-router-example.json`;
- `orchestration/continuity/ariadne-synaptic-event-router-dry-run-manifests.json`;
- `orchestration/continuity/ariadne-synaptic-event-router-evidence.json`;
- `tests/test_ariadne_synaptic_event_router.py`;
- the metadata-only Continuity node record and mechanical Compass orientation
  assertions/report update;
- exact orchestration receipts, closeout and Sol acceptance artifacts; and
- after every acceptance gate passes, the Continuity graph, Compass mechanical
  revision fields/report, live handover and orchestration ledger.

No product source, product test, API contract, database fixture, runtime
configuration or external-worker artifact is in scope. The existing
`tests/test_ariadne_compass.py` may change only to replace the now-consumed
protocol-authorisation decision with the separately closed runtime-adapter
decision.

## 6. Acceptance gates

The tranche passes only when:

1. schema and canonical authored-synthetic document pass JSON Schema and
   semantic validation;
2. route decisions are deterministic and prove matching, fan-out, suppression,
   replay and monotonic aggregate revision;
3. bilateral exact route policy is required and events cannot become commands;
4. lease expiry, stale/superseded generation, illegal narrowing/broadening,
   cross-practice access and sensitivity escalation fail closed;
5. mailbox deduplication and both handling policies have explicit forward-only
   traces;
6. fresh-read grants are exact, time-bounded, non-executing and cannot carry
   returned data or action authority;
7. a stale earlier completion cannot survive supersession;
8. dry-run manifests are deterministic, default-deny, non-executing and contain
   no adapter, endpoint, DSN, topic, provider, model, container command or
   product command;
9. static inspection proves the tool imports no database, network, product,
   model, subprocess or container actuator and exposes only read-only
   `validate`, `route`, `compile-manifests` and `trace` commands;
10. the focused suite, predecessor Ariadne suites, API Spine artifacts,
    continuity/Compass validators, Ruff, compilation, JSON and whitespace gates
    pass serially; and
11. closeout claims remain limited to a non-executing authored-synthetic
    protocol.

## 7. Allocation and reasoning

GPT Sol Extra High owns architecture, implementation, tests, acceptance and
protected integration. No external worker, native subagent or independent
provider reviewer is assigned: the artifacts are tightly coupled, the user
explicitly closed model connections, and deterministic local verification is
the appropriate evidence surface. This substitution is recorded rather than
claiming independent veto evidence.

## 8. Deferred decisions

The following require new Yuri authority: any real scope registry, persistent
mailbox, database/outbox/event-feed adapter, listener, broker, retry/dead-letter
worker, retention policy, operational authentication store, product read,
additional event family, GraphQL subscription/mutation, REST command, model or
container integration, external participant, PII, protected/historical data,
Stage 3B, production, deployment, release or autonomous action.
