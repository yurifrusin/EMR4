# Provider-free default-off live-source observation boundary plan

Date: 2026-08-06

Status: frozen architecture-only plan

Parent result:
`raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_fresh_generation_rehearsal_pass`

## Objective

Freeze the first fail-closed architecture boundary between a future live
practice change source and the accepted Practice Context Fabric temporal
lifecycle. An authenticated, practice-scoped, default-off observer may report
only that an allowlisted committed change might have invalidated one or more
dependencies. It must never supply replacement truth, return context, grant a
read, invoke a provider or carry command authority.

**The observer is not truth.** It proves only that authorised truth may have
changed and that existing context may therefore be unusable.

The architecture result label is
`raisa_provider_free_default_off_live_source_observation_boundary_architecture_pass`.

## API Spine classification

This is an async/event integration architecture plan, not an API or runtime
implementation. The mixed API Spine remains unchanged:

- GraphQL remains a scoped read/context graph with no mutation, provider call
  or observer control surface;
- REST/OpenAPI remains the sole command plane and gains no command here;
- async metadata may announce committed change but cannot become current
  state, evidence for a command or a route around fresh authorization;
- manifests may declare allowlists and limits but cannot execute policy; and
- typed backend code must authenticate, normalize, admit, classify,
  invalidate, authorize any later read and proofread each new frame generation.

No GraphQL field, subscription, REST path, OpenAPI operation, database object,
event consumer, listener, scheduler, background worker or product route is
added in this tranche.

## Three-plane separation

The future boundary has three independent planes:

1. **Observation plane** — authenticates one integration principal, verifies
   practice/source/policy scope and normalizes committed payload-free metadata.
   It cannot inspect a frame set or decide current truth.
2. **Temporal classification plane** — maps an admitted observation to the
   accepted `TemporalSignalEnvelope`, then uses the existing manifest and
   `TemporalWatchLease` to suppress, invalidate or report a continuity gap. It
   returns no data and cannot read a source.
3. **Fresh-read plane** — begins only from an inert accepted
   `ContextReassemblyRequirement` and `FreshContextReassemblyInstruction`, then
   freshly revalidates the human/session/practice/purpose binding and derives a
   distinct no-wider need/grant before any source-specific read. Observation
   authority is never eligible as read authority.

No plane may inherit another plane's principal, lease, credential or authority
by implication.

## Typed architecture contracts

### `LiveSourceObservationPolicy`

A declarative, versioned, default-off policy naming one source system, practice
scope, allowlisted event/schema families, sensitivity ceiling, required
authentication kinds, maximum event rate/batch size, maximum clock skew,
continuity semantics and expiry. It contains no credential, callback, URL,
query, executable policy or product field allowlist.

The policy has an exact schema, policy id, version and digest; fixed
`enabled_by_default: false` and current `enabled: false`; one exact source
contract and schema version; and no wildcard practice, source, event, schema,
aggregate or selector scope. Its fixed ceilings also include
`payload_allowed: false` and `persistence_authority: false`.

### `LiveSourceObserverBinding`

A backend-issued, expiring and revocable binding over:

- observer id and generation;
- authenticated integration-principal digest and authentication kind;
- practice-binding digest, source-system id and source-contract digest;
- exact policy version and event/schema allowlist;
- issued, not-before and expiry instants; and
- fixed `returns_data: false`, `read_authority: false`,
  `provider_authority: false`, `command_authority: false` and
  `persistence_authority: false` ceilings.

It is not a database credential, human session, `ContextAuthorityBinding`,
`TemporalWatchLease` or durable checkpoint.

### `CommittedChangeObservation`

A recursively closed payload-free envelope containing only:

- stable observation/event identity and exact event/schema type;
- source-system id, exact source-contract revision and observer-generation
  coordinate;
- practice-binding digest;
- aggregate class plus opaque aggregate reference;
- positive aggregate revision;
- monotonic transaction/outbox position, expected predecessor position and
  stream id;
- fixed `committed: true` and authored-synthetic/live evidence mode;
- committed, observed and expiry instants;
- allowlisted sealed selector digests already representable by the temporal
  dependency manifest;
- sensitivity code, correlation id and privacy-safe reason codes; and
- the binding and policy digests.

It has no arbitrary payload, patient identifier, patient name, contact detail,
date of birth, Medicare identifier, free text, clinical/financial value,
before/after state, appointment content, replacement context, provider output,
credential, URL, callback or command material. `occurred_at` or wall-clock time
must never be the ordering coordinate.

Practitioner, location and appointment-time values are also prohibited; a
sealed selector digest may identify an already-authorised dependency but may
not disclose the underlying value. Hashing, aliasing or encrypting prohibited
payload does not make it eligible metadata. Opaque references remain sensitive,
internal, expiring and unavailable to the observer after admission.

