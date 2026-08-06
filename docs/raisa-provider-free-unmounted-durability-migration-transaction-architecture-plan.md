# Provider-free unmounted durability migration-and-transaction architecture plan

Date: 2026-08-06

Status: sixth recovered architecture plan candidate pending fresh independent veto

Parent result:
`raisa_provider_free_unmounted_authored_synthetic_durability_state_machine_rehearsal_pass`

## Objective

Freeze the narrowest future PostgreSQL realization of the accepted pure
durability state machine for the patient-free
`diary.appointment_rescheduled.v1` control family. This tranche specifies the
future schema catalogue, tenant and principal boundaries, transaction and lock
semantics, rollback and recovery behavior, key/credential binding constraints,
retention safety relation and database-backed authored-synthetic acceptance.

The intended result is
`raisa_provider_free_unmounted_durability_migration_transaction_architecture_pass`.

This tranche is declarative, provider-free and unmounted. It creates no
migration, database object, SQL role, credential, source connection, runtime or
product data path.

No applied migration exists or is authorised by this tranche.

## API Spine classification

This is internal async durability architecture only:

- GraphQL remains read-only and unchanged;
- REST/OpenAPI remains the only command plane and gains no operation;
- the existing signed appointment update-confirm command remains the only
  mutation that may later produce this exact control family;
- the existing staff committed-event GET route, time/event cursor and
  appointment-bearing response remain unchanged and are ineligible as the
  observer source or durability checkpoint;
- the future payload-free control row is an atomic side effect of the existing
  producer transaction, not a new command, API, truth source or success proof;
- no subscription, acknowledgement, generic database procedure, retention
  endpoint, event-triggered command or event-triggered fresh read is added; and
- every later fresh product read remains a new application-principal decision
  under a current no-wider `ContextScopeGrant`.

The authoritative API references are `orchestration/api_spine_adr.md`,
`orchestration/api_spine_programme.md`,
`docs/api-spine/async/integration-events.yaml`,
`docs/api-spine/openapi/diary-committed-events.yaml` and
`docs/api-spine/graphql/practice-context-fabric-read.graphql`. No nonexistent
API Spine README may be claimed as evidence.

## Frozen architecture surface

This tranche may add only:

- this plan, one design and one threat-model delta;
- one closed declarative architecture contract and JSON Schema under a new
  `orchestration/continuity/` directory;
- static and schema-focused tests;
- bounded read-only analysis/review artifacts; and
- later closeout, acceptance and Continuity/Compass artifacts.

No `app/**`, `alembic/**`, `docs/diary/**`, API Spine contract, runtime
configuration, existing database model or existing source adapter may change.
The architecture contract is not executable DDL or a deployment manifest.

## Non-inheritance and data ceiling

Only the exact patient-free control projection already accepted by the parent
may be represented. It may contain closed practice/source/stream/generation
coordinates, exact positions and predecessors, opaque backend aliases and
digests, aggregate revision metadata, closed decision/reason/frame codes,
key ids and integrity metadata.

The sole product-identifier exception is the owner-private
`diary_context_aggregate_aliases_v1` bridge described as relation 2 below. It
contains exactly one practice-bound product appointment UUID solely to maintain
one stable opaque aggregate alias across producer transactions. That UUID is
not control projection content and is never selectable by the observer,
admission receiver, coordinator, lifecycle, retention or application-read
principals. No other future relation may contain an appointment, patient,
practitioner, location, time-slot, actor, session, correlation, command, audit-
correlation, provider, payload, free-text, raw product UUID or current-truth
value. JSON/JSONB, unbounded text, arrays and arbitrary key/value metadata are
forbidden in every future relation. Exact closed codes use enum/domain/check
constraints. A compact affected-frame mask may encode only none, Diary, waiting
room or both.

## Exact future schema catalogue

The later migration may create one dedicated schema owned by a non-login,
non-runtime owner. The architecture contract must freeze the following logical
relations and no generic work queue or event store:

1. `context_observation_stream_head` — one row per `(practice_id, stream_id)`;
   exact stream epoch and last committed position. It carries no observer HMAC
   digest: the producer neither holds the observer key nor manufactures a
   classified observation.
   Epoch is fixed to `1` for this source-contract version. Position zero is the
   empty baseline. The position is a checked signed
   64-bit integer; overflow fails the producer transaction and consumes the
   epoch. No sequence or identity default is allowed.
2. `diary_context_aggregate_aliases_v1` — the sole product-identifier exception:
   an immutable owner-private mapping keyed by
   `(practice_id, source_contract_id, product_appointment_uuid)` to one opaque
   aggregate alias, with reverse uniqueness on
   `(practice_id, source_contract_id, opaque_aggregate_alias)`. The source
   contract is exactly `diary.appointment_rescheduled.v1`; the caller cannot
   supply the alias. The owner generates it inside the single producer
   projection entry point described below. Rows permit neither update nor
   deletion for this contract epoch. A concurrent same-appointment create must
   reload and return the exact existing alias; a cross-appointment collision
   fails the entire command transaction. No separately executable alias helper
   is granted to a runtime principal and no runtime principal receives direct
   table DML. Observer, admission receiver, coordinator, lifecycle, retention
   and application-read principals receive neither `SELECT` nor the product
   id. The product UUID is never copied into the outbox, admission, receipt,
   checkpoint, anchor, audit, key or retention relations.
