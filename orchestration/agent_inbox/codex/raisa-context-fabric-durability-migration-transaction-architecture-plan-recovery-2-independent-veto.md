# Durability migration/transaction architecture second-recovery veto

Date: 2026-08-06

Candidate: `917dff6f06fdbacdc99e66c6802cac1b7f8b5d7f`

Decision: `revision_required`

## Rehydration and postflight

The genuinely fresh reviewer restored
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`; read the API Steward and its exact API Spine sources;
and remained on clean branch
`codex/review-durability-migration-transaction-plan-recovery-2-917dff6f` at
exact HEAD `917dff6f06fdbacdc99e66c6802cac1b7f8b5d7f` before and after.
Local/origin `master` and `handoff/current` remained
`2e34bdad732fdab32fbf778280b3d3c70d66d602`.

The authorised system-Python `--noconftest`, no-cache, no-bytecode focused test
passed 5/5. No `uv`, `pip`, bootstrap, file creation, provider/model/network,
database/source/runtime contact or ref movement occurred.

## Blocking finding

**P1 — the data ceiling contradicted the owner-only aggregate-alias bridge.**
The plan prohibited appointment identifiers and raw product UUIDs in every
future durability relation while relation 2, `diary_context_aggregate_aliases_v1`,
explicitly mapped the product appointment UUID to an opaque aggregate alias.
The API contract confirms that appointment ids are UUIDs. The static test proved
only that both phrases existed and therefore did not detect the contradiction.

The architecture must either keep raw product identity outside the durability
catalogue or define the bridge as one exact tightly bounded owner-private
exception, including explicit privilege and retention treatment. No inert DDL
rehearsal may be admitted until this is resolved and freshly reviewed.

## Reconciled properties that passed

- The bounded receiver-owned admission relation now represents at most one
  immutable `PRIMARY` and one immutable `CONFLICT` sentinel per position.
- Exact duplicate, same-position mismatch, observation-digest reuse, conflict-
  only coordinates and uniqueness races remain bounded and source-purge safe.
- The coordinator accepts a locator only, loads the complete stored admission
  set and rebases on any conflict before redelivery success.
- Primary/conflict evidence remains retained with receipt/checkpoint meaning.
- Pending anchors allow receiver admission appends while fencing coordinator
  consumption and every next decision/rotation transition.
- Authenticated binding, RLS/security-definer ceilings, producer and coordinator
  atomicity, lock/retry ordering, independent anchors, generation-local rotation,
  three-family retention, no-cascade, expand/rollback and API Spine boundaries
  remain coherent.

All passing properties remain declarative architecture evidence only, not
implemented PostgreSQL, credential, transport, runtime or operational-safety
evidence. AER-0051 remains open.

`DECISION: revision_required`
