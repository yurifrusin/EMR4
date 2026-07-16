# LC4V6 Sol Acceptance

Date: 2026-07-16

Decision: `evidence_valid_certification_fail_permanently_sealed`

## Provenance and procedure

Yuri authorized one genuinely fresh certification holdout. DeepSeek V4
Flash/high through Claude Code `--bare` worked only on the empty content-blind
framework. Sol rejected its conceptual fail-open candidate and recovered the
framework under the lease. Gemini 3.5 Flash independently passed exact
recovered framework head `f53bb976` before any V6 content existed. External
sessions were then closed.

Sol alone froze the thresholds, authored the 24-family/288-scenario synthetic
Gold corpus, and bound the source, corpus, manifest, framework, evaluator,
acceptance rule, and protected runner. Source commit
`0527848bb7d4c86a4c138f49016472c447c05757` is bound by source hash
`sha256:d0ea315cbe2da3c2fbb68cd2934484e4d96e59db1ae8a164f7394fab48482a64`.
The unconsumed seal was committed and pushed before evaluation.

The exact named pre-run check passed from a clean protected worktree. The
ordinary non-intercepted extractor and explicit Option A policy path then ran
once for attempt `lc4v6-fresh-attempt-001`. The source seal, aggregate report,
attempt marker, and durable lock were written by the fail-closed transition.
No case-level output was written or committed. V6 is permanently consumed and
cannot be rerun, relabelled, repaired, or reused implicitly.

## Evidence validity

All evidence gates pass:

- 24 groups, 288 scenarios, 72 multi-turn and 216 one-shot scenarios;
- 288 unique coverage cells, all six actions, two repeats, and 576 samples;
- zero evaluation exceptions, missing dimensions, case artifacts, and repeat
  variance;
- exact source/corpus/manifest/framework/evaluator bindings;
- valid aggregate arithmetic, slices, consumed seal, marker, receipt, and
  durable lock.

The aggregate-only post-run validator plus ordinary semantic extraction,
Option A policy, framework, acceptance, Ariadne, autonomous-continuation, and
handover preservation gate passed `264/264` serial tests.

Aggregate report hash:
`sha256:02f1555adc494672b15aed722f86414eb4570014e795f79210ae10b7936d417a`.

## Frozen product decision

The frozen acceptance rule returns `certification_fail`:

- complete composed contract: `540/576` (minimum `548`);
- safety: `576/576` with zero safety-layer failures;
- interpretation failures: `36` (maximum `28`);
- policy failures: `0`; integration failures: `0`;
- every individual dimension meets its `548/576` floor: clarification is
  `552/576`, normalized values `564/576`, and the other ten are `576/576`;
- the worst family slice is `move_unknown_practitioner` at `0/24`, so the
  every-slice and worst-slice gates fail;
- the paraphrase language slice is `34/48`; each other language-form slice is
  `46/48`;
- all create, cancel, and explain families pass completely. The six resize and
  status families are each `22/24`; the other move families pass completely.

This is not poor overall progress: safety, policy, integration, ten dimensions,
and most aggregate slices are complete. It is also not certification. The
valid result identifies a bounded aggregate interpretation weakness, dominated
by unknown-practitioner move language and accompanied by smaller clarification
and normalization deficits. Aggregate evidence supplies no case-level parser
proof, so it does not authorize direct parser repair or inspection of V6
content.

## User decision boundary

Recommended next choice: authorize a bounded development-only `LC4V6D1`
diagnostic tranche. Sol would author fresh, inspectable ordinary probes from
the public aggregate categories only, with emphasis on unknown-practitioner
move requests, paraphrase robustness, clarification, normalization, and the
smaller resize/status surface. The tranche would first separate authoring,
parser, and policy causes, then remediate only independently supported ordinary
gaps. It would not inspect, import, rerun, or tune against V6.

After a later development exit, any V7 holdout or reuse proposal remains a
separate Yuri decision. T3.1-T3.4 remain intact and blocked by default;
T3.5/providers, local-model development use, historical material, product
runtime, routes, APIs, UI, database, deployment, release, and all live/write
authority remain deferred.
