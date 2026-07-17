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

LC4V6D1 then froze 24 new inspectable layer-specific probes: 12 unknown-
practitioner moves, six matched known-practitioner moves, three resize controls,
and three status controls. All 24 pass extraction, policy, composition, safety,
and two-repeat determinism. The unknown names are linguistically exact at
context-free extraction and safely clarify only after policy directory lookup;
a conflated clarification scorer would fail all 12. DeepSeek's evidence
self-pass was rejected for conceptual normalization, mapping, safety, and hash
gaps; Sol recovered without a correction loop. Gemini passed the authored
contracts and exact recovered head `bef040eb`. No parser/policy runtime change
was made or authorized. D1 supports a future layer-specific certification
contract but does not reveal or rescore V6.

Yuri then authorized genuinely fresh LC4V7 with extraction clarification,
policy clarification, and their composition scored independently. DeepSeek
Flash's empty-framework candidate was rejected after its own closeout admitted
running protected V6 framework tests; Sol did not adopt that source. Sol built
a clean-room framework, and Gemini independently passed exact head `186ccf44`
plus the source-binding amendment at `b4f8cb18` before any content existed.
Sol alone authored and froze 288 fresh scenarios at source `403fcafd` without
executing parser or policy, then committed the unconsumed seal and ran the only
permitted attempt.

V7 is consumed with
`certification_invalid_acceptance_rule_misclassification`. Its aggregate
evaluation evidence is complete and deterministic over 576 samples: zero
validation/runtime/missing-dimension/case-artifact/oracle/variance defects and
safety `576/576`. The executable rule incorrectly placed nonzero product
policy/integration failures in evidence validity, so the raw report returned
`certification_invalid`. It remains unchanged. The aggregate counts also miss
product gates: complete `224/576`, temporal `384/576`, normalization `432/576`,
extraction clarification `408/576`, policy clarification and composition each
`540/576`, policy failures 100, and integration failures 176. Speech-like and
interval are each `0/96`; all ambiguous-practitioner families and unknown-
practitioner schedule explanation are `0/24`. Report hash is
`sha256:fd64f30c7b0869923bb5938f5d7ddd03fb8c8f768c240f9ba364cfdbf104d1fb`.
These are public aggregates only; V7 supplies no case-level repair authority.

LC4V7D1 then used 24 fresh inspectable development probes to isolate and repair
the valid aggregate-directed gaps without touching V7. All 24 pass
normalization, extraction, policy, composition, and safety over 48 repeat
observations with zero variance. Gemini returned `DECISION: pass` on exact head
`19d50763`; the broader serial preservation gate passed 680 nodes with 16
documented historical deselections.

Yuri subsequently authorized genuinely fresh LC4V8. DeepSeek Flash's
content-blind candidate at `2beeffe8` was rejected for conceptual fail-open
evidence behavior; Sol recovered under the lease, and Gemini independently
passed two exact pre-content framework heads, ending at `b24f0293`. Sol alone
authored and froze source `313e6247`, sealed it at `5d465667`, and executed the
only attempt. Its evidence procedure is valid across 576 observations with
zero validation, runtime, missing-dimension, artifact, oracle-leak, or variance
defects. The result is `certification_fail`: complete and policy resolution
are `0/576`; temporal relation and normalized values are `528/576`; safety and
every other semantic dimension are `576/576`; policy and integration failures
are zero. Every group and language-form complete gate fails. Report hash is
`sha256:1b66929304a0a0e1cfecf31e85ab3dc85b891c7ddac73772f84c0815835c7ac6`.
V8 is permanently consumed. Its first aggregate-only hypothesis is a
systematic policy-resolution authoring/projection mismatch, not broad parser
regression; it supplies no case-level repair authority.

