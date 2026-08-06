# Durability migration/transaction architecture plan recovery veto

Date: 2026-08-06

Candidate: `5de1ba511910335ea2ee73f12877ee886639c836`

Decision: `revision_required`

## Rehydration and postflight

The genuinely fresh reviewer restored
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`, applied the API Steward read-only and remained on clean
branch `codex/review-durability-migration-transaction-plan-recovery-5de1ba51`
at exact HEAD `5de1ba511910335ea2ee73f12877ee886639c836` before and after. Local/origin
`master` and `handoff/current` remained
`2e34bdad732fdab32fbf778280b3d3c70d66d602`.

The authorized system-Python `--noconftest`, no-cache, no-bytecode focused test
passed 5/5. No `uv`, `pip`, bootstrap, file creation, provider/model/network,
database/source/runtime contact or ref movement occurred.

## Blocking findings

1. **P1 — conflicting admission attempts were not durably representable.** The
   plan defined one immutable admission keyed by generation plus position and
   correctly forbade overwrite. A same-position conflicting packet or digest
   reuse could therefore neither replace the primary row nor append durable
   receiver-owned evidence. The separate coordinator, which accepts only a
   stored locator, would continue seeing only the original valid admission.
   After source purge the receiver's source-first wording also prevented an
   altered resubmission from being compared with retained admission/receipt
   evidence. The repair must persist a bounded typed conflict sentinel or an
   equivalent append-only attempt model under the authenticated receiver, never
   reintroduce a caller decision packet, and prove conflict visibility before
   and after source purge.

2. **P1 — pending-anchor admission gating was ambiguous.** The plan said a
   pending anchor blocks “admission processing,” while its intended safety rule
   is that receiver-owned immutable admissions may continue to append but the
   coordinator cannot consume the next admission or perform a next decision or
   rotation transition. The broader phrase could cause unnecessary source
   backlog and producer pressure.

## Reconciled repairs that passed

- Actual observer `session_user`, exact binding/source membership, identifier
  disposal and non-overlapping receiver/coordinator ceilings close the original
  unauthenticated handoff without giving the coordinator the observer HMAC key.
- Exact stored receipt/admission redelivery is source-independent; an unadmitted
  row is ordinary waiting.
- Recovery anchors are append-only and lifecycle-owned, including baseline,
  decision and rotation revisions plus independent post-commit verification.
- `DECISION` and `KEY_ROTATION` use one gap-free lifecycle and their respective
  atomic generation-local transactions.
- Generation-local key intervals, tenant isolation, producer rollback,
  retention census/barrier/pins, no-cascade families and disabled-by-default
  execution remain coherent.
- API classification remains internal async only with unchanged GraphQL,
  REST/OpenAPI command plane and staff event route.

AER-0051 remains open. A fresh exact-head veto is required after the bounded
conflict-sentinel and anchor-wording recovery.

`DECISION: revision_required`
