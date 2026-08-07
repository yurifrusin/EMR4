# Fresh exact-HEAD veto: second-recovery durability function/trigger bodies

Date: 2026-08-07

Candidate HEAD: `5a3c5b5118f80153d545bf30ae9db99acb187cd7`

Candidate contract:
`sha256:78db131b6da9482e7092a3530d747030010cf027c582f54f49b959827f4bff8a`

## Exact review postcondition

- Exact HEAD was clean before and after review.
- Every packet-authorized plan, recovery, design, threat, parent/child contract,
  builder/body/validator/schema, test and API Spine path was inspected.
- Builder `--check` passed at the exact candidate digest.
- The prescribed packet passed 192/192 with only the two existing dependency
  deprecation warnings.
- The exact prescribed Ruff rerun passed. An earlier transcription used one
  hyphenated filename and returned E902 before analysis; it was not a candidate
  defect and changed no file.
- `git diff --check` passed; final status was empty and final HEAD unchanged.

## Findings

### P1 — recovery anchor does not reverify complete committed state

`append_recovery_anchor_v1` is required to independently reverify the committed
checkpoint, lifecycle, receipt/audit and controlling digests before append. Its
AST reads only binding, barrier, generation, checkpoint and anchor relations.
It never reads lifecycle, classified receipt, durability audit or key evidence,
so it can construct or replay an anchor from copied generation/checkpoint fields
without proving the committed lifecycle and receipt/audit packet.

### P1 — coordinator receipt replay inherits source reads

`source_position_set` and other dependent reads occur unconditionally before
conflict/receipt routing. Derived `RECEIPT_REPLAYED` paths consequently read
`diary_context_observation_outbox_v1`, contrary to the frozen source-independent
replay rule and the path-sensitive rule that retained exact or terminal replay
must not inherit source/product reads from another branch.

### P2 — set-key pairs are not duplicate-free in structural schema

Both generated `key_pairs` schemas have `minItems: 1` but no
`uniqueItems: true`. Duplicating a valid pair produced zero Draft 2020-12 schema
errors. The semantic validator rejects the duplicate, but schema-level primitive
closure is incomplete.

## Surviving independent challenges

R5A conflict precedence/cardinality/digest derivation, R5B head assignment and
complete replay comparison, R5C identity joins/per-generation coverage and R5D
literal field-specific maps otherwise survived. Owner, security-definer,
volatility, timing and deferrability mutations each produced dedicated
non-digest issues. No additional trigger-totality, current-XID, retention-grace,
enum, privilege-ceiling or API Spine defect was established.

## Claim boundary

GraphQL remains read-only; the committed-event REST surface remains GET-only;
events remain observation-only. No SQL/DDL, database/source contact,
runtime/provider/data path, deployment, production, release, Pages or
protected-ref authority was opened.

DECISION: revision_required