Yuri authorized LC4V8D1, which froze 24 fresh inspectable ordinary-development
probes across canonical policy actions, policy boundaries, time surfaces, and
temporal composition. All 24 pass normalization, extraction, independently
scored semantic policy behavior, exact 14-field canonical projection,
composition, and safety across 48 observations with zero variance. Report hash
is `sha256:e7507a4333316012449168f4e11ab93e0b8b60b29c1495b1864eb932bd5fa0bd`;
the non-pass selection is empty. Flash's useful uncommitted candidate was
rejected for conceptual provenance and fail-open evidence defects; Sol
recovered under the lease without a correction loop. Gemini passed both the
immutable authorship and exact baseline head `b72cf748`. The broader gate passed
581 selected nodes with ten documented deselections. D1 supports a V8-specific
Gold/evaluator mismatch, finds no broad temporal/parser defect, and authorizes
no product runtime repair.

Yuri then authorized genuinely fresh LC4V9. Its valid consumed attempt returned
`certification_fail`: complete 88/576, entity semantics 96/576, exact policy
projection 88/576, policy behavior/clarification/composition/replay 528/576,
and every other semantic, safety, evidence, runtime, and variance gate 576/576
or zero as appropriate. All 20 non-create groups failed while no create group
failed. V9 is permanently sealed and supplies no case-level repair authority.

LC4V9D1 used the aggregate pattern to author 30 fresh inspectable non-create
development probes. Its valid pre-repair baseline contained 9 passes, 7
extraction gaps, 14 policy gaps, and no authoring-invalid row. Sol rejected
Flash's conceptually invalid Gold/taxonomy and recovered without a correction
loop. The repaired source passes all 30 cases across extraction, semantic
policy behavior, exact projection, composition, and safety over 60 observations
with zero variance and empty selection. The complete report hash is
`sha256:3429eef910fa871c6d416c1a8dd40d5f42b04581b67b18ddddfc3866ce60c879`.
A fresh Gemini review passed 70 focused and 280 broader selected nodes; Sol
reproduced both commands. Exactly three immutable historical equality nodes
were deselected.

On 2026-07-17 Yuri preauthorized successive genuinely fresh certification
versions beginning with V10 until a valid pass, evidence of stalled progress,
or an unexpected material decision fork. This does not authorize holdout reuse
or weaken content-blind, independent-veto, Sol-only authorship, immutable-seal,
or one-shot requirements.

LC4V10 subsequently passed its sole valid fresh attempt at 576/576 on every
dimension and completed the standing certification cycle. No V11 is
authorized.

Yuri then authorized a development-only multi-model synthetic corpus for the
actual Bernie target: trained receptionist instructions to an assistant. The
pilot exported 96 dialogue-free anchors from ordinary LC development evidence
and produced two noisy candidates per anchor. Wave one was rejected for a
Sol-owned dialogue-form selector defect. Sol recovered only the Codex
generator source under the lease; a first reviewed hash was then rejected for
18 unsupported correction-operation labels. Fresh DeepSeek V4 Flash/high and
Gemini 3.5 Flash/medium contexts each accepted 192/192 on final canonical hash
`sha256:ae14c613ecdd87aac39201d44a8024f3b9216f871c7d5859c4249e7f4026c665`.
Sol admitted all 192 as ordinary development Silver, with no quarantine or
reject. No external corpus, historical diary, or protected holdout was used.
The result makes no real-world, Gold, certification, provider/runtime, or
write-authority claim.

Yuri authorized the next development-only robustness baseline. Sol bound the
accepted corpus and current deterministic interpreter at source `4ac0a901`,
adapted each candidate from its named ordinary-development oracle, and ran two
interpretation/replay/scoring observations per candidate. Exact report hash
`sha256:18501cf5c8d28c0e660a9f5c7b15f7690622e44c90b248d51301c6ece03973c5`
is complete over 192 candidates and 384 observations with zero variance and
safety 384/384. Only the two seed-001 one-shot create variants pass every
dimension. Primary failures are action extraction 114,
temporal/normalization 68, entity semantics 6, and replay-only 2. A fresh
Gemini project independently reproduced the exact baseline and returned
`DECISION: pass`. The result authorizes no repair; the next material choice is
a bounded action/temporal remediation diagnostic versus revising or expanding
the synthetic distribution. One broad discovery command emitted protected
filenames only; no protected content or label was accessed or used.