3. `diary_context_observation_outbox_v1` — immutable payload-free source rows keyed by
   `(practice_id, stream_id, stream_epoch, transaction_position)`, with exact
   predecessor, one non-semantic raw event UUID, opaque aggregate alias/revision,
   source-contract digest and transaction-authored instant. The raw event UUID
   is also unique within the exact practice/source contract, so one committed
   command event cannot allocate two positions. It is visible only to the narrow
   observer, is domain-separated into the accepted
   observation digest and is then discarded; it never reaches receipt or audit.
   The predecessor is zero only at position one and otherwise exactly position
   minus one. Stream epoch is fixed to `1` for this source-contract version.
4. `context_proofread_observation_admission` — immutable, receiver-owned,
   bounded attempt rows keyed by the full observer-generation coordinate,
   source position and closed entry kind. The relation permits at most one
   `PRIMARY` plus at most one `CONFLICT` sentinel for that position. One
   hardened admission entry point rederives the actual observer `session_user`.
   For a first `PRIMARY` it reselects the exact payload-free source row,
   validates its coordinate, predecessor, aggregate revision and generation-
   local key interval, and binds those facts to the closed proofread packet and
   its admission digest. A `CONFLICT` stores only the authenticated binding and
   source coordinate, attempted admission digest and a closed conflict reason;
   it contains no copied packet. Neither entry kind stores a raw event UUID,
   aggregate alias, payload, free text or product identifier. The observer
   receives no direct DML and the coordinator may use only the complete stored
   admission set, never a caller-supplied decision packet. A `CONFLICT` grants
   no positive decision meaning and is sufficient only for fail-closed rebase.
5. `context_generation_registry_barrier` — one lock/barrier row per exact
   practice/source/stream. Generation registration/rebaseline and later source
   retention must serialize on it.
6. `context_observer_generation` — backend-complete generation registry keyed
   by practice/source/stream/epoch/observer/generation, with closed lifecycle
   and controlling policy, principal, binding, source, registry, impact and
   generation-local key-schedule digests. The lifecycle role, not the
   coordinator, creates or consumes a generation.
7. `context_durability_checkpoint` — exactly one state row per observer
   generation, carrying `ACTIVE`, `REBASE_REQUIRED`, `REVOKED` or `CONSUMED`,
   the last contiguous classified position/digest, lifecycle revision, audit
   head digest and integrity metadata.
8. `context_recovery_anchor` — append-only lifecycle-owned rows keyed by the
   full generation coordinate plus lifecycle revision. Each freezes the exact
   committed checkpoint/state digest, last contiguous position/digest and all
   controlling digests. Baseline and every later decision/rotation checkpoint
   require their own anchor. The coordinator cannot create, rewrite or delete
   one, and it cannot process the next lifecycle transition until an exact
   anchor matches the current checkpoint.
9. `context_classified_observation_receipt` — immutable receipt keyed by the
   full generation coordinate plus position, with observation digest,
   decision, reason, affected-frame mask, checkpoint disposition and lifecycle
   revision. Observation digest is unique within the generation so reuse at a
   different position is corruption.
10. `context_frame_generation` — opaque generation id, exact closed frame type,
   assembled-through position and one-way `CURRENT`/`RETIRED` lifecycle. A
   retired frame cannot become current.
11. `context_invalidation_watermark` — one row per generation and closed frame
   type; its position is monotonic and cannot exceed the classified
   checkpoint. It never stores replacement facts.
12. `context_reassembly_obligation` — at most one pending obligation per frame
   generation, with earliest/latest positions, bounded rolling cause digest,
   and closed public count bucket. The coordinator derives the exact count and
   bucket from canonical admitted audit history under the checkpoint lock;
   callers cannot supply either and no convenience counter is persisted.
13. `context_durability_lifecycle` — one immutable total-order journal for both
     `DECISION` and `KEY_ROTATION` entries. Its revisions cover exactly every
     lifecycle revision after the baseline without gaps or reuse, removing any
     ambiguity between audit and rotation chronology.
14. `context_durability_audit` — immutable minimized typed rows keyed by full
     generation coordinate plus lifecycle revision, with prior/head digest and
     one-to-one linkage to `DECISION` lifecycle entries and only the accepted
     closed metadata. It is not Context Fabric content,
     Bureau Memory, current truth, command evidence or cryptographic proof.
15. `context_observation_key_interval` — generation-local metadata keyed by the
     full observer-generation coordinate, with ordered, gap-free, non-overlapping
     inclusive-start/exclusive-end position intervals and opaque key ids. One
     deferred exact constraint or owner transaction entry point must prove the
     complete partition for that generation. No key bytes, cloud key resource
     or credential is stored.
