# Bernie Language and Evaluation Ledger

Last consolidated: 2026-07-15 after LC4R10.

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

The final explicit serial development gate passed 831 tests with exactly 22
historical report/queue equality nodes deselected. Gemini 3.5 Flash returned
`DECISION: pass` on exact recovered source head `01d7ac18`; the acceptance
preserves and corrects its non-blocking prose miscount of those historical
nodes. Protected holdout v1 remained sealed.

## Next safe sequence

1. Request Yuri's decision between holdout v2 and an explicit holdout-v1 reuse
   policy before LC5 certification work.
2. Keep holdout v1 sealed until that decision is made.
3. Keep T3.5 provider adapters and live-provider execution separately deferred.
4. Authorize future parser work only from a newly frozen independently
   supported surface subset.

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
- `orchestration/agent_inbox/codex/lc4r10-sol-acceptance.md`

Protected holdout v1 is sealed. Do not enumerate its paths, inspect content,
rerun it, regenerate it, hash-check it, infer labels from it, or tune against
it. T3.1-T3.4 remain blocked-by-default evaluation scaffolding; T3.5 is
deferred.
