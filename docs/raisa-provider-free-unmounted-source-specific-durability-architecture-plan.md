# Provider-free unmounted source-specific durability architecture plan

Date: 2026-08-06

Status: frozen bounded architecture plan

Parent result:
`raisa_provider_free_unmounted_authored_synthetic_observation_to_temporal_signal_rehearsal_pass`

## Objective

Freeze a source-specific durability boundary for the already-defined,
patient-free `diary.appointment_rescheduled.v1` committed-event family. The
boundary must replace the existing delivery feed's wall-clock cursor with a
genuinely monotonic, rollback-safe source coordinate and define how a future
runtime could durably commit an observation decision, monotonic Context Fabric
invalidation, one coalesced reassembly obligation and the next classified
checkpoint in one transaction.

The architecture result label is
`raisa_provider_free_unmounted_source_specific_durability_architecture_pass`.

This tranche is architecture and authored-synthetic contract evidence only. It
does not create or alter a database object, read a committed event, mount an
observer, persist a checkpoint, invalidate a real frame set or execute any
runtime path.

## API Spine classification

This is a source-specific async/event durability architecture. It preserves the
mixed API Spine:

- GraphQL remains a scoped read/context graph with no mutation or subscription;
- REST/OpenAPI remains the only product command plane and gains no operation;
- `diary.appointment_rescheduled.v1` remains a report of committed change, not
  current truth, replacement context or command evidence;
- the existing signed update-confirm command remains the sole event producer;
- YAML and JSON contracts are declarative, not executable policy; and
- every consequential fresh read remains a later application-principal action
  behind fresh purpose, role, practice and source authorization.

No `app/**`, `alembic/**`, `docs/diary/**`, API schema, route, resolver,
database object, feed, watcher, listener, worker or deployment artifact changes
in this tranche.

## Exact source family and non-inheritance rule

The source family is fixed to:

- source system: `emr4-diary`;
- event type: `diary.appointment_rescheduled`;
- schema version: `diary.appointment_rescheduled.v1`;
- aggregate class: `APPOINTMENT`;
- producer: the existing signed appointment update-confirm transaction; and
- present event store: `diary_committed_events`.

The existing `GET /api/v1/diary/events/committed` feed remains an independent,
default-off Reception One delivery surface. Its signed `(occurred_at, event_id)`
cursor, 24-hour delivery expiry and payload-bearing response are not a no-loss
coordinate, observer checkpoint or Context Fabric source. They may not be
reused, upgraded by documentation or treated as evidence that durability
already exists.

The future durability source is a distinct append-only, payload-free control
projection named by this architecture as
`diary_context_observation_outbox_v1`. A later migration may create it only
after a separate reviewed live-runtime plan. Its row is appended in the same
database transaction as appointment truth, appointment audit, idempotency
completion and the existing committed-event row. Visibility after commit is
the publication boundary.

The control projection contains only the exact source contract, closed event
and aggregate enums, a non-semantic raw event UUID, a backend-issued opaque
aggregate alias, aggregate revision, stream position, predecessor position, a
canonical transaction-authored instant and controlling version/digest fields.
It contains no event payload, appointment/practitioner/location identifier,
time slot, actor identity, command or audit id, correlation id, reason text,
patient/clinical/financial value, before/after state or provider material.

## Exact principals and authority separation

### Observation integration principal

The exact logical integration principal is
`emr4:integration:context-fabric:diary-appointment-rescheduled-observer:v1`
with kind `integration_service_account`. A later credential binding may grant
it only:

- practice-scoped `SELECT` on the exact payload-free control projection;
- the exact source/event/schema/stream scope above; and
- access to the current observer policy/binding and HMAC key schedule needed to
  normalize one observation.

It receives no `SELECT` on `diary_committed_events.payload` or any appointment,
patient, practitioner, location, audit, idempotency or Context Fabric frame
table. It has no insert/update/delete, checkpoint, invalidation, fresh-read,
provider, command, application-session, deployment or secret-administration
authority. Its `LiveSourceObserverBinding` retains
`persistence_authority: false`.

It must never reuse the staff JWT or human/application-session principal
accepted by the existing committed-event HTTP feed.

### Temporal durability coordinator

