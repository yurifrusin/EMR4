# Bernie LC4V3 Content-Blind Framework

Status: content-blind framework; actual v3 corpus does not yet exist.

## Boundary

The framework validates and evaluates only a future `lc4-holdout-v3` corpus.
It imports no earlier protected-holdout fixture, support module, seal, receipt,
test, or report. DeepSeek supplied an untrusted empty-framework candidate; Sol
rejected its fail-open manifest and seal path and recovered it under the
Ariadne lease. Sol alone owns corpus authorship, sealing, one-shot evaluation,
acceptance, and protected integration.

Protected holdouts v1 and v2 remain sealed and unavailable. No LC4V3 case
content exists during framework implementation.

## Contracts

- Exactly 24 group files named `lc4v3_group_001.json` through
  `lc4v3_group_024.json`.
- Exactly 12 `ReceptionScenarioSpec` variants per group (9 surface + 3
  multi-turn trajectories).
- Exactly 288 variants and 72 trajectories.
- Exactly 2 deterministic repeats, producing 576 aggregate samples.
- Evaluation ID: `lc4-holdout-v3-baseline-001`.
- Evaluator version: `lc4v3.aggregate_evaluator.v1`.
- Corpus identity: `lc4-holdout-v3`.

## Manifest

The manifest binds sorted safe relative filenames, individual file hashes,
schema/version, case counts, and a canonical corpus hash. The corpus hash is
computed from the sorted list of `{filename, file_hash}` entries rather than
from order-free bytes.

`build_manifest(corpus_dir)` scans only the bounded v3 corpus directory. It
validates exact group schemas and identities, every `ReceptionScenarioSpec`,
unique namespaced IDs, Gold/adjudicated provenance, explicit outcome fields,
non-empty lossless spans, explicitly synthetic diary state, trajectory shape,
and the fixed counts before computing the corpus hash.

`reconstruct_manifest(manifest)` verifies every fixed-shape field, recomputes
the corpus hash from the file entries, and raises `ValueError` on any
mismatch.

## Seal

Seal creation first reconstructs and exactly verifies the corpus manifest.
The sealed identity binds:

- Source commit hash
- Manifest hash (over the canonical manifest JSON)
- Corpus hash (from the manifest)
- Evaluator version
- Evaluation ID
- Repeat policy

The CLI rebuilds and exactly compares the live pre-consumption manifest before
creating a seal. `create_seal(manifest)` requires a full 40-hex source commit
and creates a fresh seal with `consumed: false`. `verify_seal` rejects schema
drift, stale source commits, already-consumed state, and any authority hash,
version, evaluation, or repeat mismatch.

## Real aggregate evaluation

`evaluate_aggregate(...)` requires the sealed source, manifest, and corpus
identities, then streams every scenario twice through the
ordinary public `deterministic_interpret`, `deterministic_replay`, and
`score_interpretation_replay_pair` path. It retains per-case observations
only in process and emits no per-case structure.

The report exposes only:

- Passed/failed totals for 14 fixed dimensions
- Failure-layer totals (interpretation, policy, integration, safety)
- Repeat-variance counts (variant_scenario_count, variant_sample_count,
  all_samples_deterministic)
- Predeclared slice totals by action, temporal relation, diary state,
  entity state, dialogue form, language form, and trajectory type
- Coverage cell counts (distinct cells and total possible cells)
- Frozen source commit, manifest hash, and corpus hash
- Report hash (computed over the canonical report JSON)

Production validation requires exactly 576 samples. Every dimension must
total 576. Keys capable of disclosing utterances, IDs, expected labels,
tools, deltas, source spans, normalized values, observations, or case
findings are recursively rejected before the report is emitted. The
`check_forbidden_aggregate_keys` function applies this lint recursively
at every nesting depth.

## One-shot CLI

The script `scripts/bernie_lc4v3_certification.py` exposes:

- `build-manifest <corpus_dir> [--write <output>]`
- `check-manifest <corpus_dir> <manifest>`
- `create-seal <corpus_dir> <manifest> --write <output>`
- `baseline-once <corpus_dir> <manifest> <seal> --write <report> <consumed-seal>`
- `check-aggregate <report>`

