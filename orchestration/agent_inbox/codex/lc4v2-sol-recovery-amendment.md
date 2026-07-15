# LC4V2 Sol Recovery Amendment

## Recovery decision

DeepSeek V4 Flash/high returned a self-certified pass for the content-blind
framework candidate preserved at commit `fd8324f5`. Sol rejected it as a
conceptual failure and opened no Flash correction loop.

The candidate's `run_aggregate_evaluation` returned hard-coded zero-failure
totals without invoking interpretation, replay, or scoring. It could create a
seal from an unverified manifest, accepted equal dimension totals of any size
rather than the production 576, did not bind safety or critical-slice totals,
and implemented one-shot consumption by mutating an in-memory seal that the CLI
reloaded afresh on every invocation. Its own completion artifact disclosed the
placeholder but nevertheless returned `DECISION: pass`.

## Sol amendments

- replaced the placeholder with streaming calls to the real deterministic
  interpreter, replay, and composed scorer;
- aggregated 14 exact dimensions, four failure layers, repeat fingerprints,
  six canonical slice axes, and coverage counts without serializing per-case
  evidence;
- made manifest construction validate every group and variant immediately;
- bound corpus identity to sorted filename/hash entries and required exact
  manifest reconstruction before seal creation;
- required namespaced IDs, Gold/adjudicated provenance, explicit outcomes,
  non-empty lossless source spans, and explicitly synthetic state;
- constrained manifest paths and digests, full Git SHAs, schema/evaluator
  versions, evaluation identity, and report hashes;
- required production reports to bind 24 groups, 288 variants, 72 multi-turn
  trajectories, two repeats, and exactly 576 samples;
- recursively rejected disclosure-capable report keys and restricted slice
  values to the canonical lattice;
- replaced the mutable in-memory transition with a `baseline-once` CLI that
  refuses existing outputs before evaluation and creates both result artifacts
  exclusively; and
- replaced the worker tests with 33 synthetic-only tests that prove real
  measurement, fail-closed production totals, redaction, hash binding, and
  one-shot output refusal.

## Evidence and boundary

The recovered focused suite passes 33/33 and both implementation files compile.
No actual v2 content exists. Holdout v1 was not opened, enumerated, searched,
imported, run, regenerated, evaluated, hash-checked, inferred from, or tuned
against. No provider, route, database, historical diary source, T3.5 adapter,
or write authority was opened.
