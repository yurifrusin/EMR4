# LC4 DW2 Bounded Evaluator Revision — Completion

## Commit

| Field | Value |
|---|---|
| Commit | `1f18507` |
| Branch | `codex/lc4-dw2-scaled-evaluator` |
| Base commit | `762f01aa6938ad6c06da77e7d278813dc34afc8d` |

## Changed files

| File | Description |
|---|---|
| `app/services/bernie/scaled_evaluator.py` | Bounded findings (96 cap, dedup, deterministic selection, metadata in report), authority-bearing SHA-256 hash over canonical complete payload + `validate_report_hash()`, replaced all `assert` with `ValueError` + repeats validation, hardened `SealedHoldoutReceipt` (fixed purpose, blank rejection, evaluator/evaluation ID checks, strict recursive allowlist), `compute_sanitized_holdout_hash()`, new exports |
| `tests/test_bernie_lc4_scaled_evaluator.py` | Added 30+ new tests covering findings cap, dedup, deterministic selection, omitted arithmetic, hash authority (6 mutation tests), fail-closed ValueError negatives (2), hardened holdout access (12 including blank/malformed/identity/evaluator checks), stricter sanitizer (7 including alias/tuple/non-numeric/aggregate checks), holdout hash validation (2). Removed `test_findings_count_matches_samples`. Fixed `test_repeat_scores_match` to use variance data. |
| `docs/bernie-lc4-development-evaluation-report.json` | Regenerated: 4,005 lines (down from 85,925), 96 bounded findings, all aggregate scores preserved |

## Report verification

| Metric | Value |
|---|---|
| Report hash | `sha256:d94f9481a6333af25645253a02517b5ac5b9ed7fc1b93901571751f60a1c325e` |
| Report lines | 4,005 (down from 85,925) |
| Total passed (aggregate) | 0 |
| Total failed (aggregate) | 2,304 |
| Adjudicated gaps preserved | True (152,061) |
| LC1 Gold cells | 3 |
| Case findings included | 96 |
| Case findings omitted | 1,056 |
| Case findings limit | 96 |
| Safety failures | 0 |
| Variance | 0 (all deterministic) |

## Retained aggregate counts

All per-dimension scores, simultaneous failure attribution, critical slices across 10 dimensions, candidate-aware lattice, and variance are unchanged from the previous evaluation. The report is materially smaller (4,005 vs 85,925 lines) because case_findings are bounded to 96 deterministic selections with deduplicated repeats.

## Correctness evidence

### 1. Bounded findings (96 max)
- `test_findings_capped_at_limit` — proves ≤96 findings
- `test_findings_limit_constant_is_96` — proves CASE_FINDINGS_LIMIT = 96
- `test_findings_dedup_repeats` — proves no duplicate scenario_id
- `test_findings_deterministic_selection` — proves shuffle-stable selection
- `test_findings_omitted_arithmetic` — proves correct omitted = deduped - selected
- `test_findings_selection_rejects_zero_limit` — proves limit ≤0 raises ValueError

### 2. Authority-bearing hash
- `test_report_hash_authority` — proves validate_report_hash passes
- `test_report_hash_invalidated_by_manifest` — manifest mutation invalidates hash
- `test_report_hash_invalidated_by_per_dimension` — per_dimension mutation invalidates
- `test_report_hash_invalidated_by_slices` — critical_slices mutation invalidates
- `test_report_hash_invalidated_by_variance` — variance mutation invalidates
- `test_report_hash_invalidated_by_findings` — case_findings mutation invalidates
- `test_report_hash_invalidated_by_partition` — partition mutation invalidates
- `test_exact_regeneration_same_hash` — deterministic stability

### 3. Fail-closed ValueErrors
- `test_wrong_repeats_raises` — repeats=3 raises ValueError
- `test_zero_repeats_raises` — repeats=0 raises ValueError

### 4. Hardened sealed-holdout boundary
- `test_blank_manifest_hash_raises`, `test_blank_evaluator_identity_raises`, `test_blank_evaluation_id_raises` — blank fields rejected
- `test_malformed_purpose_raises` — wrong purpose rejected
- `test_wrong_hash_rejected`, `test_wrong_purpose_rejected`, `test_unsealed_rejected` — basic fail-closed
- `test_wrong_evaluator_identity_rejected`, `test_wrong_evaluation_id_rejected` — identity checks
- `test_correct_access_with_identity` — full credential check passes
- `test_consume_with_identity_checks`, `test_wrong_identity_does_not_consume` — ledger identity enforcement
- Stricter sanitizer: `test_rejects_expected_alias`, `test_rejects_observed_alias`, `test_rejects_span_alias`, `test_rejects_finding_alias`, `test_rejects_tuple_with_forbidden_string`, `test_rejects_non_numeric_aggregate_value`, `test_rejects_aggregate_non_dict`
- `test_holdout_hash_validation`, `test_holdout_hash_invalidated_by_mutation`

## Test results

```
$ python -m pytest tests/test_bernie_lc4_scaled_evaluator.py -q --tb=short
........................................................................ [100%]
No failures.
```

```
$ python scripts/bernie_lc4_scaled_evaluation.py --check
Report check passed — in-memory computation matches stored report.
```

## Remaining limitations

- The 24-group holdout is not created, authored, or used. The sealed-holdout interface is tested with generic dummy names only.
- No provider SDK, route, database, UI, T3.5 adapter, or write authority was touched.
- No historical diary, H-series profile, H15 fixture, RAG, GraphRAG, or memory was accessed.
- No promotion or self-certification occurred (all Silver/pending).
- No push to `master`, `handoff/current`, or any integration branch occurred.

## Boundaries preserved

- No provider SDK, adapter, live prompt, or external call
- No route, GraphQL, OpenAPI, database model, migration, or write gate
- No historical-diary/H-series/H15 access
- No modification to DW1 fixtures or existing file boundaries
- No alteration of LC3 report semantics, providers, routes, DB, UI, T3.1-T3.4
- No promotion or self-certification (all Silver/pending)
- No real 24-group holdout data created, named, inspected, or inferred
- No protected master, push, or integration access

## STATUS: complete
