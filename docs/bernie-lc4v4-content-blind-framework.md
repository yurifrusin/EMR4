# Bernie LC4V4 Content-Blind Framework

LC4V4 begins with an authoring-quality gate and empty certification framework.
Neither component contains real v4 scenarios. Holdouts v1-v3 remain sealed.

## Independent authoring quality

Every authored turn has six independent values: turn index, prefix, canonical
core, rendered core, suffix, and final rendered text. Validation requires the
rendered core to equal the canonical core byte-for-byte and the final text to
equal `prefix + rendered_core + suffix`. This detects whole-string case
transforms and punctuation or wrapper code that rewrites semantic content.

Authority-bearing tokens carry exact turn coordinates, canonical text,
case-sensitivity, and lossless source text. The validator checks the addressed
turn, valid non-overlapping coordinates, containment inside the preserved
core, exact/case-aware value, source-text equality, duplicate tokens, and
field-specific evidence counts. Entity relations use relation-specific rules:
exact requires one case-preserved token; corrected requires at least two
different case-preserved tokens; omitted requires none; ambiguous, negated,
and mismatched require explicit surface evidence.

Expected tools, authority, outcome, appointment deltas, and audit deltas are
derived from canonical facts through a local frozen policy table. No expected
tool sequence or outcome is accepted as canonical input. A separate comparison
checks every expected contract field against a fresh derivation.

The lattice gate checks 288 unique scenario IDs, every canonical category,
both trajectory types, and at least 240 distinct six-dimensional cells. Its
receipt removes all finding details and contains only aggregate category
totals. Every required category must be present and completely passing. The
receipt is deterministic UTF-8/LF JSON with its own SHA-256 hash.

## Manifest and one-shot binding

The v4 manifest binds:

- exact 24-group, 288-scenario, 72-trajectory corpus bytes;
- category-complete corpus metadata and at least 240 distinct cells;
- the exact passing authoring-quality receipt hash;
- evaluator identity, repeat policy, and aggregate population.

The seal then binds the manifest hash, corpus hash, current full Git commit,
evaluator identity, evaluation identity, and unconsumed state. The only
baseline entrypoint reconstructs the manifest, revalidates the quality receipt
and corpus, verifies the live source commit and unconsumed seal, evaluates two
repeats, creates the aggregate report exclusively, and creates the consumed
seal exclusively last. Output paths must be distinct and outside the corpus.
Existing paths are never replaced.

After consumption, `check-aggregate` accepts only the aggregate report. It has
no corpus, quality-receipt, manifest, or seal argument and recursively rejects
case-level keys and values.

## CLI

```text
build-manifest <corpus> <quality-receipt> --write <manifest>
check-manifest <corpus> <quality-receipt> <manifest>
create-seal <corpus> <quality-receipt> <manifest> --write <seal>
baseline-once <corpus> <quality-receipt> <manifest> <seal> --write <report> <consumed-seal>
check-aggregate <report>
```

All paths are operator supplied. The framework opens no provider, T3, route,
database, UI, runtime, historical-diary, deployment, release, confirmation, or
write-authority surface.
