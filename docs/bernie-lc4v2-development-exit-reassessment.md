# LC4V2 Development Repair Exit Reassessment

## Outcome

LC4V2E1 closes the current development-only repair sequence with
`no_r3_authorized`. LC4V2R1 remains 21/21 and LC4V2R2 remains 28/28, both with
empty failure selections and zero repeat variance. The ordinary development
aggregate remains `880/814/672/154/330/835`, safety remains 1,152/1,152, and
variance remains zero over 2,304 samples.

This is a repair-exit decision, not product certification. No new post-R2
surface-supported parser failure exists in the frozen input set, so naming a
third repair tranche would manufacture work rather than respond to evidence.

## Deterministic audit

`scripts/bernie_lc4v2_exit_gap_reassessment.py` reads only the six exact
development artifacts frozen by Sol's contract. It binds their byte hashes,
exact JSON top-level schemas, R1/R2 canonical report hashes and empty failure
selections, and the accepted LC4R10 ordinary baseline. It does not discover
files or execute the parser.

The canonical report is `docs/bernie-lc4v2-exit-gap-report.json`, report hash
`sha256:aa65f631f748948cdaf0c7adc280a2db1d86b3f2f4779edc1f67ecc3c0412fba`.
Any hash, schema, assertion, count, safety, variance, or corpus drift produces
`reassessment_invalid` and cannot overwrite an accepted report.

## Verification

- exact R1, R2, R10, and LC4V2E1 report checks: pass;
- focused cross-tranche suite: 159/159 pass;
- LC4V2E1 drift/determinism suite: 10/10 pass; and
- Gemini 3.5 Flash/medium independent exact-head veto: `DECISION: pass` on
  `e0d30bd8`.

The final serial preservation gate passed 385/385 selected nodes after
deselecting the one known immutable LC4 development-report equality node. That
historical report was not regenerated.

## Boundary reached

Protected holdouts v1 and v2 remain sealed. T3.1-T3.4 remain intact and blocked
by default; T3.5 and all live/provider/runtime/write surfaces remain deferred.
The next action is a user decision between a genuinely fresh certification
holdout and an explicit reviewed reuse policy. Neither is authorized by this
reassessment.