Yuri authorized the bounded action/temporal tranche. Sol froze 24 candidates
before repair; the pre-repair population was 0/24 complete. Eleven supported
action and ten supported temporal assertions were accepted without allowing
the interpreter to receive expected fields or invent duration/time values
absent from dialogue. The final tranche is 2/24 complete, safety 48/48, zero
variance, with report hash
`sha256:6a4c89992e7a791164bda581b04ae2216a3c7e2661b4a9f29963b220d90b9db2`.
Across all Silver, complete candidates improve from 2/192 to 11/192 while
safety remains 384/384 and variance zero. Exact parent comparison changes 32
authored resize scenarios and no LC4R10 reconciliation scenario. Fresh Gemini
independently reproduced the exact reports and returned `DECISION: pass`.
The tranche closes as an accepted `partial_pass`: the remaining 22 selected
failures expose missing surfaced evidence or oracle, clarification-policy,
entity-transition, and replay-contract incoherence and are not automatic
parser targets. The next material choice is a bounded all-192 corpus/admission
coherence audit with quarantine or regeneration of invalid rows.

Yuri authorized that all-192 coherence audit. The frozen pre-repair result was
85 coherent and 107 invalid rows. Sol repaired exactly eight missing resize-
action surfaces and four schedule-anaphora referents without changing IDs,
evidence coordinates, source semantics, provenance, or authority. Final
current admission is 90 coherent, 102 quarantined, and zero rejected, with
audit report hash
`sha256:4e2f3a5dd3632a8d5f927a2d42a203a909673d89d6406ded886eb37bbbfabd80`
and admission hash
`sha256:55b5c968fa066fc0830e9c80781b0ded1e13520b6f206a41fee9dd0e027687cd`.
Primary quarantines are 78 oracle-policy, 16 whole-action reversal, and 8
replay-contract conflicts. The admitted 90 run twice with 4/90 product
complete, safety 180/180, and zero variance. Fresh Gemini reproduced and
conceptually accepted all findings and returned `DECISION: pass`. All
clarification and reversal forms are absent from current admission; restoring
balanced coverage requires a new coherent v2 anchor contract.

Yuri then authorized a genuinely fresh coherent synthetic Silver v2 course and
successive evidence-backed refinements through completion. V2 contains 96
balanced dialogue-free anchors and 192 admitted candidates across six actions,
eight dialogue forms, and two noise levels. The staged unchanged-product result
progressed from 6/192 complete with safety 356/384, through 16/192 and 138/192,
to final 192/192 complete with safety 384/384 and zero variance. No
clarification policy, replay, scorer, certification, provider/runtime, API,
database, UI, confirmation, deployment/release, or write surface changed.

Final anchor, candidate, admission, and robustness hashes are respectively
`sha256:8609cdd7cab00281c7c2061cf24291be91ca225c5e26c41f8aa5411729f47b23`,
`sha256:1dd79a3209f87e46dbdb2a375c2f2c82a654e9208105f6ee28b4cb5ce4b4d46e`,
`sha256:a3f2ba35e5526d5b4529d37a77214b7034cb11f29517b4a5a3f1df044c5346e0`,
and `sha256:ea4217943fa3a2ec83ec4afcff12cd7eebeba520f225d4e0fb290abb7850dedd`.
A fresh Gemini project reviewed all 192 candidates, reproduced 70/70 focused
tests, and returned `DECISION: pass`, `POLICY_REPLAY_SCORER_CHANGES: false`,
and `PROTECTED_ACCESS: false`. The synthetic course is complete and supplies no
residual supported parser target.

## Next safe sequence

1. Keep holdouts v1-v10 sealed; use only accepted aggregate evidence and
   closeouts for planning.
2. Preserve the original 192-record corpus as immutable historical Silver and
   use only the separately bound 90-row coherent admission for current
   development; do not promote either to Gold or certification evidence.
