# Durability function-and-trigger-body exact-veto recovery

Date: 2026-08-07

Status: normative Sol recovery frozen before replacement implementation

Rejected candidate source HEAD:
`f51f5b65dd77d9282e5325a5e4f17edd872d14df`

Independent veto:
`orchestration/agent_inbox/codex/raisa-context-fabric-function-trigger-body-architecture-exact-veto.md`

Immutable parent digest:
`sha256:4b0ec20ba00010a1034c6d3c5eedfe8de3f329d7cd5ef495e5878689cdaacba8`

## Recovery classification

The third candidate is rejected before acceptance. Its typed IR and generated
artifacts are untrusted implementation source under
`docs/ariadne-orchestrator-recovery-lease.md`. The defect is conceptual rather
than a same-lane mechanical omission, so Sol owns reconciliation. Bounded
separable workers may implement disjoint corrections, but no worker may accept
its own output.

This recovery does not revise the accepted parent architecture, API Spine,
authority allocation, evidence label or claim ceiling. It closes the four
independently demonstrated under-specifications below.

## R1 — Exact coordinator state machine and effects

`apply_durability_transition_v1` must derive one closed state from exact locked
rows rather than treating all non-primary states as missing admission.

- Exact retained receipt replay is source-independent and inert after complete
  receipt integrity comparison.
- Existing terminal/rebase replay is derived from stored lifecycle,
  checkpoint, result and reason integrity; no caller-supplied terminal fact is
  trusted.
- A retained conflict sentinel, absent or duplicate admission, missing or
  ambiguous predecessor, demonstrated gap, stream-epoch mismatch, key
  membership failure, invalid anchor fence or conflicting dependent state
  takes an explicit typed fail-closed/rebase branch.
- A receipt-apply branch requires exactly one authenticated PRIMARY admission
  at the expected predecessor/epoch and exact key interval. It atomically
  writes the receipt, advances checkpoint and watermarks, retires superseded
  frames one way, coalesces the obligation/dependent effects, records minimized
  lifecycle/audit evidence and returns the exact closed composite.
- No result kind may fabricate a PRIMARY, apply, replay, rebase or terminal
  outcome. Every effect is represented by an operand-derived typed node and is
  present in the independently rederived body summary.

Hostile acceptance must reject removal or substitution of every state proof or
required effect, including a resealed deletion of the central producer event
membership assertion.

## R2 — Complete retention census, grace and key proof

Retention must remain `SERIALIZABLE` and barrier-locked. Its eligibility is
derived from one internally consistent census:

- non-consumed generations are exactly lifecycle states `ACTIVE`,
  `REBASE_REQUIRED` and `REVOKED`; only `CONSUMED` is excluded;
- checkpoint, anchor, key and active-pin rows are scoped to the same exact
  practice/source/stream and the generation identities in that census;
- the slowest checkpoint is the operand-derived minimum over the complete
  checkpoint set, with exact one-per-generation coverage;
- source, receipt/checkpoint and audit grace compare the exact policy intervals
  to `transaction_timestamp()` and the derived through-position; and
- key coverage proves an actual overlapping interval for every retained
  generation/position that remains required, not merely a non-empty key set.

Reason codes are exactly REC19 and no others:
`ELIGIBLE`, `EXECUTION_DISABLED`, `CHECKPOINT_LAG`, `ACTIVE_PIN`,
`KEY_OVERLAP`, `GRACE_PENDING`, `AMBIGUOUS_CENSUS` and
`NO_NON_CONSUMED_GENERATION`. The validator must reject an out-of-enum `CONST`.
Purge rederives the same eligibility in its transaction and can delete only
bounded rows from the payload-free source relation.

## R3 — Current-transaction non-temporal fence

For an appointment update whose start time and duration are unchanged, the
deferred fence must prove the absence of effects caused by this exact top-level
transaction, not the absence of historical rows.

- Matching committed events are current-XID rows for the exact appointment,
  event type and schema.
- Matching aliases are only aliases inserted by the current XID for the exact
  appointment/source/stream. An older immutable alias is legitimate history
  and must not fail the branch.
- Matching outbox rows are only current-XID rows tied through the exact alias,
  raw event, aggregate revision and transaction/appointment relationship. An
  unrelated or historical practice/stream row must not fail the branch.
- Head movement is proved from `OLD`/`NEW` position change and the exact
  current-transaction event/outbox relationship; historical head state alone
  is not an effect.

Temporal updates retain the complete exact bijection. The existing
same-top-level-transaction second-update rejection remains fail closed.

## R4 — Independent semantic and structural closure

Validation may not rely on regenerated-baseline byte equality as the decisive
reason a hostile mutation fails.

The semantic validator must independently bind and validate:

- the immutable parent digest and effective-parent derivation;
- the exact ordered twenty-six recovery operations, including every scalar
  value and exact REC19 membership;
- all twenty-two full signatures, with owner, executor, security-definer,
  public-execute denial, fixed search path, volatility, strictness, parallel
  safety, inputs and output;
- all thirteen trigger declarations and their exact event/return matrix;
- the exact effective-role privilege matrix and the rule that runtime roles
  gain no product DML, outbox deletion or trigger-function execute authority;
- every enum-typed `CONST` against the effective type catalogue; and
- independently derived program effects, reachable proofs, terminals and call
  graph against their body-specific summaries.

The generated JSON Schema must freeze critical normative scalar envelopes with
ordered `const`/`prefixItems`: recovery operations, effective-parent summary,
full signatures, trigger declarations, privilege rows, enum vocabularies,
renderer/artifact boundaries and body identities/order. Body instruction ASTs
remain structurally typed and semantically validated; whole-body `const`
snapshots are not a substitute for semantic proof.

The hostile packet must reseal the candidate and regenerate the structural
schema where applicable, then demonstrate rejection by the independent
semantic validator and/or a critical scalar schema constraint before any
whole-baseline equality assertion. It must include at least:

1. owner direct outbox `DELETE` privilege widening;
2. REC19 enum widening and an invalid retention-reason `CONST`;
3. producer security-definer owner swap;
4. removal of the producer central event-membership assertion;
5. coordinator conflict/predecessor/epoch/key/effect removal;
6. retention filtered to `ACTIVE`, unscoped census rows, omitted grace or
   count-only key evidence; and
7. historical alias/outbox rows treated as current non-temporal effects.

## Lane allocation and integration

- **Coordinator/retention lane:** entry-point bodies and focused semantic tests.
- **Transaction-fence lane:** appointment trigger body and focused historical
  versus current-XID tests.
- **Normative-closure lane:** semantic validator, structural schema and resealed
  hostile tests.
- **Sol:** recovery contract, any shared catalogue/builder reconciliation,
  generated contract/schema, aggregate deterministic acceptance and fresh
  independent exact-head veto.

Owned implementation paths must be disjoint. Repository pytest processes remain
serial. Generated artifacts are rebuilt only after the three sources reconcile.

## Acceptance and unchanged boundary

The replacement must pass the original plan and all prior recovery acceptance,
the new seven attack families above, Ruff and `git diff --check`, then receive a
fresh candidate-independent veto from a new exact-HEAD read-only worktree.
Rejected candidate `f51f5b65dd77d9282e5325a5e4f17edd872d14df`
cannot become the accepted source.

This remains pure, provider-free, unmounted and repository-local. It renders or
executes no SQL/DDL; creates no migration, database object or operational state;
opens no source/feed/watcher/listener, product/patient read, provider, command,
runtime, deployment, production, release, Pages or protected-ref authority.