### `ObservationAdmissionDecision`

A pure deterministic result with one of:

- `ADMIT_SIGNAL`;
- `SUPPRESS_DUPLICATE`;
- `SUPPRESS_REPLAY`;
- `BLOCK_FOREIGN_SCOPE`;
- `BLOCK_SCHEMA_OR_POLICY`;
- `BLOCK_EXPIRED_OR_REVOKED`;
- `FULL_INVALIDATION_REQUIRED` for baseline, ordering, revision, overflow or
  restart uncertainty; or
- `OBSERVER_DISABLED`.

It binds the observation, binding, policy, previous observed coordinate and
decision reasons. It carries no source value and grants nothing.

An architecture-only same-packet proofreader must reconstruct the policy,
binding, observation, manifest/lease coordinates, decision and emitted-signal
digest from authoritative inputs. A self-consistently resealed substitution is
not admissible. Any later trace exposes only digests and privacy-safe reason
codes, fixes `checkpoint_persisted: false`, and grants no authority.

### `ObservationToTemporalSignalTrace`

A sealed one-way mapping from exactly one admitted observation to exactly one
accepted `TemporalSignalEnvelope`. It binds every repeated identity, practice,
aggregate, revision, selector, transaction-position, time, sensitivity,
binding and policy field. The temporal signal contains no observation payload,
and the mapping cannot narrow a known impact to a convenient dependency.

The backend constructs the temporal signal from admitted metadata. An
event-supplied `TemporalSignalEnvelope`, dependency list or field-impact claim
is never trusted. Unknown impact either blocks or causes bounded full
invalidation for the allowlisted source class; it never widens access.

The accepted temporal classifier alone intersects the signal with each
session-bound `TemporalDependencyManifest` and `TemporalWatchLease`. A shared
practice observer may fan out only the same payload-free signal; every session
performs its own binding, generation, scope, expiry, deduplication and
dependency checks.

### `ObservationContinuityRequirement`

A design-time contract for any later mounted implementation. It requires:

- a committed transactional outbox position or equivalent monotonic source
  coordinate;
- a durable classified checkpoint distinct from an observed cursor;
- atomic persistence of decision, invalidation state and next checkpoint;
- stable event identity, aggregate revision and deduplication;
- explicit baseline and observer-generation coordinates;
- gap, overflow, revocation, restart and retention behavior; and
- audit of enable/disable, authentication failure, gap, overflow and
  generation rotation without event payload or PHI.

This plan implements none of those mechanisms and makes no no-loss claim.

The existing Diary committed-event polling feed is not this boundary: it is
payload-bearing. Its `(occurred_at, event_id)` cursor does not establish a no-loss
transaction/outbox position. It may not be inherited or relabelled as a Context
Fabric observer without a separately frozen source-specific descendant.

## Baseline, ordering and restart rule

A newly enabled or rotated observer may not silently attach to an already
current frame set. The safe future sequence is:

1. authenticate and bind a new observer generation while still default-off;
2. establish a monotonic source baseline;
3. bind a newly assembled frame generation and temporal manifest to that exact
   starting checkpoint; and
4. only then admit later committed observations.

If that ordering cannot be proved, all potentially affected active frame sets
become unusable and require fresh authority plus a full new read. The observer
must not replay payloads to reconstruct missed truth. Cursor mismatch,
transaction-position gaps, aggregate revision gaps, late newer revisions,
overflow, restart uncertainty, expired binding, revoked principal, policy
rotation or lost checkpoint all fail closed to suppression or full
invalidation, never silent continuation.

## Default-off and lifecycle rule

The future observer remains disabled unless a separately reviewed runtime gate
issues an exact practice/source policy and binding. Enablement is not inherited
from an active user session, existing committed-event feed, environment default
or accepted synthetic evidence. Binding expiry, revocation, policy change,
principal rotation or practice change consumes the observer generation and any
unclassified input. No observation renews its own authority.

Disabled means zero source connection, credential acquisition, admission,
cursor movement or read request.
Disablement stops future admission and cannot make already invalidated context current again.
A new generation requires a new baseline and new frame-set binding.

## Fresh-read handoff

An admitted observation can produce only an accepted temporal decision. On a
relevant change, that decision retires the old immutable `ContextFrameSet` and
emits the existing inert `ContextReassemblyRequirement`. It does not directly
invoke a source adapter.

Exactly one pending requirement exists for an affected frame-set generation.
Later relevant observations coalesce as privacy-safe cause digests without
creating a read storm or renewing authority. A failed or blocked fresh read
leaves the old generation retired.

A later fresh-read attempt must independently prove:

