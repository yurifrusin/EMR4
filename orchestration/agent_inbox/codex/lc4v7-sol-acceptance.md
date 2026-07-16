# LC4V7 Sol Acceptance

Date: 2026-07-16

Decision: `certification_invalid_acceptance_rule_misclassification`

## Result

The single permitted V7 attempt is complete and permanently consumed. Its raw
aggregate report returned `certification_invalid`.

The underlying evaluation evidence is complete and deterministic: exactly 288
scenarios, 576 samples, 24 families, 288 unique coverage cells, 72 multi-turn
and 216 one-turn scenarios, zero validation errors, runtime exceptions,
missing dimensions, case artifacts, oracle leaks, or repeat variance. Safety
is `576/576`.

The invalid decision comes from a frozen acceptance-rule defect, not missing or
variable evaluation evidence. The executable rule placed nonzero
`policy_failures` and `integration_failures` inside evidence validity, although
the longer frozen Sol contract places those counts in the later product gate.
The raw report therefore labels an evidence-valid product failure as
`certification_invalid`. The report and decision remain unchanged; V7 is not
rerun, repaired, rescored, or relabelled.

There is no concealed product pass. The aggregate counts independently miss
multiple frozen product gates: complete `224/576`; temporal relation `384/576`;
normalized value `432/576`; extraction clarification `408/576`; policy
resolution `476/576`; policy clarification and clarification composition each
`540/576`; interpretation tool contract `462/576`; replay contract `502/576`;
policy failures 100; and integration failures 176. Intended action, source span,
and safety are each `576/576`; entity semantics is `544/576` and action
semantics `464/576`.

Public aggregate language results are correction `68/96`, interval `0/96`,
paraphrase `20/96`, plain `68/96`, speech-like `0/96`, and word-order `68/96`.
All six ambiguous-practitioner families are `0/24`; unknown-practitioner
schedule explanation is also `0/24`. These are aggregate planning categories
only and provide no case-level repair authority.

The aggregate report hash is
`sha256:fd64f30c7b0869923bb5938f5d7ddd03fb8c8f768c240f9ba364cfdbf104d1fb`.
The frozen corpus hash is
`sha256:966a537efb772a970da5c4159c2cca78fa861d4a8efd8edeea7bbaf9fcbfd068`;
the manifest hash is
`sha256:10826fefbfdc05dde5727e8556a6eef05e65c4e0d7fe6451a87c9260960a280e`.

## Provenance and framework review

The layer-specific contract and thresholds were frozen before content. The
first DeepSeek V4 Flash/high candidate is preserved at `77905e63` / `418fec3f`
but rejected because its own closeout admitted running protected V6 framework
tests despite the no-access packet, and it named the wrong final head. Sol did
not open or adopt that source.

Sol built a clean-room replacement from the frozen contract and ordinary D1
interfaces. Gemini 3.5 Flash independently returned `DECISION: pass` on exact
empty-framework head `186ccf44`. Sol then corrected a pre-content Git
self-reference issue by binding the seal to an ancestor commit containing the
exact corpus blob; Gemini independently returned `DECISION: pass` again on
exact amended head `b4f8cb18`. Both external sessions closed before content.

Sol alone authored 288 fresh scenarios without executing parser or policy,
froze the corpus at source `403fcafd`, and committed the unconsumed seal at
`1433b131`. The pre-seal serial framework, authorship, D1, semantic-extraction,
and Option A policy gate passed 284 nodes. The only baseline then produced the
aggregate report and consumed marker committed at `3bfbc577`.

## Authority and next boundary

All V7 fixture, support, authoring, manifest, seal, receipt, test, and per-case
surfaces are now protected with v1-v6. Do not open, list, search, import, run,
regenerate, hash-check, infer labels from, repair, or tune against them. Only
this acceptance, the aggregate report, and aggregate closeout remain available
for planning.

The next decision is Yuri's. Sol recommends a bounded ordinary-development
V7D1 using only fresh inspectable probes derived from the public aggregate
categories. It should first repair the generic future-certification taxonomy
(`product failure` must not become `evidence invalid`), then separate authoring,
parser, and policy causes for speech-like time, cross-turn intervals,
ambiguous-practitioner choices, and unknown-practitioner schedule explanation.
No parser or policy repair is authorized until those fresh probes adjudicate a
valid gap.

A fresh V8 should wait for D1 exit. Any V7 inspection, rerun, rescore,
relabelling, or repair requires a separate explicit policy and is not
recommended. T3.1-T3.4 remain intact and blocked; T3.5/providers and all
product/write/deployment surfaces remain deferred.
