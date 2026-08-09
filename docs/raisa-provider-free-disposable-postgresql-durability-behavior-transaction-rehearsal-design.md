# Disposable PostgreSQL durability behavior/transaction rehearsal design

Date: 2026-08-08

Status: candidate planning design; runtime closed

## Purpose

This design translates the accepted Context Fabric durability catalogue into
one small, evidence-bearing PostgreSQL experiment. It deliberately proves a
serial slice before opening concurrency, rotation, retention or application
wiring.

The slice is large enough to exercise the important trust transitions:

```text
lifecycle binding
  -> registered generation + head/checkpoint/anchor/key baseline
  -> producer update-confirm transaction + payload-free outbox
  -> observer proofread admission
  -> coordinator receipt + invalidation/retirement/obligation/checkpoint
  -> application-read projection under RLS
```

Each arrow is entered under a distinct accepted database login. No arrow
inherits the preceding role's authority.

## API and authority boundary

There is no API request in this design. The later harness connects only to its
owned container-local PostgreSQL socket. Its product-shaped tuples are opaque
fixtures reproducing the accepted update-confirm transaction membership; they
are not calls to the REST command and do not establish product write authority.

The producer may write the four fixture application relations only through
exact local grants that stand in for the already existing application
transaction. It receives no direct Fabric DML. Fabric effects arise only from
the accepted security-definer entry point and triggers.

## Installation and fixture phases

The later harness has one irreversible order inside the disposable container:

1. prove exact local image, containment, ownership and stable PostgreSQL 16
   readiness;
2. create one behavior database and the four exact prerequisite shapes;
3. apply the byte-identical accepted artifact atomically;
4. reconcile the same exact catalogue and privilege digests already proved by
   the parent run;
5. install only the closed fixture keys, producer application-table grants,
   binding rows and opaque appointment seeds;
6. record a zero-behavior baseline;
7. run `BTR-E01` through `BTR-B03` in contract order;
8. reconcile final allowlisted counts/digests and parent catalogue identity;
9. remove the exact owned container and prove absence.

No behavior scenario may begin if installation/catalogue reconciliation or
fixture closure differs. No fixture DDL may change a Fabric object.

## Session and transaction discipline

Every scenario uses a fresh `psql` process and connection. The container
initialization superuser sets the session authorization exactly once before
the transaction begins. Evidence records both `session_user` and
`current_user`; the scenario must observe the expected accepted login and the
security-definer owner only while inside the accepted function.

Producer, observer, trigger and RLS scenarios use `READ COMMITTED`. The three
registration transactions and the coordinator apply/replay/rollback scenarios
use `SERIALIZABLE`, exactly as required by the accepted entry-point guards.
Every transaction remains top-level, with no savepoint, role switch or retry.
Read-only RLS evidence sets the transaction read-only. Standard retryable
`40001` or `40P01` is not absorbed or reclassified; either would fail this
single-session serial tranche and require diagnosis.

Expected custom failures and the fixed injected `P0001` abort terminate the
connection with the transaction uncommitted. Readback occurs through a new
fixed privileged evidence connection.

## Positive thread partitions

Three observer generations share the exact alpha practice/source/stream but
have distinct observer IDs:

- `happy` owns position-one admission and coordinator replay evidence;
- `conflict` owns position-two primary/conflict boundedness evidence; and
- `rollback` owns admission/coordinator outer-rollback evidence.

The one producer binding prevents ambiguous stream selection. Position one and
position two are created in separate complete update-confirm transactions over
distinct fixed command/audit/event IDs. The stream head must advance exactly
`0 -> 1 -> 2`; all negative producer cases leave it at two.

Generation registration is repeated under the lifecycle role, but stream-head
create-or-reload semantics must converge on the same exact position-zero head.
Each generation gets a separate checkpoint, baseline anchor, key interval and
frame set.

## Producer transaction proof

The positive temporal transaction has this exact order:

```text
insert current IN_PROGRESS claim
  -> update pre-existing appointment start/duration once
  -> insert one matching audit
  -> insert one exact allowlisted reschedule event
  -> call project_update_confirm_reschedule_v1(command_id)
  -> update the same claim to completed
  -> deferred trigger fences at commit
```

