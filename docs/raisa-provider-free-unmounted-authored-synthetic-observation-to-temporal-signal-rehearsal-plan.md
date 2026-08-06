# Provider-free unmounted authored-synthetic observation-to-temporal-signal rehearsal plan

Date: 2026-08-06

Status: frozen bounded implementation plan

Parent result:
`raisa_provider_free_default_off_live_source_observation_boundary_architecture_pass`

## Objective

Prove the first pure implementation of the accepted live-source observation
membrane without connecting to a source. Trusted code must validate a
default-off policy, an expiring observer binding, a backend-owned alias
registry, an impact-floor policy and one sealed synthetic-only activation;
normalise a recursively closed authored-synthetic committed-change fixture;
derive a domain-separated keyed observation identity; and construct exactly
one accepted `TemporalSignalEnvelope` from backend-owned impact, never from
source-supplied selectors or replacement truth.

The exact result label is
`raisa_provider_free_unmounted_authored_synthetic_observation_to_temporal_signal_rehearsal_pass`.

## API Spine classification

This is an unmounted async/event contract rehearsal. GraphQL remains the
read/context graph and gains no field, mutation or subscription. REST/OpenAPI
remains the command plane and gains no operation. The async event boundary
admits only payload-free control metadata and cannot return data, execute a
read, invoke a provider or become command evidence. No manifest or fixture is
executable policy.

The rehearsal may import the accepted pure temporal-weave constructors and
processor. It adds no `app/**`, `docs/diary/**`, API route, resolver, database,
outbox, feed, watcher, listener, broker, scheduler or background worker.

## Exact inputs

Only newly authored synthetic values and accepted public pure functions are
eligible:

1. a sealed `LiveSourceObservationPolicy` with exact schema/policy versions,
   `enabled_by_default: false`, current `enabled: false`, closed source/event/
   schema/aggregate enums, bounded rate/time ceilings, one alias-registry
   digest and one impact-policy digest;
2. a sealed `LiveSourceObserverBinding` for one synthetic integration
   principal, practice, source, policy version, observer generation and expiry,
   with every data-return/read/provider/command/persistence ceiling false;
3. a sealed backend-owned `ObservationAliasRegistry` containing only bounded
   registered aliases and their trusted synthetic aggregate/location/
   practitioner resolutions for the exact practice/source/class;
4. a sealed `ObservationImpactPolicy` mapping each allowed event/schema/
   aggregate triple to a non-empty conservative minimum frame-type floor;
5. one exact `SyntheticObservationClassificationActivation`, valid only for
   `AUTHORED_SYNTHETIC_REHEARSAL` and fixing source connection, credential
   acquisition, cursor persistence, data return, read, provider, command and
   persistence authority false;
6. one recursively closed `SyntheticCommittedChangeInput` whose raw source
   event id is non-semantic, bounded and used only inside trusted normalisation;
7. an in-memory synthetic HMAC key of at least 32 bytes, never released in any
   observation, trace, evidence or error; and
8. the accepted authored-synthetic Current packet, temporal dependency
   manifest and watch lease used only to prove compatibility with the existing
   temporal classifier.

No source input may contain a selector, dependency id, field list, patient or
person identifier, practitioner/location/time value, correlation id, reason
string, callback, URL, credential, payload, before/after state or replacement
context. Unknown fields fail closed before hashing or classification.

## Outputs

- one sealed, recursively closed `CommittedChangeObservation` containing only
  exact enums, positive bounded numeric coordinates, canonical UTC instants,
  backend-issued aliases, exact controlling digests and a domain-separated
  keyed observation-id digest;
- one sealed `ObservationAdmissionDecision` from the closed decision enum;
- zero or one accepted `TemporalSignalEnvelope`; only `ADMIT_SIGNAL` may emit
  the signal in this rehearsal;
- one sealed `ObservationToTemporalSignalTrace` reconstructing every repeated
  coordinate and proving the signal impact came from the backend policy floor
  plus independently resolved registry entries;
- one design-time `ObservationContinuityRequirement` with every persistence,
  checkpoint, connection and runtime flag false;
- the existing temporal processor's decision/state/requirement for the emitted
  signal, proving compatibility without mounting a watcher;