16. `context_recovery_pin` — independently owned closed pins over source,
     receipt/checkpoint or audit retention families. Pins have typed reason and
     lifecycle codes, never free text or product identity.
17. `context_service_practice_binding` — exact authenticated database login,
     logical capability, practice, source family, binding revision and active
     interval. It contains no secret and is authoritative only when read inside
     a hardened database entry point from the actual authenticated session.
18. `context_retention_policy` — versioned safety constraints and disabled-by-
     default executor state for the three independent retention families.
    Production durations, capacity and key-store selection remain later
    operational decisions.

Every primary, unique and foreign key of a tenant-bearing relation includes
non-null `practice_id` and the full necessary source/generation coordinate.
Cross-practice foreign keys are impossible. Source-row deletion never cascades
to admission, anchor, receipt/checkpoint, audit, generation, pin or key-schedule
state. A position's `PRIMARY` and `CONFLICT` admission rows share the receipt/
checkpoint retention family and are retained together. Neither can be removed
while its receipt, checkpoint, restart, redelivery or conflict meaning remains
retained. The owner-private alias bridge is not governed by the three
durability retention families and is never an input to their purge decision.
Update and deletion are prohibited for this v1 source-contract epoch, so a
product UUID cannot be deleted and recreated with a different alias and an
opaque alias cannot be reused. Any future erasure/non-reuse design requires a
new separately reviewed migration/contract descendant and source epoch. The
bridge never cascades and cannot remove or rewrite an opaque alias already
present in retained durability evidence.

## Ownership, role and binding model

The future design must separate these logical planes:

- schema/table owner: `NOLOGIN`, not a runtime role and not `BYPASSRLS`;
- producer: one future database capability bound exclusively to the existing
  signed appointment update-confirm command path. The command and its one exact
  owner-mediated projection entry point use one physical connection, one
  transaction, one logical capability and one `session_user`; there is no
  second login, role switch, separately executable alias helper or direct
  bridge/head/outbox table privilege;
- observer: exact practice/source scoped read of the closed payload-free
  projection only;
- observation admission receiver: one authenticated, source-revalidated,
  immutable proofread-packet admission only; the observer has no direct DML;
- durability coordinator: one typed atomic durability transition only;
- generation lifecycle/anchor authority: generation and independent recovery
  anchor creation/consumption only;
- retention evaluator/executor: database-derived eligibility and a separately
  gated source-row purge only; disabled by default; and
- application read principal: separate current-truth reads only under existing
  application authorization.

Runtime roles are `NOINHERIT`, cannot `SET ROLE` into another plane, do not own
objects, are explicitly `NOBYPASSRLS`, do not have `CREATEROLE`, schema create or generic SQL
authority, and inherit no public/default privileges. `PUBLIC` receives no
schema use, function execute or table privilege.

All tenant relations enable and force RLS, but RLS must not trust a caller-set
custom GUC or packet `practice_id` alone. A resource-locator `practice_id`
argument grants no authority. Exact connection login/capability/practice/source
binding is rederived from `session_user` against the backend binding registry
inside each narrow entry point. One credential-bearing login has exactly one
active logical capability/practice/source/credential-epoch binding. An absent,
inactive, duplicate, ambiguous or mismatched binding denies the operation.
Connection pooling may not multiplex different practices, capabilities or
credential epochs through one bound login, and reset/reuse must preserve this
separation mechanically.

Any later security-definer entry point must be owned by a non-login role, have
a fixed schema-qualified search path, use no dynamic SQL, derive session
identity before acting, revoke `PUBLIC` execute and expose no generic table or
SQL operation. Direct table DML is denied to observer, admission receiver,
coordinator, lifecycle and retention logins except for the exact capability
mediated by their entry point. The observer may execute only the receiver's
closed admission function; this is candidate submission, not generic
persistence or durability-state authority. Static acceptance must prove that a
forged `app.current_practice_id` cannot widen scope.

## Producer transaction and position allocation

The future producer remains the existing signed appointment update-confirm
transaction. At `READ COMMITTED`, its fixed lock/effect order is:

1. claim/read the existing idempotency result under its accepted contract; a
   new command inserts one exact `IN_PROGRESS` row in this transaction for
   `confirmAppointmentUpdateProposal` / `update-confirm`, bound to the practice,
   actor, idempotency-key digest and immutable request-body digest of the signed
   confirmation envelope. Replay, conflict, stale or any previously committed
   `IN_PROGRESS` row is ineligible to produce;
2. lock, authorize and update the exact appointment aggregate;
3. append the existing appointment audit and committed event, populate the
   claim's existing `target_appointment_id` and `audit_log_id` while it remains
   `IN_PROGRESS`, and rely on the event's existing practice-scoped
   `(practice_id, command_id)` foreign key plus unique `command_id` constraint
   to bind the sole event to that claim. No invented event-id or aggregate-
   revision column is added to the idempotency row;
