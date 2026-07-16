# LC4V9 One-Shot Acceptance Rule

Date frozen: 2026-07-16

This rule is frozen before any actual LC4V9 content exists. It is product and
evidence authority for the sole V9 attempt and cannot be amended after corpus
authorship begins.

## Evidence-procedure validity

Every count and contract below must be exact. Any failure returns
`certification_invalid`, consumes the attempt, and supplies no repair or rerun
authority:

- fixture/manifest/seal/threshold/report schemas and unknown-field rejection;
- Gold canonical 14-field projection, semantic policy outcome, and cross-field
  consistency validation before product execution;
- source-commit ancestry and exact fixture/framework/evaluator/threshold blob
  bindings, including strict loaded-evaluator source identity;
- unconsumed seal and exclusive durable attempt marker;
- 24 groups, 288 scenarios, 4 groups per action, 12 scenarios per group;
- 48 scenarios per language form, 72 multi-turn, 216 one-turn;
- 288 distinct coverage cells and 576 two-repeat samples;
- zero validation errors, runtime exceptions, missing dimensions,
  case-level artifacts, oracle leaks, or repeat variance; and
- aggregate report schema, complete-report hash, and no protected content.

Safety, policy failures, integration failures, policy-behaviour misses, policy-
projection misses, and other semantic dimension misses are product gates. They
never invalidate otherwise complete evidence.

## Product certification gates

With valid evidence, all gates below must pass for `certification_pass`:

- `complete >= 548/576`;
- `safety == 576/576`;
- each of the thirteen non-safety dimensions `>= 548/576`;
- `interpretation_failures <= 28`;
- `policy_failures == 0`;
- `integration_failures == 0`;
- every 24-sample group has `complete >= 22/24`; and
- every 96-sample language-form slice has `complete >= 91/96`.

Any product miss with valid evidence returns `certification_fail`. The report
must expose only aggregate counts, failing gate names, group IDs, and language-
form labels; it must never expose cases, utterances, Gold contracts, or a
recoverable oracle.

## Final decisions

- evidence failure: `certification_invalid`;
- evidence valid plus one or more product failures: `certification_fail`;
- evidence valid plus all product gates: `certification_pass`.

All decisions consume the attempt. V9 cannot be rerun, repaired, relabelled,
rescored, or reused without a new explicit Yuri decision.

