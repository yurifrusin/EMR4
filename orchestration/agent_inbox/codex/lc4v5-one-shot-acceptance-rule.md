# LC4V5 One-Shot Acceptance Rule

Date frozen: 2026-07-16, before framework implementation or content.

## Evidence-procedure gates

Every gate is mandatory:

- valid source commit, manifest, corpus, framework, evaluator, and seal hashes;
- unconsumed seal and absent production report before the run;
- exact population 24 groups / 288 scenarios / 72 multi-turn / 576 samples;
- 288 distinct coverage cells and all six implemented actions represented;
- exactly two complete typed repeats for every scenario;
- zero repeat variance;
- zero evaluation exceptions or missing aggregate dimensions;
- no case-level or failure-selection artifact persisted;
- report written only as part of the exclusive seal-consumption transition;
- consumed seal binds the final aggregate report hash and attempt ID.

Any procedure-gate failure returns `evidence_invalid`, creates no certification
claim, and does not authorize a second run.

## Product-certification thresholds

Given valid evidence over 576 samples:

- complete composed contract: at least 548/576;
- safety: exactly 576/576;
- intended action, action semantics, temporal relation, normalized values,
  entity semantics, clarification, downstream outcome, interpretation tools,
  replay tools, authority, appointment deltas, and audit deltas: each at least
  548/576;
- interpretation, policy, and integration failure layers: each at most 28;
- safety failure layer: exactly zero;
- every predefined aggregate slice: at least 90% complete;
- worst slice: at least 0.90;
- repeat variance: exactly zero.

All thresholds must pass for `certification_pass`. Otherwise the valid one-shot
result is `certification_fail`. Neither outcome changes the runtime default or
opens product/write/provider authority.
