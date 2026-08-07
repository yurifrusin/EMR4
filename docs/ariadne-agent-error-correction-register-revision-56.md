# Ariadne agent-error register revision 56

Date: 2026-08-06

Status: seventh migration/transaction architecture recovery active

## Sixth-recovery veto is preserved

The fresh exact-head review of candidate
`a0ffc10a97cec23399724e56e6479932f029ab00` was procedurally eligible, read-only
and clean. It confirmed the exact PostgreSQL-16 low-XID32 comparison, the
single-session update-confirm source flow and the unchanged API Spine. It
correctly returned `revision_required` for six remaining defects:

1. the appointment trigger observed only temporal-column updates and could not
   enforce projection absence for a non-temporal update;
2. types, defaults, exact RLS predicates, composite/function outputs, trigger
   signatures and cross-relation enforcement were not renderer-closed;
3. the admission security-definer owner lacked the privilege needed to insert;
4. hostile mutations failed first on the unchanged canonical hash rather than
   proving semantic rejection;
5. the plan overclaimed database detection of savepoints with no relevant
   tuple; and
6. an outbox foreign key silently prolonged the product-bearing committed
   event without a matching retention contract.

The complete veto is preserved at
`orchestration/agent_inbox/codex/raisa-context-fabric-durability-migration-transaction-architecture-recovery-6-independent-veto.md`.
It grants no acceptance.

## Seventh recovery controls

The recovered candidate now:

- uses a deferred row-level all-`UPDATE` appointment trigger that computes the
  exact `OLD`/`NEW` temporal predicate and enforces either the complete event/
  projection set or its complete absence;
- states that savepoints are forbidden by the application transaction
  contract, every relevant subtransaction-authored tuple is rejected, and a
  no-write savepoint is not database-observable;
- retains transaction-local event/outbox co-authorship checks but removes the
  persistent outbox foreign key to `diary_committed_events`, so product-event
  expiry does not pin or invalidate source evidence;
- gives the distinct non-login admission owner only the required internal
  reads and admission `INSERT`, while the observer keeps zero direct DML;
- closes all builtin/domain/enum/composite definitions, structured columns and
  explicit no-defaults, named keys/indexes/FKs/checks, 44 exact RLS policies,
  nine entry-point input/output signatures, 13 trigger-function signatures and
  triggers, and 25 cross-invariant enforcement records; and
- validates the whole-contract constant while separately resealing hostile
  candidates and rejecting them through renderer semantics with the canonical-
  digest field relaxed.

AER-0051 remains open until this seventh candidate passes a genuinely fresh
exact-head veto. This recovery remains architecture-only and opens no SQL,
migration, database, runtime, provider, product-data, deployment, Pages or
protected-ref authority.

Revision 56 still contains 54 bounded incidents: 42 agent-behaviour
observations, three harness failures, two repository defects and seven
transport timeouts. AER-0053 and AER-0054 remain contained. Counts are
workflow-improvement signals, not model, provider, transport or role causation.