A separate internal service principal is fixed as
`emr4:service:context-fabric:temporal-durability-coordinator:v1`. A later
runtime binding may allow it to invoke one narrowly typed transaction that
touches only admitted-observation receipts, observer generation/checkpoint
state, Context Fabric frame-set lifecycle state, coalesced reassembly
obligations and privacy-safe observer audit. It cannot query source payloads,
current product truth or session content and has no provider or product-command
authority.

### Fresh-read principal

Any later fresh read remains owned by the current authenticated application
principal and a new no-wider `ContextScopeGrant`. Neither integration identity,
durability identity, outbox position, checkpoint, invalidation record nor audit
entry is eligible as a read grant or command evidence.

Credentials, cloud service-account names, PostgreSQL roles and key-storage
mechanisms are not created here. A later live gate must bind these exact logical
principals to independently reviewed operational credentials.

## Durable source coordinate

### Stream

The exact logical stream id is
`emr4:diary:appointment-rescheduled:v1`, partitioned by practice. Check-in or
future Diary event families do not consume its positions.

### Transactional head

The future producer must lock one row keyed by `(practice_id, stream_id)`, read
its current `last_position`, and transactionally update it from `n` to `n + 1`
while appending the payload-free outbox row with:

- `predecessor_position: n`;
- `transaction_position: n + 1`; and
- `stream_epoch: 1` for this source-contract generation.

Both coordinates are non-boolean signed 64-bit positive integers, except the
established baseline may be zero. The initial source head is zero and the first
row is `(predecessor: 0, position: 1)`. Counter exhaustion blocks observer
publication and requires a new source-contract epoch; it is never wrapped.

This counter is an ordinary transactionally updated row, not a PostgreSQL
`SEQUENCE`, identity column, wall-clock timestamp, UUID ordering, `xmin`, commit
timestamp or WAL LSN. Rollback therefore rolls back both head advancement and
row append; concurrent event transactions serialize only on their exact
practice/stream head. A position gap is never explained away as normal sequence
allocation behavior.

The application command remains authoritative for appointment mutation. The
outbox row has no independent command meaning and cannot be inserted after the
fact as a best-effort side effect.

`aggregate_revision` is a freshness/anomaly coordinate, not stream continuity.
The current producer derives it from all appointment audit rows, so a jump may
reflect another appointment action and cannot prove a missing reschedule. For
one registered aggregate alias the later classifier requires a strictly newer
revision for a new source position; equality or reversal fails closed, but a
jump never substitutes for, or automatically contradicts, contiguous stream
positions.

## Payload-free observation projection

The future control row maps to the accepted observation membrane only after:

1. the observation integration principal and exact practice/source binding are
   authenticated;
2. the row's recursively closed shape and exact contract digest are verified;
3. the raw event UUID is accepted solely as a non-semantic event coordinate,
   converted to the accepted domain-separated HMAC observation digest and
   discarded;
4. the backend-issued aggregate alias resolves in the exact practice/source/
   aggregate registry;
5. stream epoch, predecessor, position and aggregate revision are checked
   against the durable checkpoint; and
6. the existing proofreader-only observation-to-signal builder releases the
   canonical packet.

The projection does not expose the existing JSON payload. A SQL view that
merely hides columns from a role while retaining an unbounded underlying table
grant is insufficient. The later gate must prove column/table privileges, RLS
or an equivalent practice boundary and inability to query the payload-bearing
row.

## Durable checkpoint contract

`SourceDurabilityCheckpoint` is keyed by practice-binding digest, stream id,
source-contract digest, observer id and observer generation. It contains:

- stream epoch and established baseline position;
- last durably classified transaction position and observation digest;
- last aggregate revision by the exact backend alias where retained;
- policy, binding, alias-registry, impact-policy and key-schedule digests;
- state: `ACTIVE`, `REBASE_REQUIRED`, `CONSUMED` or `REVOKED`;
- last decision receipt digest and monotonic lifecycle revision; and
- created, updated and expiry instants authored by the backend.

An observed cursor, fetched batch, in-memory decision or outbox read never
advances this checkpoint. Only the atomic durability transaction may do so.
The checkpoint is not a source of current context, a session lease or command
authority.

## Durable invalidation watermark and frame fence

Atomic invalidation is represented by a monotonic durable watermark, not by an
in-memory frame mutation. `SourceInvalidationWatermark` is keyed by practice,
stream epoch, observer generation and conservative frame type. It records the
greatest transaction position known to invalidate that class plus a sealed
decision-receipt digest.

