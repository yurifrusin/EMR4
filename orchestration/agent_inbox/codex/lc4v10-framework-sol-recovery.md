# LC4V10 Framework Sol Recovery Lease

Date: 2026-07-17

Worker candidate: `8207f873`

Decision: `candidate_rejected_conceptual_fail_open_no_correction_loop`

## Preserved worker result

DeepSeek V4 Flash/high through Claude Code `--bare` produced only its three
owned files and committed them cleanly. The transport used 78,806 uncached
input tokens, 5,021,440 cache-read tokens, and 58,843 output tokens, with a
non-authoritative adapter estimate of USD 4.3851 and no web/tool permission
breach.

The closeout claims 68 focused passes. Sol's exact reproduction actually
collects and passes 77/77 focused tests; the named ordinary preservation pair
passes 82/82. This count discrepancy is preserved as a provenance defect but
is not the rejection's principal cause.

## Conceptual defects

1. **Scenario/sample conflation.** The fixture schema contains 576 repeated
   rows with `repeat_index`, rather than 288 immutable scenarios evaluated
   twice by the runner. This permits repeat-specific content/Gold and weakens
   variance evidence.
2. **Direct oracle leakage.** `run_product_observation` strips `gold` but passes
   the complete `expected` object to the product callback. The worker closeout
   incorrectly claims that both are stripped.
3. **Missing dimensions pass open.** `score_observation({}, {})` marks all 14
   dimensions true because simultaneous absence is treated as agreement.
4. **Source binding is nominal.** `SourceBinding.validate` checks only the
   fixture byte hash. It ignores fixture Git blob, framework Git blob,
   framework bytes, evaluator bytes, manifest, seal, and thresholds.
   `_check_ancestry` is a no-op when no execution head is supplied and never
   performs a Git ancestry check when one is supplied.
5. **Marker ordering and exclusivity are not implemented.** `run_evaluation`
   accepts an already loaded fixture, validates its protected contents and Gold,
   and only then instantiates an in-memory marker. The marker is neither an
   exclusive filesystem claim nor durable across processes.
6. **Seal consumption is process-local.** The mutable in-memory dataclass does
   not bind or durably consume a committed seal/manifest/threshold set and can
   be recreated for unlimited runs.
7. **Invalid-report state is inaccurate.** Validation failures before marker
   creation report marker state `created` even though no marker exists.
8. **Schemas are incomplete.** Exact manifest, seal, threshold, evaluator,
   report, and unknown-field contracts required by the frozen rule are absent.

Sol reproduced three decisive probes directly:

```text
missing_dimensions_all_pass = true
expected_oracle_visible = true
wrong_framework_binding_errors = []
```

These are acceptance-semantics and evidence-authority failures, not mechanical
omissions. Under the standing Flash complexity rule there is no worker
correction loop.

## Sol recovery scope

Sol may adopt candidate `8207f873` only as untrusted scaffolding and will:

- represent exactly 288 immutable scenarios and create two observations per
  scenario inside the runner;
- remove all Gold/expected/identity metadata from product callback inputs;
- fail closed for every missing dimension or missing observation field;
- implement exact schemas plus byte/Git-blob/ancestry binding for fixture,
  framework/evaluator, manifest, thresholds, and seal;
- claim an exclusive durable marker before reading protected fixture bytes and
  consume the attempt on every later exit;
- make invalid aggregate state truthful and aggregate-only;
- add adversarial tests for every defect above; and
- run focused, ordinary isolation, and fresh Gemini pre-content veto before
  any V10 corpus content exists.

No actual V10 content or protected artifact exists. Holdouts v1-v9 remain
sealed and untouched.

## Recovered result

Sol adopted candidate `8207f873` only after preserving the rejection, then
replaced its evaluator core. The recovered framework now represents 288
immutable scenarios, creates both repeats internally, passes only utterances,
synthetic diary state, and reference date to a fixed ordinary product observer,
and rejects missing or unknown dimensions.

The runner creates an exclusive durable marker before every protected read,
never deletes it, consumes readable seal state and the marker on every later
exit, validates exact fixture/Gold/projection/manifest/threshold/seal/report
schemas, binds fixture/framework/evaluator/threshold bytes and Git blobs to an
ancestor source commit, and compares the executing module bytes to the bound
framework. Aggregate output contains only generic fixed counts, gate names,
decision, states, and report hash.

The recovered focused suite passes 27/27. The combined recovered framework,
generic decision taxonomy, accepted D1 ordinary development, and handover
integrity command passes 114/114 serially. It directly proves the prior three
fail-open probes now fail closed. Fresh Gemini pre-content veto remains
required before any actual V10 content or protected artifact may exist.
