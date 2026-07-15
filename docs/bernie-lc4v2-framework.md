# LC4V2 Content-Blind Framework

Status: Sol-recovered framework; actual v2 content does not yet exist.

## Boundary

The framework validates and evaluates only a future `lc4-holdout-v2` corpus.
It imports no earlier protected-holdout fixture, support module, seal, receipt,
test, or report. DeepSeek implemented an initial candidate without content;
Sol rejected its conceptual evaluation and consumption defects and recovered
the source directly. Gemini reviews this recovered framework before any actual
v2 scenario exists.

## Contracts

- Exactly 24 group envelopes, each named `lc4v2_group_NNN`, with exactly 12
  `ReceptionScenarioSpec` variants and exactly three real multi-turn
  trajectories.
- Exactly 288 Gold/adjudicated variants and 72 multi-turn trajectories.
- Every variant has a namespaced unique ID, explicit outcome field, non-empty
  lossless source-span evidence, and explicitly synthetic initial diary state.
- The manifest binds sorted safe relative filenames and individual file hashes;
  its corpus hash binds the filename/hash list rather than order-free bytes.
- Seal creation first reconstructs and exactly verifies the corpus manifest.
- The sealed identity binds the full source commit, evaluator version, manifest
  hash, corpus hash, two-repeat policy, and fixed baseline evaluation ID.

## Real aggregate evaluation

`evaluate_aggregate` streams every scenario twice through the ordinary public
`deterministic_interpret`, `deterministic_replay`, and
`score_interpretation_replay_pair` path. It retains per-case observations only
in process and emits no per-case structure.

The report exposes only:

- passed/failed totals for 14 fixed semantic, outcome, tool, delta, authority,
  safety, and complete dimensions;
- aggregate interpretation/policy/integration/safety attribution totals;
- repeat-variance counts;
- predefined action, temporal, diary-state, entity-state, dialogue-form, and
  language-form slice totals;
- total distinct coverage-cell and scenario counts; and
- corpus, manifest, source-commit, evaluator, and report hashes.

Production validation requires exactly 576 samples. Every dimension and every
slice axis must total 576. Keys capable of disclosing utterances, IDs, expected
labels, tools, deltas, source spans, normalized values, observations, or case
findings are recursively rejected before schema validation. Slice values are
restricted to the canonical lattice vocabulary.

## One-shot CLI

The CLI exposes explicit `build-manifest`, `create-seal`, `baseline-once`,
`check-manifest`, and `check-aggregate` commands. Mutating commands require
`--write`. `baseline-once` refuses to evaluate if either authority-bearing
output already exists, writes the report exclusively, and writes the consumed
seal last. A partial failure is visibly incomplete and cannot be mistaken for
a pass.

`check-manifest` is a pre-consumption authoring command only. After the real
baseline is consumed, closeout may use only `check-aggregate`, ordinary
development regressions, and Git/documentation integrity checks; it must not
load or hash the protected corpus again.

## Verification

The 33 synthetic-only tests cover schema, provenance, explicit outcomes,
source-span evidence, synthetic-state marking, manifest path/hash/count drift,
cross-group identity, real composed evaluation, repeat variance, fixed
production totals, forbidden aggregate fields, report hash drift, seal
binding, `--write`, and exclusive one-shot outputs. No real v2 case exists in
the tests.