Every later durable `ContextFrameSet` generation that depends on this source
must cite the exact stream id/epoch, observer generation, baseline and
`assembled_through_position`. It is current only while its dependency-specific
watermark is not newer. A greater watermark makes the generation permanently
non-current even if a process crashed before updating an in-memory cache.

A replacement generation may be released only when its authoritative truth read
and captured source head are fenced against one another. When both use the same
PostgreSQL source, the preferred future pattern is one database snapshot that
reads truth and the stream head consistently. Otherwise a before/after head
fence must prove equality around the read. A changed or unverifiable fence
blocks release and repeats only under fresh authority. This architecture does
not implement either pattern.

## Atomic decision-invalidation-checkpoint transaction

For one candidate position, the future durability coordinator must perform one
database transaction:

1. lock the exact observer-generation checkpoint;
2. revalidate its active state, policy/binding expiry and every controlling
   digest against backend-owned state;
3. require the candidate to be the exact next position and require its
   predecessor to equal the last durable checkpoint;
4. rebuild and proofread the observation admission, temporal signal and each
   affected session's temporal classification from authoritative inputs;
5. append one immutable classified-observation receipt;
6. monotonically advance every affected durable invalidation watermark and
   derive retirement for intersecting frame generations, never relying on an
   in-memory-only update or restoring an older generation;
7. insert or coalesce exactly one inert reassembly obligation per retired
   frame-set generation using bounded privacy-safe cause digests;
8. append one privacy-safe audit record; and
9. advance the checkpoint to the candidate position only after every required
   invalidation and obligation write succeeds.

All nine effects commit or roll back together. A crash before commit permits
the same source position to be presented again. A crash after commit returns
the existing durable receipt for the same position and cannot repeat, narrow or
reverse invalidation.

A contiguous, fully classified observation that intersects no active manifest
may still advance the checkpoint after its durable receipt and audit commit.
For `FULL_INVALIDATION_REQUIRED` caused by unknown impact or aggregate
continuity, the checkpoint may advance only if every potentially affected
frame-type watermark has been durably advanced in the same transaction. A source-position
gap, predecessor mismatch, lost checkpoint, stream-epoch mismatch or unverifiable
key schedule instead places the generation in `REBASE_REQUIRED`, retires all
potentially affected current frame sets, records audit and holds the last known
contiguous checkpoint; it never skips to the observed upper position.

Malformed, unauthenticated, foreign-scope or wrong-contract input changes no
checkpoint. It stops that generation for operator review and cannot be turned
into a suppress-and-continue decision.

## Duplicate, replay and concurrency rules

- A position greater than `last_checkpoint + 1` or a predecessor different
  from `last_checkpoint` is a coverage gap.
- A position equal to or below the checkpoint is a redelivery only when its
  position, observation digest and existing durable receipt all match in
  constant time; the existing receipt is returned with no new state change.
- Any mismatched identity at an already classified position is source
  corruption and consumes the generation through `REBASE_REQUIRED` plus full
  invalidation.
- Reuse of an observation digest at a new position is source corruption, not a
  harmless duplicate.
- The unique durability key is `(practice_binding_digest, stream_id,
  observer_generation, transaction_position)`.
- Concurrent coordinators serialize on the checkpoint row. A loser rereads the
  committed receipt and never performs a second invalidation.

## Baseline, restart and recovery

A new observer generation must establish a durable source baseline before a
new frame-set generation or temporal manifest may cite it. The frame-set
binding records stream id, epoch, observer generation, baseline position and
checkpoint digest plus `assembled_through_position`. Existing frames without that exact provenance are retired
and rebuilt; they are never adopted retroactively.

On process restart, the runtime reloads the sealed checkpoint, verifies its
digest chain and policy/binding/key schedule, obtains the exact next retained
source row and resumes only when predecessor and position are contiguous. It
does not reconstruct truth from event payloads or from the current Diary feed.

Missing/corrupt checkpoint, lost key material, unknown policy or registry
digest, stream reset, retention overrun, earliest-retained position later than
the required next position, overflow, source contract change or unprovable
predecessor sets the generation to `REBASE_REQUIRED`. Recovery requires full
invalidation, a new observer generation, a new durable baseline and newly
authorised frame generations. Disablement or restart cannot make a retired
frame current again.

## Retention and backpressure

Payload-free outbox retention is position- and checkpoint-based, never the
existing event row's `expires_at` and never wall-clock-only. A row is purgeable
only when:

