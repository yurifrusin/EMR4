# LC4 DW2 — Scaled Evaluator and Sealed Aggregate Interface Completion

## Changed files

| File | Description |
|---|---|
| `app/services/bernie/scaled_evaluator.py` | Provider-free generic LC4 scaled evaluator — reuses LC3 deterministic interpret/replay/scorer APIs; loads 96-group development corpus; evaluates 1,152 variants × 2 repeats = 2,304 samples; produces per-dimension scores, simultaneous failure attribution, critical slices across 10 dimensions, bounded case findings, candidate-aware lattice, variance, and report hashes. Includes strict generic sealed-holdout interface (SealedHoldoutReceipt, SingleUseLedger, sanitize_holdout_report) testable only with miniature dummy records. |
| `scripts/bernie_lc4_scaled_evaluation.py` | CLI script: writes `docs/bernie-lc4-development-evaluation-report.json` (default) or `--check` verifies in-memory without writing. |
| `tests/test_bernie_lc4_scaled_evaluator.py` | 55 focused tests across 12 test classes covering exact report regeneration, two-repeat variance, shuffle stability, simultaneous layers, every slice dimension, bounded findings, candidate/adjudicated lattice, mutation detection, holdout access/rejection/single-use, import isolation, and honest-failure visibility. |
| `docs/bernie-lc4-development-evaluation-report.json` | Committed deterministic development evaluation report (generated). |

## Exact counts

| Metric | Value |
|---|---|
| Development groups | 96 |
| Surface variants | 864 |
| Multi-turn trajectories | 288 |
| **Total individual records** | **1,152** |
| **Repeats** | **2** |
| **Total samples** | **2,304** |
| Provenance | silver |
| Adjudication | pending |
| Corpus hash | `sha256:aa2d946b60694eab96846ed77e885273c807e127f8998981a8cf8ff20ebae647` |
| Report hash | `sha256:fb7d844687358d5f3a35eff8c2f136180ee22b97be88dde0e7828492a9996a7c` |

## Development evaluation results

| Dimension | Passed | Failed | Total |
|---|---|---|---|
| **Aggregate (all_passed)** | 0 | 2,304 | 2,304 |
| intended_action | 928 | 1,376 | 2,304 |
| action_semantics | 1,024 | 1,280 | 2,304 |
| temporal_relation | 954 | 1,350 | 2,304 |
| normalized_values | 142 | 2,162 | 2,304 |
| entity_semantics | 136 | 2,168 | 2,304 |
| downstream_outcome | 108 | 2,196 | 2,304 |
| interpretation_tools | 486 | 1,818 | 2,304 |
| authority | 1,088 | 1,216 | 2,304 |
| appointment_deltas | 432 | 1,872 | 2,304 |
| audit_deltas | 384 | 1,920 | 2,304 |
| **safety** | **2,304** | **0** | **2,304** |

## Failure attribution

| Layer | Count |
|---|---|
| Interpretation failures | 2,282 |
| Policy failures | 2,196 |
| Integration failures | 2,244 |
| Safety failures | 0 |
| Multiple simultaneous layers | 2,294 |

## Lattice

| Metric | Value |
|---|---|
| Adjudicated (LC1 Gold) cells | 3 |
| Adjudicated empty cells | 152,061 |
| Expected gaps preserved | True |
| Candidate-only cells (LC4) | 444 |
| Pending candidates do not reduce adj. gaps | True |

## Known honest failures

All 2,304 samples fail `all_passed` because the LC3 deterministic interpreter,
designed for the 18 LC1/LC2 scenarios, does not handle the broader linguistic
variety of 1,152 LC4 development variants across 6 actions, 6 temporal relations,
11 diary states, 8 dialogue forms, and 8 language forms.  Per-dimension scores
show partial coverage (e.g., 928/2304 correct intended_action, 954/2304 correct
temporal_relation).  Safety score is perfect (0 failures) — no sample claims
write authority or action completion.

This is honest visible evidence of interpreter gaps targeted by the corpus, not
an expected-answer echo.

## Slice coverage

All 10 required slice dimensions present: action, temporal_relation, diary_state,
entity_state, dialogue_form, language_form, tier, adjudication, trajectory_type,
gap_target.  Worst slice: `language_form` / `abbreviation` (0.0 pass fraction).

## Sealed-holdout interface

- `SealedHoldoutReceipt` — requires manifest_hash, exact purpose
  `sealed_baseline_evaluation`, evaluator identity, evaluation ID, sealed flag.
  Wrong/reused credentials fail closed.
- `SingleUseLedger` — single-use in-memory capability; second consume() returns
  False.
- `sanitize_holdout_report()` — rejects any key/value containing scenario_id,
  group_id, utterances, expected outcomes, source spans, etc.  Emits only
  aggregate/slice counts, hashes, version.

## Tests

55 tests across 12 classes:

| Class | Count | Coverage |
|---|---|---|
| `TestExactReport` | 4 | Committed report regeneration, stable hashes, corpus hash match, schema version |
| `TestExactCounts` | 4 | 1152 variants, 2304 samples, 288 trajectories, silver/pending, 96 groups |
| `TestTwoRepeatVariance` | 2 | Zero variant count, repeat 0/1 match |
| `TestShuffleStability` | 2 | Stable report hash and per-dimension values |
| `TestSimultaneousLayers` | 4 | Layer sum ≤ total, simultaneous counts present, zero safety, accurate attribution |
| `TestSliceDimensions` | 5 | All 10 dimensions present, action/temporal coverage, totals sum, worst slice |
| `TestBoundedFindings` | 3 | Count matches samples, compact schema, failure info |
| `TestCandidateAdjudicatedLattice` | 5 | 3 Gold cells, 152,061 adj. gaps preserved, separate discovery, no gap reduction, builder test |
| `TestMutationDetection` | 5 | Temporal, entity, authority write, claims_completed, forbidden outcome |
| `TestHoldoutAccess` | 4 | Wrong hash/purpose/unsealed reject, correct access granted |
| `TestSingleUseLedger` | 3 | First use succeeds, reuse fails, wrong credentials don't consume |
| `TestHoldoutReportSanitizer` | 7 | Rejects scenario_id/utterance/outcome/group keys/values, accepts aggregate-only |
| `TestImportIsolation` | 2 | Isolation pass, no prohibited imports in AST |
| `TestStaticImportGuard` | 2 | No product module imports holdout capabilities, fixture path works |
| `TestHonestFailures` | 2 | Failures visible, no expected-answer echo |

## Boundaries preserved

- No provider SDK, adapter, live prompt, or external call
- No route, GraphQL, OpenAPI, database model, migration, or write gate
- No historical-diary/H-series/H15 access
- No modification to DW1 fixtures or existing files
- No alteration of LC3 report semantics, providers, routes, DB, UI, T3.1-T3.4
- No promotion or self-certification (all Silver/pending)
- No real 24-group holdout data created, named, inspected, or inferred
- No protected master, push, or integration access

## Candidate commit

`candidate_commit: resolved_by_receipt`
