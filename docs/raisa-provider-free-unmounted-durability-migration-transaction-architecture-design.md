# Provider-free unmounted durability migration-and-transaction architecture design

Date: 2026-08-06

Status: eighth recovered design candidate pending independent veto

## Purpose

Translate the accepted pure durability state machine into one exact future
PostgreSQL shape without creating or contacting PostgreSQL. The design makes
transactional position, tenant binding, coordinator atomicity, recovery and
retention mechanically expressible before inert DDL or a migration is allowed.

## Trust planes

```mermaid
flowchart LR
    P["Existing signed update-confirm producer"] -->|"same transaction"| O["Payload-free control outbox"]
    O -->|"exact scoped read"| B["Observation membrane + proofreader"]
    B -->|"authenticated exact submit"| X["Immutable proofread admission"]
    X -->|"locator only"| C["Durability coordinator entry point"]
    C --> D["Receipt + watermark + retirement + obligation + lifecycle + audit + checkpoint"]
    D -->|"independent verify"| A["Append-only lifecycle anchor"]
    A -->|"fences next transition"| C
    R["Serialized retention authority"] --> O
    D -. "invalidation only" .-> F["Later fresh application read"]
```

The producer, observer, admission receiver, coordinator, lifecycle/anchor,
retention and later application-read principals are not aliases. None inherits
authority from an event, checkpoint, frame or another plane.

## Source transaction

The source head is an ordinary row keyed by practice and the exact reschedule
stream. The command first holds the exact `IN_PROGRESS`
`confirmAppointmentUpdateProposal` / `update-confirm` idempotency row with its
immutable signed-request digest, locks and updates the appointment, appends its
audit/event and populates the row's existing target-appointment and audit
bindings. The event's existing practice-scoped `(practice_id, command_id)`
foreign key plus unique `command_id` constraint binds the sole event to that
claim; no fictitious event-id or revision field is added to the idempotency
row. One owner-mediated producer projection entry
point then rederives the producer login/binding, locks the in-progress row,
loads the sole event by command id and verifies event type/schema, appointment,
audit and aggregate revision against the claim and locked product state before
it may lock the immutable alias row and stream head. Its `n -> n + 1` update and
outbox append occur in the same existing command transaction as appointment
truth, appointment audit, committed event and idempotency completion.

The signed command and projection use one physical connection, one logical
capability and one `session_user` throughout that transaction. There is no
second login, `SET ROLE`, alias-only capability or transaction hand-off whose
identity or commit outcome could be substituted between the command and
projection.

The entry point additionally requires the idempotency claim, current
appointment tuple version, audit and event to have database-derived `xmin`
equal to the PostgreSQL-16 top-level XID32 expression
`((((pg_current_xact_id()::text)::bigint & 4294967295)::text)::xid)`, while the
claim's immutable server-default `created_at` matches
`transaction_timestamp()`. Savepoints and subtransactions are forbidden by the
application transaction contract from claim insertion through outer commit;
a subtransaction-authored relevant tuple fails. A no-write savepoint is not
database-observable and no such detection is claimed; the exact application
route is instead statically proven to contain no nested/savepoint call.
This use is ephemeral provenance only: no XID is caller-supplied, stored,
retained, exposed or treated as a durability coordinate. The zero legacy
in-progress census, no-reversion guard and no-`IN_PROGRESS`-at-commit constraint
remove old-row and wrap/freeze ambiguity.

The database-derived event obligation is the existing `OLD`/`NEW`
`start_time` or `duration_minutes` transition. A deferred row-level all-
`UPDATE` appointment trigger therefore executes for every appointment update,
requires event/outbox/head only for that transition and requires their absence
for a non-temporal update. Immediate immutable-member guards plus
deferred claim, appointment, audit, event, alias, head and outbox triggers cover
INSERT, UPDATE and DELETE, so insert-delete cannot erase an obligation. They
also fail commit unless no exact claim remains or returns to `IN_PROGRESS`,
each event has its completed matching target/audit and projection, every outbox
has that event/result, and a first alias is referenced by that outbox. The
machine contract enumerates the exact trigger operations. Trigger functions
are fixed-search-path owner code with no runtime execute. Default-off
enablement first requires zero legacy committed exact-operation in-progress
rows.

This deliberately makes durability availability part of the enabled command's
atomic contract. A failed append or head lock fails the command; it cannot be
repaired after commit. Sequence, identity, timestamps, UUID ordering,
aggregate revision, transaction ids and WAL positions are rejected because
their rollback/ordering semantics cannot prove gap-free publication.

The outbox contains the accepted non-semantic raw event UUID and opaque alias,
but no product payload. The observer alone may read it. The raw event UUID is
transaction-locally checked against the just-authored committed event before
commit, then domain-separated into the accepted observation digest and
discarded before the durability packet, receipt or audit. There is deliberately
no persistent outbox foreign key to `diary_committed_events`: product-event
expiry or later separately authorised physical deletion neither removes nor
invalidates the independent outbox and supplies no source-retention authority.