1. every non-consumed observer generation that could require it has a durable
   checkpoint at or beyond its position;
2. no `REBASE_REQUIRED` recovery or audit investigation has pinned it;
3. the observation-identity key version needed to verify it has completed its
   overlap window; and
4. the later runtime policy's declared safety grace has elapsed.

The exact production grace and storage capacity are later operational choices;
this architecture fixes the safety relation, not a production retention
period. Purge must be bounded by the minimum eligible checkpoint, not the
fastest consumer.

Source-row retention, classified receipt/checkpoint retention and privacy-safe
audit retention are three separately declared later policies. Expiry of one
never silently authorises deletion under another.

Backlog thresholds may stop observer admission and alert, but may not sample or
drop invalidation truth. If required rows are unavailable or capacity/retention
policy breaks continuity, all potentially affected frame sets are retired and
the generation requires rebaseline. No retention failure blocks a user into
believing stale frames are current.

## Observation-identity key rotation

The HMAC key remains outside source rows, checkpoints, receipts, audit and
evidence. `ObservationIdentityKeySchedule` binds closed key ids to exact
position intervals. Routine rotation declares one future
`effective_from_position`; all earlier retained positions continue to verify
with the prior key and all later positions use the successor. The checkpoint
binds the schedule digest and last classified key id.

Routine rotation does not consume the observer generation only when the future
position fence, non-overlapping schedule, retained verify-only predecessor key
and checkpoint schedule digest all validate atomically. Emergency compromise,
missing overlap or any unverifiable schedule consumes the generation.

The observation-identity key ring is dedicated. It may not reuse the
application `settings.secret_key`, the integration-authentication credential or
any provider credential, and a verifier never tries every key.

An old key may be destroyed only after every eligible generation has
checkpointed beyond its final position and retention/audit overlap has closed.
An unavailable required key, overlapping or gapped intervals, retroactive
schedule change, unknown key id or schedule-digest mismatch consumes the
generation through full invalidation and rebaseline. Emergency compromise may
revoke a key immediately, but it makes all dependent continuity unverifiable;
it never silently rehashes old observations or preserves current frames.

Key rotation does not grant credential administration in this tranche and no
key material appears in authored-synthetic contracts.

## Privacy-safe audit

Each future audit record is append-only and may contain only:

- audit schema version and opaque audit id;
- practice-binding, principal, policy, binding, source-contract, alias-registry,
  impact-policy and key-schedule digests;
- observer id/generation, stream id/epoch, position and predecessor;
- aggregate class and revision, never aggregate alias or resolved identifier;
- observation digest and key id, never raw event id or key material;
- closed decision and reason codes;
- conservative affected frame types plus closed buckets for retired,
  coalesced and backlog counts;
- checkpoint before/after or held disposition;
- lifecycle revision and backend-authored recorded instant; and
- prior audit-record digest for tamper-evident chaining.

Audit contains no event payload, appointment/practitioner/location/time value,
patient or clinical data, actor identity, command/audit correlation from the
producer, active session inventory, frame contents, raw alias, provider output
or free text. It is not Bureau Memory, current context, a read grant, a command
receipt or proof of fresh truth.

## Authored-synthetic architecture contract

This tranche may add one closed JSON contract and Draft 2020-12 schema covering:

- the exact source/event/stream profile;
- the three logical principals and their authority ceilings;
- rollback-safe transactional head and payload-free projection fields;
- checkpoint state and atomic transaction invariants;
- decision-specific checkpoint dispositions;
- restart, gap, overflow and retention behavior;
- key schedule and rotation failure behavior;
- privacy-safe audit allowlist; and
- every forbidden live/runtime surface.

The contract is declarative architecture evidence. It is not a migration,
database configuration, credential, policy switch, executable manifest or
runtime checkpoint.

## Data, provider, cost and licence posture

- Data: architecture language and newly authored synthetic opaque metadata
  only; no patient, clinical, financial, product-derived, protected or
  historical-PHI data is read or processed.
- Provider/external retrieval: none.
- Cost: zero provider/cloud cost.
- Licence: no external content or corpus.

## Allowed side effects

Repository writes are limited to this plan, its design and threat-model delta,
one closed authored-synthetic architecture contract/schema, deterministic
tests, review evidence and later closeout/acceptance/continuity references.
There is no filesystem runtime, source read, database, network, subprocess,
provider, listener, command or product effect.

