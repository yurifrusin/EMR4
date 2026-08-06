# Durability migration/transaction architecture fourth-recovery veto

Date: 2026-08-06

Candidate: `77ba83d5f1695ac58eddd0e96f6ec8003247e339`

Decision: `revision_required`

## Rehydration and postflight

The genuinely fresh reviewer restored all five named rehydration sources, read
the API Steward and exact allowlisted architecture, parent, API Spine and
existing command/event model files, and remained on clean branch
`codex/review-durability-migration-transaction-plan-recovery-4-77ba83d5` at
exact HEAD `77ba83d5f1695ac58eddd0e96f6ec8003247e339` before and after.
Local/origin `master` and `handoff/current` remained
`2e34bdad732fdab32fbf778280b3d3c70d66d602`.

The authorised absolute system-Python `--noconftest`, no-cache, no-bytecode
focused test passed 6/6. No file, ref, provider/model, network, database,
source or runtime state changed.

## Blocking findings

1. **P1 — row-state equality did not prove transaction provenance.**
   `session_user`, the `IN_PROGRESS` claim and matching appointment/audit/event
   state identify an authenticated logical producer and coherent rows, but not
   the transaction that created the signed command attempt. The existing
   nullable target/audit fields permit an in-progress binding, and the
   practice-scoped command foreign key plus unique command id make the event
   sole without proving it was authored in the current transaction. A later
   transaction under the same login could therefore satisfy the documented
   checks if an eligible committed in-progress state existed. The architecture
   requires database-enforced transaction-local provenance plus a deferred
   fail-commit invariant; a missing-claim negative case is insufficient.

2. **P2 — the six tests asserted prose presence only.** The suite did not parse
   the current model constraints, validate a closed machine contract, reject
   extra/missing relations or keys, adversarially mutate transaction/alias
   invariants, or mechanically bound the architecture artifact surface. It
   could not detect the P1 or several catalogue/lifecycle/API contradictions
   despite the plan's static-proof claim.

## Reconciled properties

The existing update-confirm path does use one SQLAlchemy session through claim,
appointment lock/update, audit/event append, completion and commit; existing
target/audit fields can legally be populated while `in_progress`; current
event command/audit uniqueness is practice-bound; and the alias,
PRIMARY/CONFLICT, anchor, key, retention, RLS and API Spine boundaries remain
coherent as declarative architecture only.

AER-0051 remains open. No inert DDL rehearsal is admitted.

`DECISION: revision_required`
