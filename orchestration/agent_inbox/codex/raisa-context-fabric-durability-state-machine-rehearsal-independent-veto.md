# Ariadne independent candidate veto — Context Fabric durability state-machine rehearsal

- Decision: `REVISION_REQUIRED`
- Exact candidate: `2054500a44fbea21d87ecd65b7e7ed5a83492394`
- Review branch: `codex/review-durability-state-machine-2054500a`
- Review worktree: `C:\Users\sarashera\EMR4-worktrees\r19`
- Reviewer authority: exact-head, read-only independent veto

## P1 — resealed receipt/audit structural integrity was incomplete

The reviewer independently showed that `verify_state()` accepted all of the
following after the state was resealed:

```text
receipt_reordered_verify_state: True
receipt_digest_reused_verify_state: True
audit_chain_forged_verify_state: True
```

The accepted audit mutation reversed audits, duplicated an opaque audit id,
replaced the prior-audit digest and substituted an observation digest unrelated
to its classified receipt. The candidate therefore did not enforce canonical
receipt ordering, cross-position observation-digest uniqueness, receipt/audit
coordinate and decision linkage, canonical audit ordering, unique audit ids or
genesis/previous-record chaining.

Required correction: enforce every named structural invariant during state
verification and add direct resealed adversarial proofs.

## P1 — an omitted generation could self-authorize retention

The candidate accepted independently expected census and registry digests as
bare caller values. The reviewer removed the slow generation, resealed the
census and state, supplied that incomplete census's replacement digests and
obtained:

```text
omitted_state_verify_state: True
omitted_census_self_authorized_retention: ELIGIBLE
retention_reasons: ()
```

Required correction: use a separately typed, independently trusted retention
anchor binding the authoritative registry snapshot, census digest and exact
generation membership. Candidate census material must not create that
authority, and the correction must directly reject a self-echoed replacement
anchor.

## Reconciliation and postconditions

The committed 33-case evidence and const schema reconciled mechanically but did
not exercise either adversarial condition. The remaining inspected transition,
rollback, restart, key-boundary, privacy and false-effect-ceiling properties
showed no additional blocker. The exact seven-file pytest command was
interrupted after 16.4 seconds before pytest returned output, so no test count is
claimed.

The review left HEAD and the worktree unchanged and clean. Local/origin
`master` and `handoff/current` remained exactly
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. It made no provider, network,
database, source, runtime, product-data or protected-evidence access.
