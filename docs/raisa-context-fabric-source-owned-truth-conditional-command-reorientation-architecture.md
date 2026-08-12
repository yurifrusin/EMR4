# Context Fabric source-owned truth and conditional-command architecture

Date: 2026-08-12

Status: `architecture_only_unmounted`

## Decision

The first Context Fabric runtime will not depend on durable cue delivery for
record correctness. Authoritative services own current state and serialize
mutations. The Fabric assembles expiring evidence. Events make that evidence
refresh sooner. A command succeeds only after the owning service checks current
authority and current source truth inside the mutation transaction.

This changes the position of the durability programme, not its value. CF-D1
remains evidence about concurrent coordinator behavior. CF-D2 is no longer a
gate on the first Fabric runtime. A later **Durable Event and Cue Delivery**
extension may add restart-safe checkpoints, classification receipts and
pending-cue obligations after a new observability-first plan.

## Four planes

| Plane | Owns | Must never claim |
|---|---|---|
| Authoritative source | current domain state, invariants, mutation serialization | that an observer consumed a cue |
| Context Fabric | minimal expiring frames with provenance and freshness | current truth after expiry, confirmation, or write authority |
| Event watcher | best-effort cue, dedupe and request for a fresh authorised read | truth, authority, reservation or command success |
| Command service | current-authority check, atomic precondition, mutation, idempotency, audit and readback | authority derived from a frame or event |

Loss of an event therefore causes delayed refresh, not an unsafe mutation. A
stale interface may invite a command, but the command cannot commit on stale
evidence.

## Conditional command packet

A backend command proposal may return an opaque, short-lived precondition token
whose signed contents bind:

- schema and token versions;
- practice, actor/session, purpose and operation;
- the target appointment when one exists;
- the relevant schedule-conflict domain;
- expected source-state and conflict-domain revisions or digests;
- the canonical command digest;
- issuance, expiry, nonce and signing-key identity.

The client echoes the token; it does not interpret, widen or mint it. A Context
Frame may transport an existing opaque token but cannot create or amend one.
Freshness is not confirmation: destructive or consequential actions still need
the separately required confirmer identity or policy gate. Neither is
idempotency or audit.

## Atomic execution

The command service executes a short transaction using the canonical lock
order `practice -> schedule domain -> appointment -> idempotency record`.
Unneeded locks are skipped without reordering the locks that remain.

- **Create:** lock or atomically advance the applicable schedule-domain fence;
  recompute overlaps and authority; enforce the database conflict constraint;
  then insert.
- **Update:** lock the schedule domain and appointment; recompute current state,
  proposed placement and conflicts; then update.
- **Status:** lock the appointment; recompute current state and transition
  legality; then update.
- **Delete/cancel:** lock the appointment; recompute current state and
  cancellation authority; then mutate using the domain's retained-history
  policy.

The exact production fence mechanism remains an implementation decision. It
may be a monotonically versioned schedule bucket, advisory-key protocol plus
constraint, exclusion constraint, or another reviewed database-owned primitive.
The invariant is fixed: all contenders for the same conflict domain participate
in one deterministic serialization and final constraint check. A signed token
without that database-side serialization is insufficient.

## Ribbons and loser outcomes

Only a transaction winner receives `committed` with a durable command receipt,
audit reference and readback. The same idempotency identity with the same
command digest receives `idempotent_replay` and the original receipt, never a
second effect.

Every other contestant receives a typed non-success result with no mutation:

- `stale_precondition` — source state changed; fresh read and reproposal needed;
- `schedule_conflict` — another valid booking won the conflict domain;
- `authority_revoked` — current principal authority no longer permits it;
- `confirmation_required` — freshness is valid but confirmation evidence is
  absent or invalid;
- `validation_rejected` — the command violates a current domain invariant; or
- `idempotency_conflict` — the key was reused with a different command digest.

No result is silently promoted to success, and no event receipt substitutes for
the command receipt.

## Legacy compatibility migration

The raw create/update/status/delete routes are human-client compatibility
surfaces, not trusted bypasses. They remain unchanged for now. Their migration
has two steps:

1. internally converge each route on the same conditional-command kernel and
   typed loser outcomes, without introducing a second mutation implementation;
2. move ordinary Diary clients to proposal/confirm routes and retire raw routes
   only after parity, attribution, idempotency and user-flow evidence.

An implicit backend freshness check is desirable on all four routes. It is not
an implicit human confirmation. Where product policy requires confirmation,
the raw route must either carry valid separate confirmation evidence or fail
with `confirmation_required`.

## Deferred Durable Event and Cue Delivery

The later extension may add a source-owned monotonic position committed with
the domain change, per-practice/family durable checkpoints, immutable
classification receipts, pending cue obligations, at-least-once delivery and
idempotent consumption. It improves restart recovery, observability and cue
latency. It still cannot confer write authority or turn events into current
truth.

The topology is one logical consumer for each database event partition, not one
watcher per human user. The first runtime may use one physical watcher for the
database and accept delayed cues while it is unavailable. A later highly
available deployment may use active/standby replicas, but an external lease and
fencing generation must give only one replica checkpoint-write ownership for a
partition. Brief duplicate observation during takeover is handled as
at-least-once, idempotent cue delivery; two equal checkpoint writers are never
the intended steady state.

CF-D1 is retained as concurrency evidence. The stopped CF-D2 attempts remain
immutable negative evidence. Any return must begin with distinct
observations for viable failure causes and a fresh observability-first plan;
it is not a retry under the old authority.

## Claims deliberately not made

This architecture does not prove a production token format, database fence,
route behavior, migration, watcher, restart recovery, unknown-commit recovery,
patient-data safety, deployment or operational availability.
