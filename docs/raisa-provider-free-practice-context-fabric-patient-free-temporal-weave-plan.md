# Provider-free Practice Context Fabric patient-free temporal weave plan

Date: 2026-08-06

Status: frozen bounded implementation plan

Parent result:
`raisa_provider_free_practice_context_fabric_current_operational_weave_pass`

## Objective

Prove the patient-free temporal control plane that keeps an admitted, immutable
`ContextFrameSet` truthful while a user continues a Bureau interaction. A
backend-owned dependency manifest and expiring watch lease may classify typed
committed-event signals. A relevant signal must supersede the affected set and
emit one inert requirement for a fresh authorised reassembly; it may never
patch a frame, inject an event payload as truth or execute the read itself.

The same contract also distinguishes selected historical operational snapshots
from current truth and from committed-event memory. Historical records use
valid-time and transaction-time intervals and remain read-only, purpose-scoped
context with no present-truth or command authority.

The exact result label is
`raisa_provider_free_practice_context_fabric_patient_free_temporal_weave_pass`.

## Inputs

Only repository-authored synthetic objects are eligible:

1. the exact admitted Current operational weave packet and frame-set digest;
2. a backend-authored `TemporalDependencyManifest` derived from that frame set;
3. a backend-owned, narrowing `TemporalWatchLease` bound to the same practice,
   principal/session generation, grant, policy and frame-set digest;
4. closed patient-free `TemporalSignalEnvelope` fixtures shaped like committed
   event metadata, never event payloads or current read data; and
5. closed patient-free `HistoricalOperationalSnapshot` fixtures with explicit
   valid-time, transaction-time, correction and retention-class coordinates.

The first implementation is a pure function over sealed fixtures. It attaches
no listener, database, feed, source reader, operational registry or clock.

## Outputs

- one closed `TemporalDependencyManifest` with exact frame/source dependencies,
  selector intersections, admitted event families and starting checkpoint;
- one expiring `TemporalWatchLease` that cannot widen the parent grant;
- a deterministic `TemporalInvalidationDecision` for every ordered signal;
- zero or one deduplicated `ContextReassemblyRequirement` for the active set;
- an immutable `TemporalFrameSetState` transition from `CURRENT` to
  `REASSEMBLY_REQUIRED`, `EXPIRED` or `REVOKED` when applicable;
- selected bitemporal historical frames that are explicitly not current truth;
- one temporal weave trace and same-packet proofreader trace; and
- a closed JSON Schema, admitted example, deterministic acceptance evidence and
  focused tests.

`ObservedCursor` and `CommittedCheckpoint` are distinct. One sealed watcher
transition records the observation, decision, emitted invalidation/suppression
and next checkpoint before any reassembly begins. A failed fresh read therefore
cannot lose the signal that made the old set stale.

## Deterministic lifecycle

1. Verify the exact parent frame-set, source, grant, binding and proofreader
   digests before deriving any dependency.
2. Intersect every proposed event family, frame type, source class, location,
   aggregate selector, time window and lifetime with backend policy. Empty
   mandatory intersections fail closed.
3. Bind the manifest and lease to the exact practice binding, session binding,
   session generation, policy version, grant digest and active frame-set digest.
4. Admit only committed, schema-allowlisted, patient-free, non-expired signals
   that match practice, policy, lease generation and monotonic checkpoint rules.
5. Suppress foreign, unrelated, duplicate, replayed, equal/older revision and
   already-superseded signals without changing frame-set state.
6. On the first relevant signal, atomically mark the immutable frame set
   `REASSEMBLY_REQUIRED` and emit one inert reassembly requirement. Further
   relevant signals may coalesce into the same requirement but cannot restore,
   patch or release the old set.
7. A revision jump, noninitial feed re-baseline, cursor mismatch or late event
   with a newer aggregate revision is an explicit continuity gap. It invalidates
   the affected set, requires full reassembly and prohibits historical-
   continuity claims across the gap.
8. Lease expiry, session invalidation or revocation fail closed.
   They make the old set unavailable and require a fresh authority decision;
   they are never guessed through.
