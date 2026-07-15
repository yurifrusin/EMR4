# LC4V4 Sol Acceptance

Date: 2026-07-15

Decision: `certification_fail`

Evidence validity: valid. The aggregate report has the frozen identity,
population, evaluator, source commit, hashes, coverage, repeat policy, and
aggregate-only schema. Its report hash validates. External model sessions were
closed before authorship; the production baseline ran exactly once; its report
was written before the consumed seal. No case-level artifact was reopened
after consumption.

The first pre-authoring attempt remains invalid because it exposed one
protected filename as metadata. Yuri explicitly authorized fresh attempt
`lc4v4-fresh-attempt-002`. V2 never activated because its administrative guard
failed before content; V3 activated only after a green pushed checkpoint. A
direct Windows script invocation then failed before module import and before
any target path existed; the unchanged module entry point performed the sole
exclusive corpus materialization. This was not a partial corpus, seal, or
baseline run.

## Aggregate result

- report hash:
  `sha256:9fa0cfe19d6e24e19630d415e4a778c89b6381057ae661e4c7d6c53c088d68f5`;
- source commit: `9c005e777d008e03a3ee085382915dfc1dc652c6`;
- population: 288 scenarios, 72 trajectories, 576 samples;
- coverage: 288 distinct cells;
- repeat variance: zero;
- complete composed contract: 70/576;
- intended action: 576/576;
- temporal relation: 576/576;
- normalized values: 480/576;
- entity semantics: 240/576;
- action semantics: 388/576;
- clarification: 294/576;
- downstream outcome: 272/576;
- interpretation tools and replay tool sequence: 252/576 each;
- authority: 280/576;
- appointment deltas: 456/576;
- audit deltas: 472/576;
- safety: 466/576;
- failure layers: interpretation 500, policy 304, integration 340, safety 110;
- worst slice: 0.0000.

The result fails the frozen safety, completeness, semantic-dimension,
failure-layer, and slice thresholds. Coverage and determinism pass. The
decision is therefore mechanically `certification_fail`.

## Authority decision

This result does not authorize parser repair, case inspection, corpus
relabelling, rerun, or holdout reuse. It also does not open T3.1-T3.4, T3.5,
providers, runtime/write authority, deployment, or release.

The next recommended work is an ordinary development-only diagnostic tranche
using independently authored probes across the aggregate weak axes. It must
separate parser defects from policy/contract and corpus-authoring defects
without copying or inferring any v4 case. Any later certification requires a
new Yuri decision.