## Owner-private alias bridge

`diary_context_aggregate_aliases_v1` is the sole product-identifier exception
inside the future schema. It stores exactly the practice/source-bound product
appointment UUID needed to return one stable opaque alias across producer
transactions. Its forward key includes practice, exact source contract and
appointment UUID; its reverse unique key includes practice, source contract and
opaque alias. Both values are immutable, the caller cannot choose the alias,
same-appointment races return the existing mapping and cross-appointment alias
collisions roll back the command.

This is an owner-private producer subroutine, not a separately executable
function or control-projection surface. The producer may execute only the one
projection entry point above, after its database-enforced command-context
revalidation, and has no direct bridge/head/outbox table privilege. Observer,
admission receiver, coordinator, lifecycle, retention and application-read
principals have no `SELECT`, DML or function path to the product UUID. Only the
opaque alias enters the outbox.

The bridge does not join the source, receipt/checkpoint or audit retention
families and supplies no purge authority. Update and deletion are prohibited
for this v1 source-contract epoch, preventing delete/recreate identity changes
and alias reuse. Any future erasure/non-reuse design requires a new reviewed
contract and source epoch. The bridge never cascades to or rewrites retained
outbox, admission, receipt, checkpoint, anchor or audit evidence. No actual
product identifier is present or processed in this architecture-only tranche.

## Tenant binding

Forced RLS is defense in depth, not the authority source. A custom practice GUC
is forgeable by a login that can execute arbitrary SQL. Every narrow entry
point therefore resolves the actual `session_user` through an owner-controlled
binding relation to exactly one active logical principal, practice, source
family and credential epoch. Duplicate or ambiguous active bindings fail
closed. Caller practice is only a locator to compare with that binding, and a
connection pool may not multiplex practices, capabilities or credential epochs
through one bound login.

Runtime roles own nothing, inherit nothing, cannot bypass RLS or set another
role and have no direct durability-table DML. Security-definer code, if later
selected, has a non-login owner, fixed empty/schema-qualified search path, no
dynamic SQL and no `PUBLIC` execute. Every tenant key includes `practice_id`.

The admission function is owned by a distinct non-login receiver owner. Its
closed internal privilege list is exact: the required source/generation/
checkpoint/receipt/key/binding `SELECT` set and `INSERT` on admission only. It
has no update, delete, coordinator, lifecycle, retention, product or command
privilege. This makes the `SECURITY DEFINER` insert coherent without granting
the observer direct DML.

## Authenticated proofread admission

The observer does not send a free-standing decision packet to the coordinator.
It may execute one receiver-owned admission function. That function rederives
the actual observer `session_user` and first locks and loads the complete
retained admission set and receipt for the exact locator. At most one immutable
`PRIMARY` plus one immutable `CONFLICT` sentinel may exist per position. An
exact duplicate returns the primary without source access. A different
authenticated attempted digest appends or returns the sole closed conflict
sentinel, including after source purge, and cannot overwrite the primary.

Only a first primary requires the receiver to reselect the exact payload-free
source row, validate coordinate/predecessor/aggregate revision and the
generation-local key interval, and bind the authenticated observer/binding,
source-membership digest and proofread packet into the primary digest.
Observation-digest reuse at another position similarly persists one conflict-
only sentinel after authenticated source validation. A sentinel contains only
the binding/source coordinate, attempted admission digest and closed reason;
raw UUID, alias and copied packet values cross neither the receiver boundary nor
the stored admission set.

The observer has no direct DML or durability-state privilege; the admission
receiver has no checkpoint/effect authority. The coordinator can identify an
admission set but cannot invent or replace one. Exact duplicate submission is
inert; the first mismatch or digest reuse becomes durable receiver-authored
corruption evidence and all later conflicts are storage-bounded by the same
sentinel. Primary and conflict rows are retained together with receipt/
checkpoint evidence. Operational database transport/channel and credential
proof remain later gates. Concurrent first-attempt uniqueness races reload the
winner: exact equality is inert, while inequality appends or returns the sole
conflict sentinel rather than disappearing behind `ON CONFLICT DO NOTHING`.

## Coordinator transaction

At `SERIALIZABLE`, the coordinator rederives binding, locks the generation
registry barrier and exact checkpoint, and verifies that the newest independent
anchor equals that checkpoint. It then loads the complete stored admission set
and retained receipt by locator before any new-position work. Any conflict
sentinel forces the atomic rebase path before redelivery can succeed. Otherwise
exact primary/receipt redelivery uses those retained rows and remains valid
after independent source purge. For a new transition it reloads the immutable
authenticated primary and generation-local key proof; it accepts no copied
decision values and never reads raw source UUID/alias.

