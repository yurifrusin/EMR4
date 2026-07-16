# LC4V9 Sol Acceptance

Date: 2026-07-16
Decision: `certification_fail_evidence_valid_attempt_consumed`

## Bound evidence

- Attempt: `lc4v9-fresh-certification-001`
- Sol-authored source commit: `abd233ee08a9bd609e35fc2370c21dd52834f353`
- Seal commit: `522f61768be5d33b8936b89e261e581ac3dce945`
- Pre-run aligned head: `0e233caac8d10b3e952a8d78cd69dbfd0ae114ad`
- Aggregate report SHA-256:
  `eda59503699219060cc25a7164390ea1c489540b1e6ba3b22336fea441b02ded`
- Marker state: `consumed`

The marker was durably created before protected reads. Source ancestry, loaded
framework/evaluator paths, byte hashes, Git blobs, thresholds, runtime paths,
manifest hash, unconsumed seal, exact 288-by-two identity, 14-way conjunction,
and aggregate-only report routing all validated. There were zero validation
errors, runtime exceptions, repeat-variance observations, policy failures, or
integration failures. The evidence procedure therefore passed; the product
gates failed.

## Aggregate result

| Dimension | Passes / 576 |
|---|---:|
| complete | 88 |
| intended action | 576 |
| action semantics | 576 |
| temporal relation and bounds | 576 |
| normalized values | 576 |
| entity semantics | 96 |
| lossless source spans | 576 |
| extraction clarification | 576 |
| policy behaviour | 528 |
| policy projection | 88 |
| policy clarification | 528 |
| clarification composition | 528 |
| interpretation tool | 576 |
| replay | 528 |
| safety | 576 |

All six language-form gates failed. The aggregate group list contains all 20
non-create groups and no create group. This is evidence of a systematic
non-create entity-identity/projection weakness, not poor interpretation in
general: action, temporal, normalization, traceability, extraction
clarification, interpretation-tool, and safety dimensions were perfect with
zero variance.

No case-level inspection, rerun, relabelling, rescoring, V9 repair, or parser
remediation from protected evidence is authorized. Holdouts v1-v9 are sealed.
Only this aggregate report, this acceptance, and the aggregate closeout may be
used for planning.

## Preservation gate

The post-seal serial ordinary gate passes 356/356 across current semantic
extraction, LC4V4D3 policy resolution, LC4V8D1 development, LC4V9
content-blind framework/taxonomy, and selected runtime isolation.

Exactly three nodes were deselected:

1. two LC4V4D3 committed-report equality nodes whose historical frozen report
   cannot equal today's corrected source; and
2. the documented pre-existing runtime-isolation node that rejects the
   intentionally configured blocked-gate path in `app/config.py`.

The initial preservation run demonstrated only the two expected historical
equality mismatches; the corrected explicit gate then passed completely.

## Authority

Ordinary development-only diagnostic work may use the aggregate pattern to
author fresh inspectable synthetic probes around non-create identity semantics
and downstream policy projection. Such work must not load, infer, reproduce,
or score V9 cases. A future certification attempt, holdout reuse, or new
holdout version remains a Yuri decision. T3.1-T3.5, providers, historical
data, runtime wiring, APIs, UI, database, deployment, and write authority
remain closed.