4. invoke one exact owner-mediated producer projection entry point. It rederives
   the actual producer `session_user` and practice/source binding, locks and
   revalidates the exact `IN_PROGRESS` operation/route/request-digest claim,
   loads the sole `DiaryCommittedEvent` row through that binding, and
   verifies its exact reschedule type/schema, appointment, audit and aggregate
   revision against the claim and locked product state. It also compares the
   claim, current appointment tuple version, audit and event `xmin` values with
   the PostgreSQL-16 top-level XID32 expression frozen below and verifies the
   immutable claim `created_at` equals this transaction's start. Savepoints,
   nested transactions and subtransaction-authored members are forbidden from
   claim insertion until outer commit. A completed, previously
   committed, absent, duplicate, foreign, mismatched or caller-substituted
   context fails before any bridge/head/outbox effect;
5. inside that same entry point, create or return the immutable bijective alias,
   lock the exact `(practice_id, stream_id)` head row `FOR UPDATE`, compute
   `position = last_position + 1` and `predecessor = last_position`, append the
   payload-free control row and advance the stream head; and
6. complete the existing idempotency result, then satisfy the deferred commit
   fence described below before one transaction commit.

The alias operation is an owner-private subroutine of that single projection
entry point; it has no separately grantable runtime execute path. The command
does not open a second connection, change login, `SET ROLE` or cross a second
capability boundary before projection. Appointment truth, command audit,
idempotency completion, committed event, alias creation, payload-free control
row and stream-head advance commit or roll back together.
Failure, collision or lock timeout in any member fails the whole command safely;
there is no silent bypass or persistent alias-only effect. Disabling an already-
producing contract consumes its observer generations; re-enable requires a new
explicit source-contract epoch/version rather than silently incrementing this
version's fixed epoch. The producer may know the appointment UUID because it
already owns the signed command transaction, but only the opaque alias crosses
into the control projection or any observer/coordinator surface.
After any emitted row, migration rollback is forward-fix and data-preserving;
no downgrade may drop, truncate or silently stop the projection.

### Transaction-local provenance and deferred commit fence

The later inert DDL must target PostgreSQL 16 and render this exact top-level
comparison; an implementer may not choose a different cast:

```sql
xmin = ((((pg_current_xact_id()::text)::bigint & 4294967295)::text)::xid)
```

`pg_current_xact_id()` supplies epoch-aware `xid8`; the mask deliberately
extracts its low 32-bit transaction id before the explicit text-to-`xid` cast.
That equality is used only while the same top-level transaction is active and
only together with all of these facts: the exact claim was inserted in this
transaction, its server-default `created_at` equals `transaction_timestamp()`,
the pre-enable census contains zero committed exact-operation `IN_PROGRESS`
rows, state cannot transition back to `IN_PROGRESS`, and no exact-operation
`IN_PROGRESS` row can commit. Savepoints, `Session.begin_nested()`, explicit
`SAVEPOINT`/`ROLLBACK TO` and any subtransaction around claim, appointment,
audit, event, projection or completion are forbidden; a subtransaction-
authored tuple is rejected rather than normalized. Wrap/freeze cannot authorize
an old row because no committed eligible row survives and the comparison is
neither stored nor used after commit.

`xmin` and XID are permitted only inside the narrow producer entry point and
guard/constraint functions. They are database-derived, never caller-supplied,
stored in a user column, copied into a digest or outbox, retained, exposed to
an observer, or used as the durable position.

The exact temporal obligation is the existing source condition:
`OLD.start_time IS DISTINCT FROM NEW.start_time OR
OLD.duration_minutes IS DISTINCT FROM NEW.duration_minutes`. Practitioner,
reason, notes, status and other fields do not broaden this v1 family. When the
exact producer binding is active, a temporal update-confirm must commit exactly
one matching reschedule event and projection; a non-temporal update-confirm
must commit neither. This predicate is database-derived from the `appointments`
transition, never caller-supplied or inferred from a feature flag. Before
binding activation the guards are inert; activation is permitted only after
the application hook and zero-legacy census pass together.

Owner-only fixed-search-path immediate guards and `DEFERRABLE INITIALLY
DEFERRED` constraint triggers cover the exact event surface:

- `appointment_command_idempotency`: immediate `BEFORE UPDATE OR DELETE`
  state/provenance guard plus deferred `AFTER INSERT OR UPDATE OR DELETE`
  completeness;
- `appointments`: deferred `AFTER UPDATE OF start_time, duration_minutes`
  temporal-obligation check with `OLD`/`NEW` transition values;
- `appointment_audit_log` and `diary_committed_events`: immediate `BEFORE
  UPDATE OR DELETE` immutability plus deferred `AFTER INSERT OR UPDATE OR
  DELETE` completeness;
- `diary_context_aggregate_aliases_v1` and
  `diary_context_observation_outbox_v1`: immediate `BEFORE UPDATE OR DELETE`
  immutability plus deferred `AFTER INSERT OR UPDATE OR DELETE` completeness;
  and
