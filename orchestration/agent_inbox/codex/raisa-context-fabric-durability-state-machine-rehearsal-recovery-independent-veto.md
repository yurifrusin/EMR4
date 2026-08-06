# Ariadne recovery independent veto — Context Fabric durability state-machine rehearsal

- Decision: `REVISION_REQUIRED`
- Exact candidate: `0f3f687be40d57489a4a221161ba900bb63f4040`
- Review branch: `codex/review-durability-state-machine-recovery-0f3f687b`
- Review worktree: `C:\Users\sarashera\EMR4-worktrees\r20`
- Reviewer authority: fresh exact-head read-only independent veto

## P1 — resealed semantic integrity remained incomplete

The first recovery correctly rejected the original receipt/audit structural
attacks and every retention omission, duplication, reordering, substitution or
self-echo attempt. It nevertheless accepted a coupled semantic forgery. The
reviewer changed both the position-5 relevant receipt and its audit to
`CONTIGUOUS_NO_INTERSECTION`, `NO_INTERSECTION`, no affected frames and
`ADVANCE_AFTER_RECEIPT_AND_AUDIT`. After resealing, `verify_state()` returned
true even though the state retained the original diary watermark, retired
frame and reassembly obligation.

Coupled wrong checkpoint disposition was also accepted. Independent audit
mutations of `key_schedule_digest`, `key_id`, `predecessor_position` and
`lifecycle_revision` crossed verification. The first audit could be deleted
and the remaining audit rechained to genesis, and the state lifecycle revision
could be inflated arbitrarily.

Required correction: verify the complete semantic receipt/audit/effect graph,
including canonical baseline and audit prefix, decision-specific disposition,
exact predecessor and key linkage, lifecycle accounting, and deterministic
rederivation of watermarks, frame retirement and coalesced obligations.

## Reconciliation and postconditions

- Five-source rehydration completed.
- The exact seven-file packet collected and passed 195 tests with exit code 0.
- Ruff and `git diff --check` passed.
- Before/after HEAD remained
  `0f3f687be40d57489a4a221161ba900bb63f4040`.
- The review branch and worktree remained unchanged and clean.
- Local/origin `master` and `handoff/current` remained exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.
- No provider, network, database, source, runtime, product-data, protected
  evidence, file or ref mutation occurred.
