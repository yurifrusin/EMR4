# Bernie LC4V5 Fresh Certification Closeout

Date: 2026-07-16

Decision: `valid_one_shot_certification_fail`

LC4V5 attempt `lc4v5-fresh-attempt-001` completed exactly once. The permanent
attempt marker exists, the seal is consumed, and v5 cannot be rerun or reused.

## Evidence validity

All evidence-procedure gates passed:

- source, corpus, manifest, framework, evaluator, seal, and report hashes bind;
- the report was absent and the seal unconsumed before the run;
- exact population is 24 groups, 288 scenarios, 288 coverage cells, 72
  multi-turn trajectories, two typed repeats each, and 576 samples;
- all six implemented actions are represented;
- evaluation exceptions, missing dimensions, case-level artifacts, and repeat
  variance are all zero; and
- the consumed seal binds attempt ID `lc4v5-fresh-attempt-001` and report hash
  `17c123559a8c708fa0d122a2de1dbadc465e1d4e93a19814c5968f00f0b9c88b`.

Consumed seal hash:
`f3b8d31de29b04846273cdab4100d5776046fe988fda978518a7462a4f34d071`.

## Product thresholds

| Measure | Result | Threshold | Gate |
|---|---:|---:|---|
| Complete composed contract | 512/576 | at least 548 | fail |
| Safety | 560/576 | exactly 576 | fail |
| Interpretation failures | 48 | at most 28 | fail |
| Policy failures | 2 | at most 28 | pass |
| Integration failures | 16 | at most 28 | pass |
| Safety failures | 16 | exactly 0 | fail |
| Repeat variance | 0 | exactly 0 | pass |
| Every predefined slice / worst slice | below 0.90 | at least 0.90 | fail |

Every frozen individual semantic dimension clears its 548/576 threshold:

- intended action 576, action semantics 576, temporal relation 576;
- normalized values 552, entity semantics 576, clarification 552;
- downstream outcome 574;
- interpretation tools 560 and replay tools 560;
- authority 576; and
- appointment deltas 574 and audit deltas 574.

The result therefore shows broad semantic correctness with overlapping
cross-contract failures, not a general parser collapse.

## Aggregate localization

All 64 complete-contract failures are concentrated in three predefined family
aggregates:

- create-approximate: 8/24 pass (16 failures);
- move-interval: 0/24 pass (24 failures); and
- ambiguous-resize-duration: 0/24 pass (24 failures).

All other 21 family aggregates pass 24/24. Aggregate arithmetic also shows:

- the 24 normalized-value failures align with the move-interval aggregate;
- the 24 clarification failures align with the ambiguous-resize aggregate; and
- the 16 safety/tool failures align with the stateful create-approximate
  aggregate.

Those alignments are aggregate inferences, not per-case inspection. V5 stores
no case selection or failure list and must remain closed.

## Interpretation

Compared with the same-size v4 aggregate, v5 rises from 70 to 512 complete
samples and from 466 to 560 safe samples. Because the corpora are genuinely
fresh, this is strong directional evidence rather than a paired-case estimate.
Certification still correctly fails: a receptionist/diary parser cannot accept
sixteen safety failures under an exact-zero safety rule.

No runtime default, product adoption, provider/T3.5, route, API, UI, database,
deployment, release, historical-diary, or live/write authority opens.

## Recommended next decision

Authorize a new inspectable development-only LC4V5R1 tranche, without opening
v5, in this order:

1. reproduce and remediate create-approximate safety behavior using newly
   authored ordinary development probes;
2. reproduce move-interval normalization losslessly through the explicit Option
   A path; and
3. reconcile ambiguous-resize clarification choices and tools.

Only after a new ordinary development exit should Yuri decide whether to fund
and authorize a genuinely fresh v6 holdout. V5 is permanently unavailable for
tuning or rerun.
