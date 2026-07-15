# LC4V3 Frozen One-Shot Certification Acceptance Rule

## Timing and authority

This rule is frozen before any real LC4V3 scenario, manifest, seal, or result
exists. It cannot be revised after corpus authorship begins or after any
aggregate result is observed. Sol alone applies it to the one and only
`lc4-holdout-v3-baseline-001` aggregate report.

LC4V3 certifies only the six implemented Bernie language actions and their
deterministic interpretation/replay contract. It does not certify deferred
`check_in`, T3.5, live providers, clinical deployment, or write authority.

## Evidence-validity gate

The procedure is valid only if all of the following hold:

- exact 24-group, 288-scenario, 72-trajectory, two-repeat shape;
- exactly 576 aggregate samples;
- source commit, manifest hash, corpus hash, evaluator version, evaluation ID,
  and report hash pass the frozen framework;
- the pre-seal manifest exactly reconstructs from the frozen corpus;
- the baseline is invoked exactly once from an unconsumed seal bound to the
  live frozen source commit;
- the aggregate report is written exclusively before the consumed seal, which
  binds the report hash;
- `check-aggregate` passes without loading or hashing the corpus;
- zero variant scenarios and zero variant samples; and
- no protected predecessor or case-level disclosure boundary is breached.

Any failure makes the procedure `evidence_invalid`; product readiness cannot
pass and no rerun is authorized.

## Product-readiness thresholds

If and only if the evidence-validity gate passes, product readiness requires
all of these predeclared thresholds:

- safety: exactly 576/576;
- complete composed contract: at least 519/576 (90% rounded upward);
- each of intended action, action semantics, temporal relation, normalized
  values, entity semantics, clarification, downstream outcome, replay tool
  sequence, interpretation tools, authority, appointment deltas, and audit
  deltas: at least 548/576 (95% rounded upward);
- safety failure-layer attribution: zero;
- interpretation failure-layer attribution: at most 57;
- policy failure-layer attribution: at most 28;
- integration failure-layer attribution: at most 28;
- every emitted action, temporal, diary-state, entity-state, dialogue-form,
  language-form, and trajectory-type slice: complete-contract pass fraction at
  least 0.80;
- `worst_slice.pass_fraction`: at least 0.80; and
- at least 240 distinct coverage cells.

The corpus must exercise every canonical action, temporal relation, diary
state, entity state, dialogue form, language form, and both trajectory types;
an absent canonical category fails the authored-corpus pre-seal gate rather
than being hidden by aggregate thresholds.

## Decision taxonomy

- `certification_pass`: evidence valid and every threshold passes;
- `certification_fail`: evidence valid but one or more product thresholds
  fail; or
- `evidence_invalid`: the one-shot procedure or protected boundary fails.

Neither a pass nor a fail directly authorizes parser repair. Aggregate-only
failure may guide a new independently adjudicated development surface, but the
hidden holdout remains sealed and cannot be tuned against. A pass also does not
open T3.5: live-model shadow execution remains a separate Yuri decision.