- `context_observation_stream_head`: immediate `BEFORE DELETE` and rollback/
  monotonicity guard plus deferred `AFTER INSERT OR UPDATE OR DELETE`
  completeness.

Insert-then-delete sequences remain visible to queued constraint-trigger
events, while immediate delete guards prevent immutable members disappearing.
At commit the bidirectional invariants require:

- a temporal appointment transition has the exact newly inserted then
  completed claim, target appointment and audit, exactly one immutable event,
  one outbox row and matching stream-head advance;
- a non-temporal transition has its completed claim/audit but no reschedule
  event, alias insertion, head advance or outbox row;
- every event has that temporal transition, completed claim, target/audit,
  outbox and head advance;
- every outbox has that event/result, and any alias first inserted in the
  transaction is referenced by that outbox;
- no exact claim can commit in `IN_PROGRESS`, revert to `IN_PROGRESS`, be
  deleted in its creation transaction or adopt target/audit/completion when its
  prior tuple was not created by the same top-level transaction; and
- appointment mutation, audit, event when required, first alias when required,
  head advance when required, outbox when required and idempotency completion
  all commit once or all roll back.

The producer cannot disable or defer the fence beyond transaction end, invoke
the private trigger functions, supply an XID, or convert a previously committed
claim/event into current provenance. Trigger functions use the same non-login
owner, fixed schema-qualified search path, no dynamic SQL and no `PUBLIC`
execute. A transaction-local comparison is evidence of atomic co-authorship,
not durable ordering, cryptographic signature verification or authority beyond
the already authenticated REST command.

PostgreSQL sequences/identities, UUID/time ordering, retained `xmin`, transaction id,
commit timestamp, WAL LSN, the existing `(occurred_at,event_id)` cursor and
`aggregate_revision` are all ineligible as the durability position.

## Authenticated admission transaction

The observer never hands an unauthenticated packet to the coordinator. Through
one narrow receiver-owned entry point at `READ COMMITTED`, the actual observer
`session_user` is resolved to exactly one active observer/practice/source/epoch
binding. The receiver first locks and loads the complete retained admission set
and receipt for the exact generation and position. This retained-evidence-first
comparison is deliberately before source selection. If a `PRIMARY` already
exists, an exact authenticated admission-digest resubmission returns it without
source access; a mismatch appends or returns the sole bounded `CONFLICT`
sentinel even after an independently authorised source purge.

Only when no `PRIMARY` or `CONFLICT` exists does the receiver reselect the exact
immutable source row, validate its coordinate, predecessor and aggregate
revision, verify the packet's generation-local key id/interval and closed
schema, and append the `PRIMARY`. Its admission digest binds the observer
principal/binding, complete generation coordinate, source-membership digest and
proofread decision packet. Observation-digest reuse at a different position
appends a conflict-only sentinel at the attempted coordinate after the same
authenticated source-membership checks. Raw UUID/alias values are discarded at
the receiver boundary and never enter either entry kind.

The observer has no table DML, coordinator function or checkpoint privilege.
The receiver has no decision-effect, checkpoint, fresh-read or command
authority. The unique key and closed entry kind allow at most one `PRIMARY` and
one `CONFLICT` per position: exact duplicates are inert, the first mismatch or
digest reuse becomes durable receiver-authored conflict evidence, and later
conflicting attempts cannot grow storage without bound. No attempt overwrites
an immutable row. If concurrent first attempts race on the unique `PRIMARY` or
generation-local observation-digest constraint, the receiver reloads the
committed winner: equality is inert and inequality appends or returns the sole
`CONFLICT`; `ON CONFLICT DO NOTHING` is not an outcome. Database transport
authentication/channel protection and credential provisioning remain a later
operational gate; this architecture does not claim they have been implemented
or cryptographically proven.

## Coordinator transaction, isolation and lock order

The future coordinator operates at `SERIALIZABLE` through one narrow typed
entry point. A caller may provide only an admission locator; all decision and
authority values are reloaded from the immutable admitted row. Inside the
transaction it:

1. rederives session binding;
2. locks the exact generation registry barrier in the common global order;
3. locks the exact generation/checkpoint row `FOR UPDATE`;
4. verifies that the latest lifecycle-owned recovery anchor exactly matches the
   current checkpoint; an absent/pending/mismatched anchor permits no next
   transition;
5. loads the complete stored admission set and any existing receipt by locator.
   Any retained `CONFLICT` sentinel is durable corruption evidence and forces
   the atomic rebase path before exact-redelivery success. Otherwise exact
   receipt/`PRIMARY`/observation-digest equality returns the receipt without
   source access or mutation;
6. when no receipt exists and no conflict exists, loads and verifies the exact
   immutable `PRIMARY`, its authenticated observer/binding, source-membership
   digest, key interval and full coordinate; it never accepts a caller-supplied
   decision packet or reads the raw source UUID/alias;
