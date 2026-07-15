# Bernie Language and Evaluation Ledger

Last consolidated: 2026-07-15 after LC4R8.

## Current accepted state

LC1-LC4 established the canonical scenario contract, explicit temporal
relations, lossless normalization, coverage lattice, development corpus,
composed interpretation/replay evaluation, and sealed holdout-v1 baseline.
LC4R1-LC4R8 then separated credible implementation defects from unsupported,
ambiguous, malformed, incomplete, contradictory, or stale corpus contracts.

Current development semantic counts are
`880/814/628/101/300/782` for intended action, action semantics, temporal
relation, normalized values, entity semantics, and clarification. Safety is
1,152/1,152 and deterministic variance is zero over 2,304 samples.

LC4R8 accepted two development-only blocker surfaces:

- 53 clarification records, all blocked by upstream semantic-contract defects
  and none ready for a material clarification-policy choice;
- 51 replay/contract mismatches: 11 audit-vocabulary-only, 11 clarification
  tool/contract conflicts, 28 creation/replay-policy conflicts, one negated
  surface/create-contract conflict, and zero genuine replay defects.

Only the frozen 11 audit-vocabulary cases are authorized for LC4R9
generator-backed repair. The other 53 + 40 remain contract-reconciliation
work. No parser remediation is currently authorized.

## Next safe sequence

1. Change the source generator/contract for exactly the frozen 11 cases.
2. Regenerate through the ordinary development-only path; never edit generated
   fixtures in place.
3. Freeze and review the exact delta.
4. Recompute ordinary development evidence once.
5. Define an LC4R exit gate and keep corpus reconciliation separate from
   parser remediation.
6. Request a user decision only before holdout reuse/v2 or T3.5 live-provider
   execution.

## Primary evidence

- `docs/bernie-language-coverage-implementation-plan.md`
- `docs/bernie-t1-stateful-scenario-laboratory.md`
- `docs/bernie-t2-deterministic-behaviour-matrix.md`
- `docs/bernie-t3-shadow-evaluation.md`
- `docs/bernie-lc4-scale-and-holdout-closeout.md`
- `docs/bernie-lc4r7-silver-reconciliation.md`
- `docs/bernie-lc4r8-exit-blocker-reconciliation.md`
- `orchestration/agent_inbox/codex/lc4r8-sol-acceptance.md`

Protected holdout v1 is sealed. Do not enumerate its paths, inspect content,
rerun it, regenerate it, hash-check it, infer labels from it, or tune against
it. T3.1-T3.4 remain blocked-by-default evaluation scaffolding; T3.5 is
deferred.