## Forbidden surfaces

No `app/**`. No `alembic/**`. No `docs/diary/**`, API schema or mounted route. No
GraphQL field/subscription/mutation, REST/OpenAPI operation, database migration,
table, view, function, trigger, sequence, role or credential. No outbox, feed,
watcher, listener, broker, scheduler, worker, checkpoint store, persistence,
operational cursor movement, product/source read, patient/product/protected
data, raw audit, provider/external retrieval, command/write, runtime wiring,
deployment, production, release, Pages or protected-ref movement. Preserve and
exclude `docs/branding/` and every unrelated untracked receipt, state, evidence
or cost-ledger file.

## Acceptance

1. The source is exactly `diary.appointment_rescheduled.v1`; the existing UI
   delivery cursor and payload-bearing event remain explicitly ineligible.
2. The logical observation integration principal is exact, read-only on a
   future payload-free projection and cannot access source payload/product
   tables or persist state.
3. A distinct durability coordinator has only the narrow future atomic-state
   boundary; the later application principal alone may perform fresh reads.
4. The outbox position uses a transactionally updated per-practice/stream row,
   never a PostgreSQL sequence/identity, timestamp, UUID, transaction id or LSN.
5. Head update and control-row append are atomic with the existing command,
   audit, idempotency and committed-event transaction; rollback creates no
   phantom position.
6. The control projection is recursively closed and payload-free and exposes no
   direct appointment, practitioner, location, time, actor, correlation or
   reason value.
7. Baseline and every source/frame/checkpoint binding include exact stream,
   epoch, observer generation, source-contract and controlling digests.
8. Decision receipt, monotonic invalidation, one coalesced obligation, audit and
   positive checkpoint advancement commit or roll back together.
9. Full invalidation caused by known contiguous input may advance only after
   durable retirement; coverage gaps hold the last contiguous checkpoint and
   consume the generation for rebaseline.
10. Duplicate/redelivery is exact and idempotent; mismatched same-position or
    same-observation/different-position values are corruption.
11. Restart resumes only from a verified durable checkpoint and exact next
    retained row; uncertainty never reuses current frames.
12. Every dependent frame generation cites source epoch, observer generation
    and `assembled_through_position`; currentness derives from the durable
    watermark, and later replacement reads are source-head fenced.
13. Retention is gated by the minimum eligible checkpoint, key overlap, pins
    and safety grace; the existing 24-hour event expiry has no durability role.
14. Overflow/backpressure never samples invalidation truth or silently advances
    a checkpoint.
15. Key rotation uses non-overlapping position intervals, preserves prior keys
    through verification overlap and fails closed to rebaseline when continuity
    cannot be proved.
16. Audit is closed, payload/PHI-free, count-minimized and cannot reveal active
    sessions or become context/read/command evidence.
17. The authored-synthetic contract/schema are exact and mechanically valid;
    adversarial changes to position, principal, authority, retention, key or
    audit invariants fail deterministic tests.
18. Static checks prove that no API, app, migration, database, source, listener,
    provider, command, runtime, deployment, Pages or protected-ref surface was
    added.
19. The claim remains architecture-only and names a separate later migration,
    credential and live-runtime gate.

Evidence label:
`provider_free_unmounted_authored_synthetic_source_specific_durability_architecture`.

## Recovery and stop

Any ambiguity over source ordering, rollback gaps, product payload exposure,
principal inheritance, atomicity, checkpoint advancement, restart, retention,
key rotation or audit minimization requires architecture revision before
acceptance. A deterministic schema/test defect may receive one bounded
mechanical correction. A competing user-owned privacy, reliability or
operational outcome is a genuine fork; none is presently identified.

## Claim boundary and next dependency

Passing proves only a provider-free, unmounted, authored-synthetic durability
architecture. It proves no table or migration, source observation, event
delivery, credential, database isolation, transaction implementation,
checkpoint persistence, crash recovery, retention capacity, real invalidation,
fresh product read, patient privacy enforcement, provider behavior, command
safety, deployment or production operation.

After acceptance, the next architecture-strengthening descendant is a pure
provider-free unmounted authored-synthetic durability state-machine rehearsal
over the closed contract. It may prove decision-specific atomic state
transitions, redelivery, gap/rebase, key-boundary and retention eligibility in
memory only. Any migration, database/outbox connection, operational credential,
live observer, product read or runtime wiring remains a separately frozen gate.