- a current human/session/practice/purpose `ContextAuthorityBinding`;
- the exact reassembly requirement and instruction are current;
- a distinct monotonically newer request revision;
- a new `ContextNeed` and `ContextScopeGrant` no wider than current authority;
- source-specific authorization immediately before data access; and
- same-packet source, assembly, supersession and proofreader gates before any
  new frame reaches a Bureau.

Observer identity, binding, policy, checkpoint and signal are ineligible as
read credentials, returned context, provider input or command evidence.

## Data, provider, cost and licence posture

- Data: architecture language and opaque authored-synthetic examples only; no
  patient, clinical, financial, product-derived, protected or historical-PHI
  data.
- Provider/external retrieval: none.
- Cost: zero provider or cloud cost.
- Licence: no external corpus or content.

## Allowed side effects

Repository writes are limited to this plan, its design and threat-model delta,
deterministic architecture tests and permanent compass/handover references.
There is no filesystem runtime, network, database, subprocess, provider,
listener, source-read, command or product effect.

## Forbidden surfaces

No `app/**` is added. No `docs/diary/**` is added. No mounted route,
resolver, GraphQL schema change,
subscription, REST/OpenAPI operation, database migration/table/trigger,
outbox/feed/watcher/listener, background worker, broker or scheduler.
No checkpoint store, persistence, operational retention, product source read, provider,
patient/product/protected data, raw audit, cross-Bureau clinical source,
command/write, deployment, production, release, Pages, protected evidence or
protected-ref movement. Preserve and exclude `docs/branding/` and every
unrelated untracked receipt, state, evidence or cost-ledger file.

## Architecture acceptance

1. The API Spine classifies this solely as an async observation boundary;
   GraphQL remains read-only and REST commands unchanged.
2. Observation, temporal classification and fresh-read authority are three
   separately authenticated/bound planes with no credential inheritance.
3. The policy is declarative and default-off; the binding is practice/source/
   principal/generation scoped, expiring and revocable.
4. The observation envelope is recursively closed and payload-free and
   excludes all direct patient/product/clinical/financial/free-text values.
5. Only monotonic transaction/outbox position orders the stream; wall-clock
   time is never accepted as a no-loss coordinate.
6. Baseline establishment precedes frame/manifest binding; uncertainty forces
   full invalidation and fresh authorization rather than replayed truth.
7. Duplicate, replay, foreign-practice, wrong-source, wrong-schema, expired,
   revoked, gap, overflow, restart and policy-rotation cases fail closed.
8. Mapping to the accepted `TemporalSignalEnvelope` is exact, sealed and
   one-way; the observer cannot inspect frames or narrow dependency impact.
9. Every session-bound manifest/lease independently classifies a shared signal
   and no practice observer can disclose or mix session context.
10. Invalidation is monotonic: observer disablement or recovery cannot restore
    a retired frame set.
11. Any later fresh read starts only through the accepted inert requirement,
    fresh authority/no-wider grant, source-specific read and same-packet
    proofreader sequence.
12. Observer policy/binding/signal/checkpoint material is never a read grant,
    returned context, provider input, command or audit evidence for mutation.
13. Future no-loss, durability, restart, RLS/ABAC, audit, rate/backpressure and
    retention requirements are explicit without being claimed or implemented.
14. Disabled mode has zero source interaction or state movement, event-supplied
    impact cannot replace the sealed manifest, pending requirements coalesce,
    and static tests prove that no runtime/API/database/provider/command/
    deployment surface was added while permanent compass text preserves every
    closed gate.

Evidence label:
`provider_free_architecture_only_default_off_live_source_observation_boundary`.

## Recovery and stop

Any ambiguity between observation and current truth, any source payload,
session/practice cross-over, wall-clock-only ordering, implicit enablement,
observer-triggered read, command implication, missing gap/restart behavior or
incidental runtime/API surface requires architecture revision before any
implementation packet. Ordinary language/test corrections remain inside the
exact plan artifact set. A genuinely competing privacy, durability or product
outcome returns to Sol; no such user-owned fork is presently identified.

## Claim boundary and next dependency

Passing proves only that the future live-source boundary has a coherent,
fail-closed, provider-free architecture. It does not prove that any change is
observed or delivered, a database/outbox exists, a checkpoint survives, a
source read is authorized, patient privacy controls work, a model receives
context, or production operation is safe.

It also makes no acknowledgement, retention, background retry, crash-recovery
or no-loss claim.

After architecture acceptance, the next safe descendant is a provider-free,
unmounted, authored-synthetic observation-to-temporal-signal contract
rehearsal. It may implement pure typed constructors, validators, admission,
normalization and adversarial tests over synthetic metadata only. It may not
mount a source, database, feed, watcher, listener, route, persistence,
checkpoint, product read, provider, patient/product data, command, deployment
or protected ref.