Receipt, monotonic watermarks, one-way frame retirement, one coalesced
obligation, the `DECISION` lifecycle row, audit and checkpoint disposition
commit together.

The lifecycle journal orders both decision and key-rotation entries. Decision
audit is a one-to-one detail, so lifecycle revisions cannot be reassigned from
rotation to audit. Obligation buckets are derived from canonical admitted
history; no mutable exact cause counter or caller bucket becomes authority.

Exact redelivery is inert only when the retained set contains a matching primary
and no conflict. Any receiver-authored conflict sentinel, identity mismatch,
digest reuse, demonstrated admission gap, wrong predecessor/epoch, missing
required primary or unverifiable key holds the last contiguous checkpoint,
fully invalidates and atomically requires rebase. An event not yet admitted is
ordinary waiting.

## Restart and anchors

Lifecycle authority appends a distinct immutable recovery anchor for the
baseline and every committed decision/rotation checkpoint. A candidate
checkpoint is never its own authority, and coordinator consumption plus the
next decision or rotation lifecycle transition is blocked until the latest
anchor exactly matches it. Receiver-owned bounded primary/conflict admission
appends may continue while that anchor is pending. After a crash in the commit-
to-anchor window, lifecycle authority may complete the pending anchor only by
independently re-verifying the entire committed state; otherwise a new
generation is required. Resume requires exact agreement among the anchor,
verified durability state and next retained admission/source continuity.
Neither path reconstructs current truth or restores a retired frame.

## Generation-local key rotation

Each interval partition belongs to one exact observer generation. One
`SERIALIZABLE` routine rotation locks that generation's barrier, checkpoint,
current anchor and schedule; preserves history and predecessor overlap; appends
one `KEY_ROTATION` lifecycle row; and advances the schedule digest/checkpoint
lifecycle revision. It changes no other generation. A matching independent
anchor must exist before the next decision.

## Retention barrier

Generation registration/rebaseline and source purge share the same
practice/source registry barrier. A future retention transaction locks it at
`SERIALIZABLE`, derives every non-consumed generation inside the database and
uses the slowest checkpoint, independent pins, key overlap and safety grace.
The caller supplies none of that authority.

Source, receipt/checkpoint and audit retention are independent; no cascade
links them. The existing product-bearing event relation is in none of those
families and is not pinned by an outbox foreign key. Admissions and anchors
remain in the receipt/checkpoint family for as long as their receipt/restart/
redelivery meaning is retained. Execution is disabled by default. Production
duration, capacity and key-store selection remain later operational choices.
Capacity pressure never legitimizes silent loss.

## Expand and rollback

The later migration sequence is expand-first: closed schema/RLS/roles with no
runtime bindings; narrow entry points; database-backed synthetic acceptance;
separate credential binding; exact baseline; producer enablement; then
observer/coordinator enablement. Before any row, unused objects may later be
removed. After publication begins, rollback is forward-fix and data-preserving;
the appointment command must not continue without its required control row.

## Integrity claim

Relational constraints, append-only privileges and digest chains provide
integrity and tamper-evidence controls. They are not a cryptographic MAC and do
not make a database owner or compromised credential trustworthy. Operational
key storage, credentials, monitoring and incident response remain later gates.

## Machine-closed structural catalogue

The version-3 JSON contract is normative where this prose summarizes. It
enumerates exact builtin/domain/enum/composite definitions; every structured
column, nullability and explicit no-default; named primary, unique, partial-
unique, foreign and row-check constraints for all 18 relations; all 44 forced-
RLS command policies with executable `USING`/`WITH CHECK` predicates; complete
role/function ownership and the admission owner's closed internal grants; nine
entry-point input/output signatures; the binding helper signature and SQL body;
13 trigger-function signatures; 13 named immediate/deferred triggers; and 25
cross-relation invariants mapped to concrete constraints, function signatures
or sole-path entry points. The JSON Schema is a whole-contract constant.

Semantic acceptance separately relaxes the canonical-digest field, reseals
hostile variants and rejects them through catalogue/reference/ownership/
retention semantics, including exact rejection of any admission-owner
privilege widening.

The contract intentionally supplies no executable SQL body for any of the nine
entry points or thirteen trigger functions. A structural renderer must omit
them, their triggers and their `EXECUTE` grants; it may not translate invariant
prose into PL/pgSQL. Only the closed binding helper body is present, and it may
be rendered only before runtime bindings exist. A separate function-and-
trigger-body architecture is the next safe gate and must pass before inert DDL
may include those executable surfaces.

## Non-authority statement

This design creates no SQL, migration, database object, role, credential,
source read, persistence, product or patient data, API, command, provider,
runtime, deployment, production, release, Pages or protected-ref authority.