- one same-packet deterministic proofreader decision;
- closed schemas, an authored-synthetic example and deterministic evidence; and
- focused and inherited tests.

Suppressed, blocked, disabled and full-invalidation-required admission outcomes
emit no ordinary temporal signal. In particular, unknown/unresolvable impact
must return `FULL_INVALIDATION_REQUIRED` with a bounded source-class impact set
and can never be translated into `IRRELEVANT`. A later source-specific
descendant must freeze how such a control decision is durably handed to the
temporal plane.

## Deterministic lifecycle

1. Verify exact closed shapes and seals for policy, binding, registry, impact
   policy and activation. Reconstruct every controlling digest rather than
   trusting copies in the input.
2. Validate backend-issued aliases against a closed ASCII grammar of at most 96
   characters and resolve them in the exact bound practice/source/class
   registry. Arbitrary source strings are never aliases.
3. Validate the raw source event id only against the exact synthetic source
   contract and length ceiling; derive `sha256:<64 lowercase hex>` with HMAC-
   SHA-256 over a fixed domain, source-contract version, observer generation
   and raw id. The raw id and key are then discarded.
4. Validate non-boolean positions/revisions in `1..9007199254740991`, canonical
   RFC 3339 UTC instants, policy clock skew, binding/activation validity and all
   exact source/practice/policy/schema/registry/impact digests.
5. Because the policy remains disabled, require the exact unexpired synthetic
   activation for the sole positive path. Missing, substituted, expired or
   `LIVE` activation returns `OBSERVER_DISABLED`; it never mutates policy or
   creates a source connection.
6. Classify foreign scope, wrong schema/policy, expired/revoked binding,
   duplicate/replay and position/revision/baseline uncertainty through the
   closed admission enum. Ordering uncertainty returns
   `FULL_INVALIDATION_REQUIRED`, never a guessed checkpoint.
7. For `ADMIT_SIGNAL`, derive impact as the union of the non-empty mandatory
   event/schema/aggregate floor and independently resolved registered alias
   impact. Source metadata contributes no selector or field impact.
8. Construct the accepted temporal signal only through its public constructor.
   Signal id is the keyed observation digest; aggregate/location/practitioner
   references come only from the registry; affected frame types contain the
   mandatory floor; observed/expiry times and safe reasons are backend-authored.
9. Seal a one-way trace binding policy, binding, observation, alias-registry,
   impact-policy and signal digests. It fixes `checkpoint_persisted: false`,
   `source_read_executed: false`, `fresh_read_executed: false`,
   `provider_called: false` and `command_executed: false`.
10. Pass the signal to the accepted temporal processor with the reconstructed
    parent manifest and lease. Require the ordinary temporal result to retire
    context and emit only the existing inert reassembly requirement; the
    observation layer never invokes a source adapter.
11. The same-packet proofreader rebuilds the canonical packet from authoritative
    inputs, uses constant-time digest comparison where applicable, checks
    expiry and exact equality, and blocks any self-consistently resealed
    substitution, impact narrowing or authority/effect widening.

## Closed decision enum

`ADMIT_SIGNAL`, `SUPPRESS_DUPLICATE`, `SUPPRESS_REPLAY`,
`BLOCK_FOREIGN_SCOPE`, `BLOCK_SCHEMA_OR_POLICY`,
`BLOCK_EXPIRED_OR_REVOKED`, `FULL_INVALIDATION_REQUIRED`, and
`OBSERVER_DISABLED` are the only admission decisions. Reason codes are an
independent closed backend enum; input reason text is prohibited.

## Data, provider, cost and licence posture

- Data: newly authored synthetic opaque operational coordinates only; no
  patient, clinical, financial, product-derived, protected or historical-PHI
  data.
- Provider/external retrieval: none.
- Cost: zero provider/cloud cost.
- Licence: no external content or corpus.

## Allowed side effects

Repository writes are limited to this plan/design/threat delta, one pure module,
one read-only acceptance generator, one closed continuity evidence directory,
focused tests and later closeout/acceptance/continuity artifacts. The module
has zero filesystem, network, database, subprocess, source, listener, provider,
product-runtime, persistence or command effects.