7. derives contiguity, corruption and every canonical effect;
8. stages receipt, watermarks, one-way retirement, coalesced obligation,
   `DECISION` lifecycle row, minimized audit and checkpoint disposition; and
9. commits all members together or rolls all back.

The lock order is binding check, registry barrier, observer generation/
checkpoint, current recovery anchor, retained admission/receipt, key intervals,
then dependent rows in stable primary-key order. Producer, admission receiver
and coordinator never acquire each other's head/checkpoint locks in reverse
order.
Different practices and different observer generations do not share a global
lock.

Exact same-position/same-admission/same-digest redelivery returns the stored
receipt and makes no change even after the independently eligible source row is
purged, provided no conflict sentinel exists. `ON CONFLICT DO NOTHING` alone is
forbidden. A stored same-position mismatch or digest-reuse sentinel, wrong
predecessor/epoch, missing required primary admission, unknown key or a
demonstrated admitted-position gap holds the last contiguous checkpoint, fully
invalidates and moves the generation to `REBASE_REQUIRED` atomically. A source
row that simply has not yet produced an admission is ordinary waiting, not a
fabricated gap.

Deadlock and serialization retries are permitted only for exact PostgreSQL
retryable SQLSTATEs, over the complete transaction, with the same idempotency
key/coordinates and at most three attempts with bounded jitter outside any
transaction. An unknown producer commit outcome is
resolved through existing idempotency readback, never blind replay. A
coordinator retry is safe only because exact redelivery is inert.

## Independent recovery anchors

Generation anchors are append-only immutable lifecycle-owned rows, not
coordinator input or fields copied into the generation registry. An anchor
binds practice/source/stream/epoch, observer generation, lifecycle revision,
checkpoint integrity/state digest, baseline and last trusted contiguous
coordinate plus all controlling digests. Lifecycle authority creates the
baseline anchor before activation and a new anchor only after independently
verifying each fully committed decision or rotation state. The coordinator
cannot process the next lifecycle transition until the newest checkpoint has
one exact anchor.

A crash after a coordinator/rotation commit but before its independent anchor
cannot skip ahead. The lifecycle authority may complete the pending anchor only
after re-verifying the entire committed receipt/lifecycle/audit/checkpoint state;
otherwise restart returns `NEW_GENERATION_REQUIRED`. While an anchor is pending,
receiver-owned immutable `PRIMARY` or `CONFLICT` admission appends may continue,
but the coordinator cannot consume the next admission and no next decision or
rotation lifecycle transition may begin. The anchor is never inferred from the
coordinator's candidate state.

Missing, stale, rewritten or mismatched anchors return
`NEW_GENERATION_REQUIRED`; verified states with missing/retained-row or key
continuity failure return `REBASE_REQUIRED`. No path adopts a coordinate from
untrusted state or an older frame as current.

## Key and credential boundary

Observation identity uses a dedicated domain-separated key family, never the
application secret, authentication credential, provider credential or database
login. The database stores only key ids, immutable position intervals and
availability attestations from the separately bound key authority. It never
stores key bytes or tries every key.

Each key schedule belongs to exactly one observer generation. Routine rotation
runs as one `SERIALIZABLE` transaction over that generation's registry barrier,
checkpoint, current recovery anchor and interval partition. It is future-
fenced, changes no historical interval, appends exactly one `KEY_ROTATION`
lifecycle row, advances the checkpoint's schedule digest/lifecycle revision and
retains the predecessor key through all dependent source/admission/receipt/audit
rows plus the safety overlap. It changes no other generation. The next decision
is blocked until lifecycle authority appends the matching independent recovery
anchor. Gap, overlap, retroactive edit, missing key, insufficient overlap or
emergency revocation consumes that exact generation. Credential/key
creation, cloud resource selection and secret administration remain later
operational gates.

## Retention safety and backpressure

Source rows, receipts/checkpoints and minimized audit are three independent
retention families. The existing 24-hour event expiry and a fast consumer have
no durability meaning.

Any later source eligibility/execution transaction runs at `SERIALIZABLE` and
must lock the exact
generation registry barrier also used by registration/rebaseline, then derive
the complete non-consumed generation census inside the database. Eligibility
requires the slowest checkpoint at or beyond the position, no relevant
recovery/audit pin, closed predecessor-key dependency/overlap and elapsed
policy grace. The caller cannot supply/filter the census, expected digest,
minimum checkpoint, pin state, key state or clock result.

Registration concurrent with purge therefore cannot be omitted. Missing,
duplicate, ambiguous, inactive-authority or unverifiable state denies purge.
No cascade couples the three retention families. The architecture freezes
`retention_execution_enabled: false`; a later gate must choose production
duration/capacity, prove key-store availability and separately authorize the
executor. Capacity pressure never silently drops rows: it blocks/retries the
producer or consumes affected generations and requires rebaseline under a
later accepted operational policy.

## Migration, enablement and rollback sequence

The later implementation must be expand-first and default-off:

1. create closed types/relations/constraints/RLS/owners with public/default
   privileges revoked and no runtime login binding;
