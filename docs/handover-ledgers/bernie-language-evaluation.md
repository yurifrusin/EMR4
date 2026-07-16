# Bernie Language and Evaluation Ledger

Last consolidated: 2026-07-15 after LC4V3.

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

LC4V2R1 then introduced a new Sol-authored 21-case Gold development matrix for
entity relations and lexical duration normalization. It improved from 4/21 to
21/21 complete with zero variance. DeepSeek Flash supplied one rejected
candidate; Sol recovered its fail-open evidence checker and negation scope, and
Gemini independently passed exact recovered head `fa973311`. The ordinary
development corpus remained `880/814/672/154/330/835`, safety 1,152/1,152,
variance zero, and hash-identical. The final serial preservation gate collected
383 nodes and completed with 381 passes, one expected xfail, and one expected
skip. Neither sealed holdout was accessed.

LC4V2R2 then froze 14 matched unsafe/safe pairs across all six implemented
actions. Its baseline passed 17/28; the recovered implementation passes 28/28
with zero variance across 56 fixture evaluations. DeepSeek Flash's uncommitted
self-pass was rejected for incomplete provenance, incorrect aggregate claims,
and over-broad regexes. Sol recovered under the lease, and Gemini independently
passed exact head `ae4304f8` with 295/295 tests. Ordinary development remains
`880/814/672/154/330/835`, safety 1,152/1,152, variance zero, and corpus hash
`sha256:af8f3276a50a2defcf4e4f65570a5dd4de0d252544ff6d695792d63e7e518195`.
A final 464-node serial preservation gate completed with 462 passes, one
expected xfail, and one expected skip.
A recovery search returned protected v1 path names but no protected content or
label; the metadata-only incident does not authorize reuse.

LC4V2E1 then bound only the exact accepted R1, R2, R10, and ordinary manifest
artifacts. Its deterministic exit report returned `no_r3_authorized`, report
hash `sha256:aa65f631f748948cdaf0c7adc280a2db1d86b3f2f4779edc1f67ecc3c0412fba`.
Gemini independently passed exact head `e0d30bd8`. The current development
repair sequence is complete; this is not certification.

Yuri authorized genuinely fresh LC4V3 certification. DeepSeek Flash supplied
one rejected content-blind framework candidate; Sol recovered it, and Gemini
independently passed exact recovered framework head `170b44ab` before content
existed. Sol alone authored and froze the fresh corpus at `c57a4d62`, closed
external sessions, sealed it, and ran the single permitted baseline. Evidence
is valid and variance is zero. The frozen product decision is
`certification_fail`: complete 494/576, entity semantics 494/576, both tool
dimensions 496/576, safety 576/576, temporal and normalization 576/576, and
288 distinct coverage cells. The plain-language slice was 0/82 while every
other language-form slice passed completely. That aggregate discontinuity is
consistent with an authoring/representation defect, but it supplies no
case-level parser evidence and cannot authorize inspection, tuning, repair, or
a rerun. Holdouts v1-v3 are sealed.

LC4V4 was subsequently authorized and remains a sealed aggregate
`certification_fail`; its ordinary development sequence D1-D3 identified,
repaired, and then explicitly versioned the valid utterance and policy surfaces
without using sealed case-level evidence. LC4V4D4 integrated the approved
Option A policy into the ordinary composed development harness while leaving
legacy as the exact default. The 60-probe legacy baseline hash is
`sha256:665851ffe055efb40f2ba1e43291d6b945c4764b4f441837781d4fc964d6ff27`.
All 20 Option A cases pass over 40 observations with zero variance; all 13
fail-closed gates pass and the report hash is
`sha256:dd1ecc077a59bf05e777eda1f3a5450c0a1b97a4c8a3fd21dc0363d473abd653`.
Gemini independently returned `DECISION: pass` on exact recovered report head
`bd51caf0`. The exact six incompatible D1 expectations remain frozen and are
represented only as explicit versioned overlay differences.

LC4V4D5 then audited explicit Option A over all 60 ordinary D1 probes. It
retains 240 complete observations with zero variance and classifies exactly
`35/20/1/3/1`: 35 legacy-equivalent, 20 accepted D4 changes, one benign
exact-duplicate relation, three missing-mutation-delta blockers, and one resize
target-conflict-plus-delta blocker. All 27 gates pass; report hash is
`sha256:e2c461ee3b1821c94574b33693efa88d21b99ecf9a95b1ac723b24a933c50564`.
Gemini returned `DECISION: pass` on exact head `4fba7408`. D5 is diagnostic only.

LC4V5 later remained a permanently sealed aggregate certification failure.
Its fresh ordinary R1 tranche closed the three public aggregate-localized
development surfaces at 18/18 complete and 18/18 safe with zero variance, and
E1 passed all 13 development-exit gates. Yuri then authorized a genuinely
fresh V6 rather than reuse.

LC4V6 used the same content-blind separation: DeepSeek Flash supplied only an
empty framework candidate, Sol recovered it, and Gemini returned
`DECISION: pass` on exact recovered framework head `f53bb976` before content
existed. Sol alone authored and sealed source commit `0527848b`, then executed
the only permitted attempt. Evidence is exact and valid across 576 samples,
with zero exceptions, missing dimensions, case artifacts, or variance. The
frozen decision is `certification_fail`: complete `540/576`, safety `576/576`,
interpretation failures 36, policy/integration failures zero, clarification
`552/576`, normalization `564/576`, and every other dimension `576/576`.
The worst public family is `move_unknown_practitioner` at `0/24`; paraphrase
is `34/48`. Report hash is
`sha256:02f1555adc494672b15aed722f86414eb4570014e795f79210ae10b7936d417a`.
V6 is permanently consumed and supplies aggregate diagnostic direction only,
not case-level parser evidence.

## Next safe sequence

1. Keep holdouts v1-v6 sealed; use only accepted aggregate evidence and
   closeouts for planning.
2. Pause for Yuri's choice on the recommended development-only LC4V6D1 tranche.
3. If authorized, author fresh inspectable ordinary probes from the public
   aggregate categories and separate authoring, parser, and policy causes
   before remediation.
4. Require a later explicit Yuri decision for any V7 holdout or reuse policy
   after an accepted development exit.
5. Keep T3.1-T3.4 blocked by default and T3.5/providers plus every product/write
   surface deferred.

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
- `docs/bernie-lc4v2r1-entity-normalization.md`
- `orchestration/agent_inbox/codex/lc4v2r1-sol-acceptance.md`
- `docs/bernie-lc4v2r2-safety-language.md`
- `orchestration/agent_inbox/codex/lc4v2r2-sol-acceptance.md`
- `docs/bernie-lc4v2-development-exit-reassessment.md`
- `orchestration/agent_inbox/codex/lc4v2e1-sol-acceptance.md`
- `docs/bernie-lc4v3-fresh-certification-closeout.md`
- `orchestration/agent_inbox/codex/lc4v3-sol-acceptance.md`
- `docs/bernie-lc4v4d4-composed-integration-closeout.md`
- `orchestration/agent_inbox/codex/lc4v4d4-sol-acceptance.md`
- `docs/bernie-lc4v6-fresh-certification-closeout.md`
- `orchestration/agent_inbox/codex/lc4v6-sol-acceptance.md`

Protected holdouts v1-v6 are sealed. Do not enumerate their paths, inspect
content, rerun them, regenerate them, hash-check them, infer labels from them,
or tune against them. T3.1-T3.4 remain blocked-by-default evaluation
scaffolding; T3.5 is deferred.
