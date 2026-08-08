# Inert DDL composite dependency-ordering recovery

Date: 2026-08-08

Status: bounded renderer recovery under the accepted disposable PostgreSQL
syntax/dependency repair rule; no further database action before fresh veto

## Failure

Disposable attempt `a6a947c722bde18774fafca7` passed exact container
containment, PostgreSQL readiness, rollback-database creation and installation
of the four empty authored-synthetic prerequisite tables. The canonical inert
artifact then failed before the fixed invalid suffix and its owned container
was removed with exact-ID absence verified.

The byte order is deterministically invalid: composite
`generation_registration_v1` declares `initial_key_interval` as
`future_key_interval_v1`, but the referenced composite is emitted later. This
is an artifact-lowering dependency defect, not evidence against the accepted
domain shape.

## Exact repair

The compiler derives intra-catalogue composite dependencies from the exact
field types and emits a stable topological order. At every step it chooses the
first remaining source-ordered composite whose composite dependencies have
already been emitted. Thus already-legal source order is retained, the one
forward reference moves behind its prerequisite, and duplicate names or a
dependency cycle fail before artifact write.

The independent recognizer derives the same expected order and rejects
reordered emitted bytes. Hostile tests bind the exact future-key-before-
registration relation, cycle rejection and recognition of a reversed
regression.

## Frozen boundary

Only ordering of the nine existing composite `CREATE TYPE` statements may
change. The four domains, nineteen enums, nine composite definitions and their
fields, thirty-two type owners, every other object/statement population,
function/trigger body, policy, grant, source contract and application relation
remain byte-semantically unchanged. The previous artifact and failed runtime
evidence remain preserved; the fixed compiler regenerates a new canonical
artifact and manifest, and the disposable descendant later binds that exact
source HEAD/hash/count.

This grants no function/trigger/RLS behavior, application migration, runtime
wiring, source observation, operational persistence or credential, patient or
product data, provider product call, command/write authority, deployment,
production, release, Pages rebuild or protected-ref movement.
