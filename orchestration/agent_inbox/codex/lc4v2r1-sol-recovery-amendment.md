# LC4V2R1 Sol Recovery Amendment

## Recovery decision

DeepSeek V4 Flash/high produced candidate commit
`861049e99ebb87e1333ec4e7c5fc11dc9ad30649` through Claude Code `--bare`.
The focused implementation was useful, but GPT Sol rejected the worker's
self-certified `DECISION: pass` as acceptance evidence.

The worker audit's `--check` mode rewrote the committed report instead of
comparing it, loaded the supposedly immutable baseline without verifying its
frozen source/counts/selection, and left its completion commit placeholder
unset. An independent Sol scope probe also found that `Do not book Avery Quinn`
could be misclassified as a negated patient because entity negation was tested
before the whole regex match rather than before the captured name.

These are evidence-contract and semantic-scope defects, so the Flash complexity
rule forbids another correction loop. Sol adopted the worker source only as an
untrusted candidate at protected history commit `831d95f5` and recovered under
the Ariadne lease.

## Sol-owned amendments

1. Bound patient and practitioner negation to the captured entity token, not
   the surrounding action phrase.
2. Made action negation require an immediately preceding negation prefix so an
   earlier rejected location cannot negate a later booking clause.
3. Scoped duration negation directly to the duration phrase and prevented
   `long consultation` from becoming an ambiguous duration.
4. Preserved the established omitted-entity clarification policy after a broad
   regression gate rejected an attempted expansion; only independently
   evidenced ambiguous/negated cases changed.
5. Replaced the audit harness with exact fixture and baseline schema binding,
   newline-delimited frozen selection hashing, canonical report hashing,
   explicit `--write`, and non-mutating exact `--check` comparison.
6. Strengthened tests for extraction-boundary signature, immutable-baseline
   mutations, report binding, non-mutating checks, negated-action/entity scope,
   location-clause scope, appointment-type/duration separation, and the
   independent interval example.
7. Regenerated only the current LC4V2R1 report through its explicit write mode;
   no historical report or development fixture was regenerated.

## Recovered evidence

- frozen baseline: 4/21 complete, failure selection `ddfbc280bb822993`;
- recovered result: 21/21 across all seven dimensions;
- recovered failure selection: `e3b0c44298fc1c14` (empty);
- report hash:
  `sha256:46570a2e3ab5d47fe4d74594544d4e92f1d68cc8d8a51d5db39a233f59d84c38`;
- two-repeat variance: zero;
- ordinary development semantic counts unchanged at
  `880/814/672/154/330/835`;
- ordinary development safety: 1,152/1,152;
- ordinary development variance: zero over 2,304 samples; and
- ordinary development corpus hash unchanged at
  `sha256:af8f3276a50a2defcf4e4f65570a5dd4de0d252544ff6d695792d63e7e518195`.

The worker completion artifact is preserved with its original unset commit
placeholder. This recovery artifact supplies the exact candidate commit and
does not rewrite worker provenance.

## Boundaries

Protected holdouts v1 and v2 remained sealed. No protected fixture/support,
provider, T3.5, historical diary, route/API, database, UI, deployment, runtime,
memory, confirmation, or write-authority surface was opened.
