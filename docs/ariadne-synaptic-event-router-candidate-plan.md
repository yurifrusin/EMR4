# Ariadne Synaptic Event Router - Candidate Plan

Date recorded: 2026-07-22

Decision owner: Yuri

Status: `recorded_candidate_not_authorised_for_implementation`

## 1. Decision record

Yuri asked that a possible scope-aware bridge between the practice database
and an operational Ariadne sandbox DAG be preserved before deciding whether to
start a new tranche.

The candidate is an **Ariadne Synaptic Event Router**. It would consume typed,
committed domain events, determine which live DAG-node scopes intersect the
change, and deliver a bounded steering notice to those nodes. The central
orchestrator would remain the control plane for graph and communication policy;
it would not have to relay every event or resulting data value.

This document records the idea and a safe investigation sequence. It is not a
frozen implementation plan, runtime authorization, API decision, database
watcher approval or permission to start a new tranche.

## 2. Plain-language model

An active node may be reasoning about one patient, practitioner, appointment,
location, time window or proposal. If committed practice truth changes within
that declared scope, the node should be told that its context may be stale.
It can then pause, obtain fresh authorized context and continue, revise or
withdraw its candidate.

The notice is equivalent to steering a conversation, but it is not invisible
mid-reasoning data injection. Delivery occurs through a node mailbox at a
declared message or tool boundary. When safe continuation is impossible, a
later immutable node generation supersedes the earlier attempt and resumes from
an explicit checkpoint.

The notice does not contain a raw changed row and is not display truth or
command authority. It says, in effect:

> Authoritative state affecting your declared scope changed. Re-read these
> permitted context frames before relying on your earlier conclusion.

## 3. Architectural separation

The proposal requires two graphs that must not be confused:

- the existing **development Continuity graph** records EMR4 decisions,
  evidence, contracts and closed boundaries; and
- a future **per-practice operational DAG** would describe live node instances,
  permitted communications and execution state.

No patient, practice or operational runtime state belongs in the development
Continuity graph. The operational graph may reuse Ariadne's typed-frame,
provenance, immutable-attempt, bilateral-policy and human-authority grammar,
but it requires a separate schema, store and authorization decision.

## 4. Candidate components

### 4.1 Committed-domain-event intake

The intake should observe an append-only transactional outbox or equivalent
committed-event source. It must not poll arbitrary tables, infer domain meaning
from raw row differences or treat PostgreSQL `LISTEN/NOTIFY` as durable truth.
Notification may later be a wake-up mechanism; the committed outbox coordinate
remains the replayable authority.

### 4.2 Static DAG policy

The static operational DAG would declare which node roles may receive which
event families, scope keys, steering frames and fresh-read grants. The event
router cannot create an edge or capability absent from this policy.

### 4.3 Live node-scope registry

Each active node generation would publish a minimal, typed scope lease such as:

- practice and authorized principal boundary;
- node and container generation;
- accepted event and steering-frame types;
- relevant aggregate or resource references;
- practitioner, location and bounded time window where applicable;
- active projection or proposal coordinate;
- expiry, freshness and checkpoint coordinate; and
- sensitivity class without free text or raw clinical content.

The registry is an operational overlay, not a model prompt and not shared
mutable sandbox memory. Expired, superseded or unauthorized leases fail closed.

### 4.4 Deterministic scope-intersection router

The router compares a validated committed event with eligible live leases. It
must be deterministic code, not an LLM classification. A delivery requires:

1. the same authorized practice boundary;
2. an allowed event family and schema version;
3. an intersection on declared aggregate/resource and, where needed, time or
   projection coordinates;
4. a current node/container generation;
5. bilateral communication-policy permission for the router-to-node steering
   frame; and
6. replay, aggregate-revision and sensitivity checks.

Unrelated changes are suppressed. One event may fan out to several matching
nodes without passing through the orchestrator's context. Routing evidence must
explain why each node matched or was suppressed without recording PII.

### 4.5 Node mailbox and reconciliation

The delivered frame should be a minimal `scope_change_notice` containing event
identity, schema, affected typed coordinates, revision, freshness requirement
and permitted reread hints. It must not include a database row, patient name,
free text, clinical content, credential or command payload.

The receiving node deduplicates the notice and marks affected context stale.
It may continue only after fresh, practice-scoped, role/action/resource-checked
reads. An in-flight attempt either reconciles at an explicit boundary or is
superseded by a later immutable attempt; stale completion cannot overwrite a
newer generation. Reconciliation may preserve, revise or withdraw a candidate,
but cannot confirm or execute it.

### 4.6 Audit and recovery evidence

