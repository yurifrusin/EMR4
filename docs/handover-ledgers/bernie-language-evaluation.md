# Bernie Language and Evaluation Ledger

Last consolidated: 2026-07-15 after LC4V2.

## Current accepted state

LC1-LC4 established the canonical scenario contract, explicit temporal
relations, lossless normalization, coverage lattice, development corpus,
composed interpretation/replay evaluation, and sealed holdout-v1 baseline.
LC4R1-LC4R8 then separated credible implementation defects from unsupported,
ambiguous, malformed, incomplete, contradictory, or stale corpus contracts.

Current development semantic counts are
`880/814/672/154/330/835` for intended action, action semantics, temporal
relation, normalized values, entity semantics, and clarification. Safety is
1,152/1,152 and deterministic variance is zero over 2,304 samples.

LC4R8 accepted two development-only blocker surfaces:

- 53 clarification records, all blocked by upstream semantic-contract defects
  and none ready for a material clarification-policy choice;
- 51 replay/contract mismatches: 11 audit-vocabulary-only, 11 clarification
  tool/contract conflicts, 28 creation/replay-policy conflicts, one negated
  surface/create-contract conflict, and zero genuine replay defects.

LC4R9 repaired the frozen 11 audit-vocabulary cases at the source generator and
regenerated the ordinary development corpus. All 11 now pass complete composed
evaluation. Post-repair corpus hash is
`sha256:f11e98f9bc61b962da0e816fbb918d7f722d3f82c57dfde18a5e323c1b24e9e1`.
LC4R10 then reconciled the other frozen 53 + 40 records at the source-generator
contract. All 93 now pass every composed semantic, clarification, outcome,
tool, delta, authority, and safety dimension. Post-reconciliation corpus hash
is `sha256:af8f3276a50a2defcf4e4f65570a5dd4de0d252544ff6d695792d63e7e518195`.
No independently supported parser gap remains and no parser remediation is
currently authorized.

The final explicit LC4R10 serial development gate passed 831 tests with exactly 22
historical report/queue equality nodes deselected. Gemini 3.5 Flash returned
`DECISION: pass` on exact recovered source head `01d7ac18`; the acceptance
preserves and corrects its non-blocking prose miscount of those historical
nodes. Protected holdout v1 remained sealed.

Yuri then authorized a genuinely fresh holdout v2. A content-blind framework
was independently reviewed before actual content existed; Sol alone authored,
sealed, and consumed the 24-group, 288-variant, 72-multi-turn Gold corpus. The
only `lc4-holdout-v2-baseline-001` run produced 576 aggregate samples with zero
repeat variance. Temporal relations passed 576/576, intended action 528/576,
action semantics 410/576, normalized values 288/576, entity semantics 0/576,
clarification 308/576, safety 532/576, and the complete composed contract
0/576. The procedure passed its evidence contract, but product readiness
failed. Holdout v2 is now sealed alongside v1.

## Next safe sequence

1. Keep holdouts v1 and v2 sealed; use only aggregate v2 evidence for planning.
2. Run a development-only semantic repair and corpus-engineering tranche
   focused on entity semantics, normalization, clarification, and safety.
3. Keep T3.5 provider adapters and live-provider execution separately deferred.
4. Require explicit approval for a later fresh certification holdout or any
   reviewed reuse policy.
5. Authorize parser work only from a newly frozen independently supported
   development surface subset.

## Primary evidence

- `docs/bernie-language-coverage-implementation-plan.md`
- `docs/bernie-t1-stateful-scenario-laboratory.md`
- `docs/bernie-t2-deterministic-behaviour-matrix.md`
- `docs/bernie-t3-shadow-evaluation.md`
- `docs/bernie-lc4-scale-and-holdout-closeout.md`
- `docs/bernie-lc4r7-silver-reconciliation.md`
- `docs/bernie-lc4r8-exit-blocker-reconciliation.md`
- `docs/bernie-lc4r9-generator-contract-repair.md`
- `docs/bernie-lc4r10-contract-reconciliation.md`
- `docs/bernie-lc4v2-fresh-holdout-closeout.md`
- `orchestration/agent_inbox/codex/lc4r10-sol-acceptance.md`
- `orchestration/agent_inbox/codex/lc4v2-sol-acceptance.md`

Protected holdouts v1 and v2 are sealed. Do not enumerate their paths, inspect
content, rerun them, regenerate them, hash-check them, infer labels from them,
or tune against them. T3.1-T3.4 remain blocked-by-default evaluation
scaffolding; T3.5 is deferred.