9. A future reassembly result is admissible only to the exact current lease,
   session generation and newest request revision. Earlier asynchronous results
   are rejected as stale generation or superseded request.
10. Historical selection intersects the authorised temporal window and retention
   class. Corrections preserve both the original valid-time claim and the later
   transaction-time knowledge; no record is overwritten in place.
11. Proofreading recomputes every digest, transition, suppression, coalescence
    and temporal relation using the same caller-supplied clock.

## Data, provider, cost and licence posture

- Data: newly authored synthetic opaque identifiers, counts and operational
  labels only; no patient, clinical, product-derived, protected or historical-
  PHI material.
- Provider and external retrieval: none.
- Cost: zero provider/cloud cost.
- Licence: no external corpus, content or licence surface.

## Allowed side effects

Repository writes are limited to this plan/design/threat delta, one closed
schema/example/evidence directory, one pure temporal engine, one acceptance
generator, focused tests and later acceptance/continuity artifacts. The engine
itself has zero filesystem, network, database, subprocess, provider,
product-runtime, event-listener, source-read or command effects.

## Forbidden surfaces

No `app/**` or `docs/diary/**` change or import; no GraphQL root, resolver,
route, mutation or subscription; no REST/OpenAPI command; no real application
session, event feed, database or watcher; no persistence, retention scheduler,
background worker or operational history store; no provider or external
retrieval; no patient/product/protected data; no deployment, production,
release, Pages, protected evidence or protected-ref movement. Preserve and
exclude `docs/branding/` and unrelated untracked artifacts.

## Acceptance

1. Every object is closed and schema-valid; candidates cannot supply tenant,
   principal, role, session, policy, authority or retention decisions.
2. The dependency manifest is derived from and cryptographically bound to the
   exact parent frame-set, source and grant digests.
3. Lease intersection only narrows event family, frame/source class, selectors,
   time, freshness, sensitivity, cardinality and byte ceilings.
4. A relevant signal never edits or replaces any frame field. It produces an
   immutable state transition and inert reassembly requirement only.
5. Event metadata is never projected as current operational truth, historical
   state, user-visible content or command evidence.
6. Irrelevant, foreign-practice, replayed, duplicate, equal/older, expired,
   undeclared and superseded-generation signals remain silent and deterministic.
7. Cursor/revision/ordering gaps, revocation, lease expiry and session-generation change fail
   closed without retaining the old frame set as usable context.
8. Multiple relevant signals coalesce without losing their ordered cause
   digests; one active set produces at most one outstanding requirement.
9. Stale asynchronous reassembly results cannot overwrite a newer request,
   generation, grant or frame set.
10. Historical snapshots prove half-open valid-time and transaction-time,
    correction/supersession lineage, purpose-specific selection and explicit
    `current_truth_authority: false`.
11. Historical queries intersect both `valid_at` and `known_at`; missing
    coverage is explicit, event occurrence is not treated as valid-time truth,
    and delivery TTL never defines snapshot retention.
12. The same-packet proofreader blocks tampering, expiry, state rollback,
    payload smuggling, temporal overlap defects or digest mismatch.
13. API Spine regressions prove no new API or command surface; static/runtime
    counters prove zero provider, network, database, subprocess, filesystem-
    write, product-runtime, listener, command, deployment and protected actions.

Evidence label:
`provider_free_authored_synthetic_patient_free_temporal_weave`.

## Recovery and stop

Any schema, deterministic, temporal, source-binding, security or regression
failure blocks evidence regeneration and independent review. Mechanical repairs
remain inside the exact tranche file set. A material semantic conflict returns
to Sol's recovery lease. No stale, partially classified or incompletely
proofread temporal packet is released.

## Claim boundary and next dependency

Passing proves only a pure authored-synthetic watcher/invalidation and
bitemporal-snapshot contract. It does not prove a live database watcher, event
transport, production retention, product authorization, patient privacy,
provider-model retrieval, runtime performance or command safety.

After acceptance, the next dependency-satisfied descendant is a separately
bounded provider-free intent-shaped temporal retrieval rehearsal. This plan
grants that later descendant no product, patient, provider or runtime authority.