2. install narrow entry points and prove static/database acceptance while the
   producer and consumers remain disabled, including a zero census of legacy
   committed exact update-confirm `IN_PROGRESS` rows before the transaction
   guard can be enabled;
3. bind exact operational identities only under a separate credential gate;
4. establish one explicit practice/source/generation baseline, stream epoch and
   lifecycle-owned baseline anchor;
5. enable the producer atomically for that exact boundary;
6. enable the observer and admission receiver for that exact binding only after
   source/admission acceptance passes; then
7. enable the coordinator only after immutable admissions and baseline/post-
   transition anchors are admitted by database-backed authored-synthetic
   acceptance.

Before first production row, rollback may remove unused objects under a later
authorized migration. After first row, rollback is non-destructive forward-fix;
disabling production consumes the epoch. No code rollback may allow the
appointment command to commit without its required control row.

## Database-backed authored-synthetic acceptance design

The later implementation gate must use a disposable local database and newly
authored synthetic opaque coordinates only. At minimum it must prove:

1. rollback after every producer member, including alias insertion/collision,
   leaves no appointment change, success-idempotency result, event, alias row,
   control row or consumed position; direct projection invocation without the
   exact bound `IN_PROGRESS` update-confirm claim, its target/audit bindings and
   the sole unique-command event matching the locked appointment/revision is
   rejected with zero bridge/head/outbox effect; the command and projection are
   also proven to use one logical capability and one `session_user` without a
   second login, role switch or transaction; a previously committed or merely
   updated `IN_PROGRESS` claim/event fails the current-XID/immutable-created-at
   check, every savepoint/subtransaction attempt is rejected, and every event/
   outbox/alias/claim partial or insert-then-delete combination fails the
   immediate/deferred fence with no durable effect; a temporal start/duration
   transition without event/projection fails while a non-temporal exact update-
   confirm completes without event, alias, head or outbox effect;
2. concurrent same-stream producers yield contiguous unique positions and
   different practices share no counter;
3. duplicate idempotency yields one mutation, one immutable alias and one
   control row; concurrent same-appointment alias creation converges on that
   exact alias, different appointments cannot share one practice/source alias,
   collision rolls back, caller alias selection fails, update/delete/recreate
   fails and altered idempotency reuse conflicts;
4. only the exactly bound observer login can invoke admission; the receiver
   revalidates source membership and a coordinator-supplied decision packet is
   rejected;
5. exact admission resubmission is inert before and after source purge, while a
   same-position packet mismatch or observation-digest reuse appends one
   durable receiver-authored conflict sentinel, never replaces the primary,
   remains visible after source purge and bounds the position to at most two
   admission rows; concurrent first-primary and first-conflict races converge
   on the same bounded set without suppressing a mismatch;
6. concurrent coordinators serialize and exact redelivery is inert;
7. exact receipt/primary redelivery still succeeds after authorized source-row
   purge and performs no source access, while any retained conflict sentinel is
   loaded through the same locator and forces rebase before redelivery success;
8. same-position mismatch, digest reuse, demonstrated admitted-position gap,
   wrong predecessor/epoch, missing required admission and key loss hold the
   checkpoint and require rebase;
9. aggregate-revision jumps, duplicates and reversals never act as position;
10. failure after each coordinator member, including lifecycle append, rolls
    back every durability effect;
11. cross-practice reads, writes, foreign keys and claimed scope fail;
12. every logical role fails every forbidden operation, including inheritance,
   `SET ROLE`, `BYPASSRLS`, owner and unsafe security-definer paths; the producer
   cannot execute an alias-only helper or directly mutate bridge/head/outbox;
13. caller-set practice GUC, packet practice and direct function argument cannot
    widen the authenticated binding;
14. JSON/text/direct identifier/raw UUID/correlation/session/payload smuggling
    fails at schema and entry-point boundaries outside the exact owner-private
    alias bridge; every non-producer principal and every durability output is
    denied the bridge UUID;
15. baseline, post-decision and post-rotation anchors are append-only and
    lifecycle-owned; pending/crash/tampered/missing anchors block coordinator
    consumption and every next decision/rotation transition without blocking
    bounded receiver-owned admission appends, and cannot resume unverified
    state;
16. one generation's future-fenced rotation changes no other generation and its
    `KEY_ROTATION` lifecycle/checkpoint effects are atomic;
17. incomplete/filtered census, fast checkpoint, active pin, unfinished key
    overlap/grace and concurrent generation registration deny purge;
18. source eligibility/execution cannot cascade to admission/anchor/checkpoint/
    receipt/audit or the owner-private alias bridge; v1 bridge update/deletion
    is prohibited and cannot alter retained opaque evidence;
19. disabled mode performs zero connection, credential acquisition or state
    movement;
20. the existing staff route/cursor cannot satisfy observer/checkpoint
    authority;
21. no GraphQL mutation/subscription, REST command/route, acknowledgement or
    event-triggered fresh read appears; and
22. database constraints and digest chains are described only as integrity and
    tamper-evidence controls, never cryptographic authenticity.