Mutating commands (`build-manifest` with `--write`, `create-seal`,
`baseline-once`) require `--write`. `baseline-once` refuses if either
authority-bearing output already exists, writes the report exclusively,
and writes the consumed seal last. A partial failure (report written but
consumed seal not written) is visibly incomplete and cannot be mistaken
for a complete pass.

`check-aggregate` is a post-consumption command only. After the real
baseline is consumed, closeout may use only `check-aggregate`, ordinary
development regressions, and Git/documentation integrity checks; it must
not load or hash the protected corpus again. The `check_aggregate_report`
function validates the exact report schema, safe identities, all dimension
totals, failure layers, variance, coverage cells, slice vocabularies and axis
totals, canonical hash, and recursive forbidden structures without touching
the corpus directory.

## Verification

The tests in `tests/test_bernie_lc4v3_content_blind_framework.py` cover:

- Schema constants (group count, variant counts, evaluation ID, etc.)
- Manifest building from miniature synthetic group files
- Manifest reconstruction and verification
- Wrong count, filename, variant count rejection
- Corpus directory existence validation
- Seal creation and verification (including source commit binding)
- Seal hash/version/evaluation ID mismatch detection
- Duplicate or non-namespaced scenario IDs are rejected
- Missing explicit outcomes are rejected
- Missing or lossy source spans are rejected
- Non-synthetic, non-Gold, or non-adjudicated cases are rejected
- Forbidden aggregate keys (recursive lint at all nesting depths)
- Aggregate evaluation with 576 sample totals
- Zero repeat variance (deterministic evaluation)
- All per-dimension totals summing to 576
- Wrong repeat count rejection
- Wrong scenario count rejection
- Report hash validation and mismatch detection
- Post-consumption check-aggregate validation
- check-aggregate working without corpus files
- Baseline-once refusing existing outputs
- Consumed seal having consumed=true
- CLI write guards (--write required for mutating commands)
- File hash changes propagating to corpus hash
- Coverage cell computation
- Partial failure visibility (report without consumed seal)
- Source/manifest/corpus identity binding, consumed/stale seal rejection,
  path-alias rejection, and exact post-consumption schema validation

No real v3 case exists in the tests. All tests use only hand-authored
miniature synthetic scenarios under pytest temporary directories.

Sol's recovered focused and handover gate passes 56/56. The broader ordinary
composed-evaluator gate passes 188/188 selected nodes after deselecting exactly
the two immutable historical report-regeneration comparisons named in the
recovery evidence. No historical report was regenerated.

## Aggregation dimensions

| Dimension | Key in per_dimension |
|---|---|
| Complete composed contract | `complete_composed_contract` |
| Intended action | `intended_action` |
| Action semantics | `action_semantics` |
| Temporal relation | `temporal_relation` |
| Normalized values | `normalized_values` |
| Entity semantics | `entity_semantics` |
| Clarification | `clarification` |
| Downstream outcome | `downstream_outcome` |
| Interpretation tools | `interpretation_tools` |
| Tool sequence | `replay_tool_sequence` |
| Authority | `authority` |
| Appointment deltas | `appointment_deltas` |
| Audit deltas | `audit_deltas` |
| Safety | `safety` |

## Slice dimensions

The aggregate report exposes predeclared slice breakdowns across:

- `by_action` (create, move, resize, cancel, status_change, explain_schedule)
- `by_temporal_relation` (exact, not_before, not_after, interval,
  approximate, unspecified)
- `by_diary_state` (empty, exact_duplicate, overlap, same_day_distinct,
  terminal, stale, concurrent, roster_absent, break, no_slots,
  elapsed_window)
- `by_entity_state` (exact, omitted, ambiguous, corrected, negated,
  mismatched)
- `by_dialogue_form` (one_shot, clarification, correction, reversal,
  ellipsis, anaphora, repeated, session_restart)
- `by_language_form` (plain, paraphrase, filler, abbreviation, typo,
  speech_like, punctuation_variant, adversarial)
- `by_trajectory_type` (single_turn, trajectory)
- `worst_slice` (the worst-performing slice across all dimensions)

## Failure layers

| Layer | Key |
|---|---|
| Interpretation | `interpretation` |
| Policy | `policy` |
| Integration | `integration` |
| Safety | `safety` |