3. Preserve the accepted robustness baseline as diagnostic failure evidence;
   do not treat `baseline_complete` as a product pass.
4. Preserve the accepted action/temporal `partial_pass`; do not turn its 22
   residual candidates into automatic parser targets.
5. Preserve the accepted coherence `partial_pass_with_quarantine`; do not
   relabel the 102 quarantined rows or change their frozen source oracles.
6. Preserve the accepted balanced v2 population as current ordinary-development
   Silver; do not promote it to real-world, Gold, certification, clinical, or
   production evidence.
7. Preserve the accepted provider-free T3R1 projection of all 192 v2 dialogues;
   its 384/384 expected-decision echo proves plumbing only and establishes no
   model quality.
8. Keep the live T3 gate blocked and pause for Yuri before any synthetic-only
   provider comparison. T3.5/providers plus every product/write surface remain
   deferred.

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
- `docs/bernie-lc4v6d1-development-closeout.md`
- `orchestration/agent_inbox/codex/lc4v6d1-sol-acceptance.md`
- `docs/bernie-lc4v7-fresh-certification-closeout.md`
- `orchestration/agent_inbox/codex/lc4v7-sol-acceptance.md`
- `docs/bernie-lc4v8-fresh-certification-closeout.md`
- `orchestration/agent_inbox/codex/lc4v8-sol-acceptance.md`
- `docs/bernie-lc4v8d1-development-closeout.md`
- `orchestration/agent_inbox/codex/lc4v8d1-sol-acceptance.md`
- `docs/bernie-lc4v9-fresh-certification-closeout.md`
- `orchestration/agent_inbox/codex/lc4v9-sol-acceptance.md`
- `docs/bernie-lc4v9d1-development-closeout.md`
- `orchestration/agent_inbox/codex/lc4v9d1-sol-acceptance.md`
- `docs/bernie-lc4v10-fresh-certification-closeout.md`
- `orchestration/agent_inbox/codex/lc4v10-sol-acceptance.md`
- `docs/bernie-synthetic-receptionist-silver-contract.md`
- `docs/bernie-synthetic-receptionist-silver-closeout.md`
- `orchestration/agent_inbox/codex/synthetic-receptionist-silver-sol-acceptance.md`
- `docs/bernie-synthetic-silver-robustness-baseline-contract.md`
- `docs/bernie-synthetic-silver-robustness-baseline-closeout.md`
- `orchestration/agent_inbox/codex/synthetic-silver-robustness-baseline-sol-acceptance.md`
- `docs/bernie-synthetic-silver-action-temporal-tranche-contract.md`
- `docs/bernie-synthetic-silver-action-temporal-classification.md`
- `docs/bernie-synthetic-silver-action-temporal-tranche-closeout.md`
- `orchestration/agent_inbox/codex/synthetic-silver-action-temporal-sol-acceptance.md`
- `docs/bernie-synthetic-silver-coherence-audit-contract.md`
- `docs/bernie-synthetic-silver-coherence-audit-closeout.md`
- `orchestration/agent_inbox/codex/synthetic-silver-coherence-sol-acceptance.md`
- `docs/bernie-synthetic-silver-v2-anchor-contract.md`
- `docs/bernie-synthetic-silver-v2-closeout.md`
- `orchestration/agent_inbox/antigravity/synthetic-silver-v2-final-review.md`
- `orchestration/agent_inbox/codex/synthetic-silver-v2-sol-acceptance.md`
- `docs/bernie-t3r1-synthetic-shadow-refresh.md`
- `docs/bernie-t3r1-synthetic-shadow-baseline.json`
- `orchestration/agent_inbox/codex/t3r1-synthetic-shadow-refresh-sol-acceptance.md`

Protected holdouts v1-v10 are sealed. LC4V10 validly passed its sole attempt
at 576/576 complete with empty evidence and product failure maps. Do not
enumerate protected paths, inspect content, rerun, regenerate, hash-check,
infer labels, or tune against them. T3R1 remains provider-free and the live T3
gate remains blocked; T3.5 is deferred.