The returned outbox row is compared with the committed event, immutable alias
and stream head. The harness does not choose an alias or position. A failure at
any point rolls back the entire application/Fabric membership.

The non-temporal case changes only the location of a distinct appointment. It
does not create a claim, audit or event and does not call the projection entry
point. The appointment triggers must distinguish it using only the accepted
`OLD`/`NEW` temporal fields and commit without a Fabric effect.

## Observer admission proof

Admission receives an exact typed generation locator, source position and
proofread packet. The packet's source-membership digest is canonically derived
only from every field of the same-locator outbox row, using the accepted
`emr4_context_fabric.source_membership_digest_v1` profile after the observer's
RLS-filtered read. It is not the outbox row's `source_contract_digest`, which
is only one input to that full-row membership digest. Every other packet value
is fixed in the contract.

The first call returns PRIMARY. Exact replay must return the retained PRIMARY
without requiring a new source effect. A different packet at the same conflict
generation/position may append one receiver-authored CONFLICT. Repeating that
same mismatch must return the same conflict. The primary/conflict set is
bounded to exactly two rows.

A valid generation with a missing position fails `CF201`; a beta locator under
the alpha observer binding fails before source access with `CF004`.

## Coordinator proof

The coordinator receives only an admission locator, never a caller-supplied
decision. On first happy application it must atomically derive the receipt,
checkpoint, watermarks, matching frame retirement, one coalesced obligation,
decision lifecycle and minimal audit. Readback binds every count, position,
enum and digest relationship.

Exact replay of the same locator must return the stored replay result without
a second effect. The scenario's readback deliberately checks counts and
digests for every coordinator-owned relation, not merely its returned value.

The rollback generation first receives a committed PRIMARY. Its coordinator
call then returns inside a transaction that raises fixed `P0001`. After the
connection aborts, the PRIMARY remains because it predates the transaction,
while every coordinator effect remains absent.

## Trigger proof

The selected trigger set is chosen for transaction-integrity leverage:

- missing event/projection tests the deferred bidirectional temporal set;
- insert-then-delete tests that the immediate immutable guard prevents a
  same-transaction event from erasing the queued obligation;
- committed-event update tests reachable immediate immutable-member rejection;
  the producer retains no direct Fabric alias update grant; and
- a second appointment update tests current-XID provenance and ambiguity
  rejection.

The plan claims only these paths. Other immediate/deferred trigger operation
branches remain architecture/parse evidence until a later finite descendant.

## RLS and privilege proof

RLS evidence never relies only on `has_*_privilege`. It combines catalogue
privilege readback with actual statements under each tested session identity.

The application-read role has an exact alpha binding and direct `SELECT` only
on frame generation, invalidation watermark and reassembly obligation. The
harness seeds one beta projection row through bootstrap solely to prove it is
invisible; it contains only opaque synthetic coordinates.

The forbidden-operation matrix uses fresh connections for every cell and
includes direct Fabric DML, trigger-function execution, a foreign entry point,
`SET ROLE`, membership and bypass flags. Expected permission errors are exact
SQLSTATE `42501`; boolean catalogue ceilings must remain false.

## Evidence model

The evidence artifact will contain one closed record per scenario in the exact
contract order. A record has fixed scenario ID, expected/observed result,
principal, transaction mode, SQLSTATE/reason, allowlisted before/after counts,
canonical row digests and pass/fail. It contains no raw SQL, log, payload,
credential or unrestricted database value.

The terminal evidence also binds:

- parent artifact and manifest digests;
- image reference and immutable image ID;
- exact captured container ID and containment facts;
- catalogue/privilege identity before and after behavior;
- twenty-of-twenty scenario reconciliation; and
- exact-ID cleanup absence.

Any missing scenario, duplicate result, unexpected SQLSTATE, changed count,
unclassified failure or cleanup uncertainty makes the whole rehearsal fail.

## Deliberate omissions

This design does not test concurrent producers/coordinators, deadlocks,
serializable retention, key rotation, purge, generation consumption,
independent anchor append, source-row purge replay, crash restart, unknown
commit, migration locks, performance or operational monitoring. It does not
mount a watcher/listener or build a ContextFrameSet.

Those are later finite descendants after this serial transaction spine is
server-proven.