## Forbidden surfaces

No `app/**`, `docs/diary/**`, API schema, mounted route, resolver, GraphQL
subscription/mutation, REST/OpenAPI operation, database/migration/trigger,
outbox/feed/watcher/listener, broker, scheduler, background worker, checkpoint
store, persistence, operational cursor movement, source/product read, provider,
patient/product/protected data, raw audit, command/write, deployment,
production, release, Pages, protected evidence or protected-ref movement.
Preserve and exclude `docs/branding/` and every unrelated untracked receipt,
state, evidence or cost-ledger artifact.

## Acceptance

1. Every contract and nested value has an exact closed shape, schema and seal;
   unknown fields, bool-as-int, malformed digest/alias/time or oversized values
   fail closed.
2. Policy remains disabled and fixed default-off. The sole positive path needs
   the exact sealed authored-synthetic zero-effect activation; absent, expired,
   substituted or live-mode activation yields `OBSERVER_DISABLED`.
3. Binding is exact practice/source/principal/generation/policy scoped,
   expiring/revocable, and every read/provider/command/persistence ceiling is
   false.
4. Raw source event identity is accepted only by the source-contract grammar,
   converted to a domain-separated keyed digest and absent from every output.
   Changing source contract or observer generation changes the digest.
5. Source input contains no selector/dependency/field/correlation/reason or
   direct operational/patient value. Hashing, aliasing or resealing prohibited
   payload never admits it.
6. Backend aliases resolve only in the exact practice/source/class registry;
   unresolved, foreign or substituted registry coordinates fail closed.
7. Backend impact floor is non-empty and cannot be removed or narrowed by any
   source value. Unknown/unresolvable impact yields bounded
   `FULL_INVALIDATION_REQUIRED`, never silence or `IRRELEVANT`.
8. Duplicate, replay, foreign scope, wrong schema/policy, expired/revoked,
   baseline, position, revision and clock-skew cases produce the exact closed
   deterministic decision without renewing authority or advancing state.
9. Only `ADMIT_SIGNAL` emits exactly one existing temporal signal. Its impact,
   aliases, times and digests reconstruct exactly from trusted inputs and no
   observation payload becomes context truth.
10. The accepted temporal processor classifies the emitted signal, retires the
    affected frame set and emits only an inert reassembly requirement. The old
    frame bytes remain unchanged and no fresh read executes.
11. Trace and design-time continuity requirement fix every runtime, connection,
    credential, checkpoint, persistence, read, provider and command effect
    false.
12. Same-packet proofreading blocks resealed policy/binding/registry/impact/
    observation/signal substitution, expiry, impact narrowing, raw-id/key leak,
    authority widening or bypass.
13. Closed schemas, example and evidence hashes reproduce exactly; focused and
    inherited temporal/API Spine/architecture tests pass serially.
14. Static counters prove no API, app, database, listener, source-read,
    provider, command, filesystem-write, deployment, Pages or protected-ref
    surface was added.

Evidence label:
`provider_free_authored_synthetic_unmounted_observation_to_temporal_signal_rehearsal`.

## Recovery and stop

Any shape, digest, alias, impact, activation, admission, temporal compatibility,
proofreader, immutability, static-surface or regression failure blocks evidence
regeneration and review. One bounded mechanical worker correction is permitted;
a semantic contradiction moves to Sol recovery. No blocked, uncertain,
partially reconstructed or self-certified packet is released.

## Claim boundary and next dependency

Passing proves only a pure unmounted authored-synthetic observation-admission
and temporal-signal compatibility contract. It does not prove live event
delivery, source authentication, a real database/outbox/feed/watcher/listener,
durable atomic checkpointing, restart recovery, product reads, patient privacy,
provider cognition, command safety, deployment or production operation.

After acceptance, the next safe descendant is an architecture-only,
provider-free source-specific durability boundary choosing the first payload-
free committed-event family, integration principal and true monotonic
transaction/outbox position, and defining atomic decision/invalidation/
checkpoint persistence. It may not implement or connect that runtime until its
exact source, data, transport, migration, lifecycle and rollback boundary has
been frozen and independently reviewed.
