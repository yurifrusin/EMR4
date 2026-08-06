# Durability migration/transaction architecture third-recovery veto

Date: 2026-08-06

Candidate: `62c78cba72c99b00a0087738b771d05f0adf2c06`

Decision: `revision_required`

## Rehydration and postflight

The genuinely fresh reviewer restored all five named rehydration sources, read
the API Steward and exact allowlisted architecture, parent and API Spine files,
and remained on clean branch
`codex/review-durability-migration-transaction-plan-recovery-3-62c78cba` at
exact HEAD `62c78cba72c99b00a0087738b771d05f0adf2c06` before and after.
Local/origin `master` and `handoff/current` remained
`2e34bdad732fdab32fbf778280b3d3c70d66d602`.

The authorised system-Python `--noconftest`, no-cache, no-bytecode focused test
passed 6/6. No file, ref, provider/model, network, database, source or runtime
state changed.

## Blocking findings

1. **P1 — the alias helper remained an independently invocable mutation path.**
   The producer received execute access to an owner-mediated create-or-return
   function, but the function did not independently require the exact signed
   update-confirm command, in-progress idempotency claim and matching
   appointment/event context. The producer login could therefore call it
   outside the intended command transaction and persist an arbitrary existing
   or invented UUID mapping. Future acceptance also omitted standalone-call
   rejection and alias-row rollback.

2. **P1 — the bridge did not freeze a bijective immutable identity contract.**
   The forward `(practice_id, product_appointment_uuid)` key did not include an
   exact reverse tenant/source alias uniqueness constraint. Later deletion also
   permitted delete/recreate with a different alias because no tombstone or
   non-reuse rule existed. Generic tenant-key and no-cascade language did not
   establish stable identity.

The repair must make alias creation private to one database-enforced producer
projection transaction or independently validate the exact command/
idempotency/appointment context; prove standalone rejection and rollback; add
tenant/source-scoped reverse alias uniqueness and immutable create-or-return
semantics; prove collision/race behavior; and make the mapping permanent for
this contract or add an enforceable non-reuse tombstone.

## Reconciled properties that passed

All 18 relations were present; the appointment UUID was otherwise confined to
the bridge; non-producer principals had no table/function path; tenant keys,
`session_user`, forced RLS and security-definer restrictions were explicit;
producer position and coordinator effects were atomic; primary/conflict and
pending-anchor repairs were coherent; key rotation was generation-local;
retention remained independent/default-off; and API Spine and claim boundaries
remained architecture-only.

AER-0051 remains open. No inert DDL rehearsal is admitted.

`DECISION: revision_required`
