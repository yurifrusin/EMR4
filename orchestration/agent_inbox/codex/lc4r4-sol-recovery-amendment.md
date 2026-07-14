# LC4R4 Sol Recovery Amendment

Date: 2026-07-14

DeepSeek V4 Flash's first candidate correctly returned
`DECISION: revision_required`. Its same-lane revision at worker head
`aefb0ddf95aec20894049416e6fc8bcf040abc26` then passed the frozen 70/13
aligned selections and exact 489-record normalization classification.

Sol adopted both worker commits as untrusted candidates on the protected
LC4R staging branch. Independent diff review found one evidence-only omission:
the report called the aligned 70/13 selections the full-partition effect even
though the runtime rules match 126 standalone-`someone` surfaces and 16
ambiguous-then-explicit additive surfaces in the full Silver/pending
partition. The report also exposed the two-repeat safety sample count where
the contract's acceptance metric is one-repeat scenarios.

Under the documented recovery lease, Sol owns this bounded amendment:

- preserve the aligned acceptance target at 83 records and both frozen hashes;
- separately disclose all 126 and 16 matching development surfaces with their
  own deterministic hashes;
- report safety as 1,152/1,152 scenarios while retaining 2,304 samples for the
  repeat-variance measurement;
- remove one stale unused report-hash constant; and
- add focused report regressions so the aligned/full-partition distinction
  cannot be erased by updating the frozen JSON alone.

No runtime extraction rule, fixture, generator, scorer, audit policy,
protected evidence, provider, T3 gate, route/API, database, UI, deployment,
historical diary, or write authority is changed by this amendment.