Any later runtime design must specify stable event identity, monotonic aggregate
revision, per-node delivery/deduplication coordinate, bounded retry and
backpressure, offline catch-up, dead-letter disposition, checkpoint lineage,
lease expiry and privacy-safe audit. At-least-once delivery is acceptable only
when duplicate visible and command effects are mechanically prevented.

## 5. Relationship to accepted EMR4 evidence

The candidate generalizes two accepted foundations without widening either:

- the sandbox-DAG fork proves typed immutable nodes, bilateral direct links,
  restart lineage, fan-out/fan-in and terminal human authority; and
- the Reception One committed-event and availability-reconciliation verticals
  prove one default-off, local, authored-synthetic
  `diary.appointment_rescheduled` signal, deterministic relevance, fresh reads,
  replay suppression and safe preservation or withdrawal of proposal context.

The current product exception routes only to the open Reception One client. It
does not query an operational DAG, register live node scopes, deliver to model
mailboxes or authorize a general event consumer.

## 6. API Spine and authority classification

Boundary classification:
`candidate_async_event_consumer_plus_operational_scope_registry_and_context_steering`.

The accepted API Spine pattern would be:

- committed async events report change and never bypass REST/OpenAPI commands;
- event payloads remain minimal and do not substitute for authorized reads;
- GraphQL remains read-only and gains no mutation or subscription authority;
- context frames are typed, minimal, source-labelled, freshness-bound and
  non-authoritative;
- YAML or JSON manifests may declare policy, but typed runtime code must enforce
  authorization, scope intersection and communication policy; and
- appointment mutation still requires the existing explicit, idempotent,
  audited and human-confirmed command path.

## 7. Recommended investigation sequence

If Yuri later authorizes a new tranche, the evidence-led first step should be a
**non-executing authored-synthetic routing protocol extension**:

1. define a separate operational-DAG scope-lease and steering-frame schema;
2. extend the sandbox trace with matching, suppression, fan-out, replay,
   supersession and fresh-read-grant examples;
3. add deterministic negative tests for cross-practice, stale-generation,
   undeclared-frame, unilateral-policy, sensitive-payload and event-to-command
   escalation failures;
4. compile the accepted declarations into inspectable dry-run start-up,
   subscription and restart-policy manifests; and
5. stop with no container, model, database, product API or event feed attached.

This incorporates the previously identified dry-run policy compiler as part of
the proof: its first useful output would be inspectable node scope leases,
router subscriptions and restart diffs rather than generic container settings
alone.

A later, separately authorized tranche could connect the protocol to only the
already accepted default-off local reschedule feed. Broader event families,
delivery transports or operational persistence would each require another
explicit decision.

## 8. Candidate acceptance questions

Before freezing any implementation plan, decide:

- whether the first tranche is strictly repository-local and non-executing, as
  recommended, or includes the existing local event-feed adapter;
- whether scope leases are entirely compiled at node start or may be narrowed
  during a generation without restart;
- which scheduler behavior applies to a notice received while a node is
  reasoning: reconcile at boundary, cancel and supersede, or a typed policy by
  node role;
- what minimum routing evidence is retained and for how long;
- whether deterministic nodes and model-backed nodes share one mailbox contract;
  and
- whether the Synaptic Event Router is a general Ariadne substrate or remains
  appointment-first until the current proof is mature.

Sol Extra High should freeze the architecture and threat boundary because these
choices define future authority, privacy, durable-session and execution
semantics. A fresh independent veto is appropriate once a candidate protocol
exists; it is not required merely to preserve this idea.

## 9. Gates that remain closed

This record authorizes no database access or change-data capture, event family,
outbox change, listener, publisher, broker, background worker, WebSocket,
container, model, provider, product read, GraphQL mutation/subscription, REST
command, appointment write, autonomous action or production service.

PII, real practice data, protected holdouts, historical Diary material,
Stage 3B, voice, external participants, persistent attention preferences,
retention scheduling, production, deployment and release remain closed. The
existing bounded `diary.appointment_rescheduled` runtime exception is unchanged
and does not authorize this candidate.

## 10. Planning-record result

Exact result: `ariadne_synaptic_event_router_candidate_recorded`.

Artifacts are this candidate plan, Compass map revision 5 and its generated
report, the live handover update, the orchestration ledger entry, deterministic
Compass assertions, and the mandatory five-source receipts.

Unresolved gates are the scope-lease contract, operational-DAG schema,
steering/checkpoint semantics, privacy-safe routing evidence, runtime threat
model and every real adapter named above. The recommended next tranche is the
non-executing authored-synthetic protocol extension in section 7, but it remains
unstarted pending Yuri's explicit decision. GPT Sol should freeze that future
architecture at Extra High because it would define authority, privacy and
durable execution semantics.
