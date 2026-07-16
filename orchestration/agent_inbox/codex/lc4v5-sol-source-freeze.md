# LC4V5 Sol Source Freeze

Date: 2026-07-16

Decision: `fresh_v5_source_frozen_unconsumed`

## Immutable source

- source commit: `c2dd34b675bb378b0d4cbab1f41d05b5dd76e407`
- corpus hash: `d5828f9e0ff21cf1a2fb4d482c9556d579eca267e8e2027d09eba8388d52b3e9`
- manifest hash: `650510b52349cefe337aab385e478b26e16a4d87cdb7b13cfb9036d12c9a6d82`
- unconsumed seal hash: `b45958f3be350c63807d06795c25cba948cf5c421f6d8a41411144a2c72c1785`
- attempt ID: `lc4v5-fresh-attempt-001`

The source commit contains the protected authoring source, protected corpus,
content-blind framework, production evaluator adapter, sealer, and one-shot
runner. The later manifest and seal bind that source commit, every scenario and
group hash, all 288 coverage cells, the framework hash, and the evaluator hash.

## Aggregate-only pre-run validation

- 24 groups and 288 scenarios;
- 12 scenarios per group and 288 distinct coverage cells;
- 216 one-shot scenarios and 72 multi-turn trajectories;
- action population `96/48/36/36/36/36` across create, move, resize, cancel,
  status change, and explain schedule;
- temporal population includes exact, not-before, not-after, interval,
  approximate, and unspecified relations;
- 60 clarification cases and 36 prohibited cases;
- all 288 scenarios have source spans; and
- the strict corpus schema, canonical authoring comparison, manifest rebuild,
  file hashes, and unconsumed seal validation passed.

No parser, policy resolver, replay, scorer, or production evaluator was invoked
while authoring or validating this source. The production marker, aggregate
report, and production receipt were absent when the seal was minted.

The first direct sealer launch lacked the repository root on `PYTHONPATH` and
failed at import before reading the corpus or creating any manifest/seal file.
Sol verified both outputs were absent, then launched the same committed sealer
with the repository root supplied; this is not a production-evaluation attempt.

From this checkpoint, the corpus, authoring source, manifest, seal, labels,
filenames, and case evidence are protected. No external model may inspect them,
and the production evaluation may execute exactly once.
