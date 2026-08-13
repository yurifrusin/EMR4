# CF-D2 event and cue disposable PostgreSQL behavior/transaction design

Date: 2026-08-13

Timestamp: 2026-08-13T20:21:19+10:00 (Australia/Brisbane)

Status: `frozen_six_group_serial_behavior_only`

## Decision

Use one small standard-library host harness to install the exact accepted
inert artifact in one owned PostgreSQL 16 container, execute six fixed serial
scenario groups and destroy the container. Protocol logic is expressed only
as fixed transaction-local SQL/anonymous blocks; it creates no stored
function, trigger, migration, application adapter or reusable runtime surface.

## Protocol transaction shape

`admit_terminal` locks the exact partition and checkpoint row before resolving
the unique position. It returns an exact duplicate unchanged, refuses a
divergent duplicate, and for a new required cue either locks/extends one
eligible adjacent pending obligation or creates a new one. Receipt and
obligation change share the same transaction. Checkpoint advancement examines
only the next contiguous position and verifies required-obligation coverage.

`record_dispatch_attempt` locks the partition generation and obligation,
derives exactly `max(attempt_ordinal)+1`, inserts one immutable attempt and
changes pending to delivered only for a delivered outcome in the same
transaction. Failure retains pending. Delivered state never regresses.

`record_reconciliation` locks the obligation and exact delivered attempt,
applies the accepted six-row truth table, inserts at most one immutable receipt
per obligation, reuses an exact duplicate and rejects a conflict.

All refused protocol paths raise a fixed transaction-local result and leave
the state digest unchanged. Deliberate post-write failures demonstrate actual
PostgreSQL rollback rather than relying on a simulated state machine.

## State observations

After every material step, one fixed read-only projection emits ordered JSON
for all seven relations. The host canonicalizes and hashes that projection.
Evidence retains the digest, row counts and fixed assertions rather than raw
rows. Fixed authored-synthetic IDs and SHA-256 values are structurally valid
but carry no practice, appointment or person meaning.

## Lock observations

Rollback-only probe transactions acquire the same `FOR UPDATE` relation paths
and project the target-schema relation name plus granted lock mode from
`pg_locks`. The contract admits the exact required subset and ignores only
PostgreSQL system/index locks. It makes no concurrency claim because no second
session competes for a lock.

## Containment

The harness reuses only the already accepted parse/catalogue container helpers
for exact cached-image admission, readiness, argument-vector `docker exec`,
profile verification and exact-ID cleanup. Behavior contract and SQL remain
owned by the new harness. The bootstrap password is a fixed disposable value
inside the networkless container and is never evidence or a product
credential.

## Non-claims

The design does not prove multi-session exclusion, deadlock recovery,
serializability under contention, restart/crash/unknown-commit recovery,
source observation, transport delivery, retention, rotation, purge,
performance, real authorisation or fresh read, application wiring, migration
safety, deployment or production operation.