This architecture tranche itself performs none of those database operations;
it freezes their future acceptance contract.

## Data, provider, cost and licence posture

- Data: repository-authored schema metadata and opaque synthetic examples only.
- Patient/product/protected/historical-PHI data: none.
- Provider/model/external retrieval: none.
- Database/source/network/browser contact: none.
- Cost: zero provider/cloud cost.
- Licence: no external content or corpus.

## Allowed side effects

Repository writes are limited to the frozen architecture documents, contract,
tests, review/acceptance evidence and later continuity artifacts. Tests may
create ordinary interpreter/cache files only.

## Forbidden surfaces

No `app/**`, `alembic/**`, `docs/diary/**` or API Spine change. No executable
DDL, migration, database/table/view/function/trigger/sequence/role/credential,
source/outbox/feed/watcher/listener connection, operational checkpoint,
product/source read, patient/product/protected data, provider/model call,
GraphQL/REST operation, command/write authority, runtime wiring, deployment,
production, release, Pages or protected-ref movement. Preserve and exclude
`docs/branding/` and every unrelated untracked artifact.

## Acceptance

1. API classification remains internal async architecture with no API or
   command-plane change.
2. The closed future schema catalogue and tenant-composite keys are exact.
3. Payload/direct-identifier/free-text/JSON/array fields are structurally
   excluded except for the exact owner-private appointment-UUID alias bridge,
   whose immutable bijective key, field, privilege, non-reuse and non-cascading
   lifecycle are closed explicitly.
4. Producer positions and immutable aliases are per-practice/source, generated
   only inside the database-revalidated in-progress update-confirm transaction
   whose sole event is bound by the existing practice-scoped command foreign
   key plus unique `command_id` constraint, and
   use one transaction/session/capability; they are row-locked, bijective and
   rollback-safe, and standalone invocation plus every ineligible coordinate
   is rejected.
5. Distinct producer, observer, admission receiver, coordinator, lifecycle,
   retention and application principals have non-overlapping ceilings.
6. Forced RLS and binding derive authority from authenticated session identity,
   not caller GUC/packet/argument claims.
7. Narrow entry points are fixed-search-path, no-dynamic-SQL, public-revoked and
   generic-table-DML-free; observer submission does not grant direct DML.
8. Authenticated source-revalidated bounded primary/conflict admission,
   coordinator stored-locator-only input, lock order and all-
   or-nothing receipt/watermark/retirement/obligation/lifecycle/audit/checkpoint
   effects are frozen.
9. Redelivery is inert and source-row-independent; a receiver-authored conflict
   sentinel remains visible before and after source purge, is storage-bounded
   and makes mismatch/reuse/demonstrated admission gap/key/retention uncertainty
   fail closed without skipping.
10. Append-only recovery anchors and generation lifecycle are independent of
    coordinator candidate state and fence coordinator consumption plus every
    next decision/rotation transition while allowing bounded receiver-owned
    admission appends.
11. Key metadata and availability are separate from secrets and scoped to one
    exact generation; unsafe rotation consumes only that generation.
12. Retention uses the complete serialized backend registry and three separate
    retention families, with execution disabled by default.
13. Expand/enable/rollback and producer-availability behavior preserve no-loss
    semantics.
14. Database-backed authored-synthetic positive and adversarial cases are exact
    and include disabled-mode zero-capability proof.
15. Static tests validate the closed machine contract against its JSON Schema;
    mechanically reconcile every exact relation column/type/key/foreign-key/
    delete action, role, entry point, RLS policy, trigger event, admission,
    lifecycle/anchor, key interval and retention family; parse the existing
    idempotency/event constraints and exact update-confirm flow; and reject
    adversarial mutations across every one of those surfaces. Explicit Git
    preflight/postflight—not the schema alone—proves that no application,
    migration, database/runtime/API, provider, data, deployment or protected
    artifact changed.
16. The claim remains architecture-only and does not claim cryptographic
    authenticity or operational safety.

## Recovery and stop

A deterministic document/schema/test defect may receive one bounded correction.
A conceptual defect in tenant binding, principal separation, rollback
atomicity, coordinator effects, recovery anchors, key lifecycle, retention
census or API classification invokes Sol's recovery lease and a fresh
independent veto before acceptance. No rejected architecture may be silently
admitted.

## Claim boundary and next dependency

Passing this tranche will prove only an exact declarative PostgreSQL migration-
and-transaction architecture. It will not create or validate a migration,
database object, role, credential, source row, producer hook, coordinator,
retention executor, crash recovery, monitoring, capacity, product read,
patient-data path, provider, command, runtime, deployment or production safety.

After acceptance, the next safe descendant will be a provider-free unmounted
authored-synthetic migration/DDL rehearsal that renders the exact schema and
privilege plan into inert SQL artifacts and statically/adversarially validates
them without applying a migration or contacting a database. Any applied local
migration, database-backed execution, operational credential or live source
remains a later separately bounded gate.
