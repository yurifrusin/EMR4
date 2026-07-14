# LC4R4 DW1 — Patient Entity Evidence Repair — Completion

## Scope

Bounded implementation/test worker for LC4R4 patient entity evidence repair
as specified in `orchestration/agent_inbox/codex/lc4r4-normalization-entity-contract.md`.

## Revision

Revision of candidate `c43631a6` to fix six defects identified by Sol's evidence audit.

## Changes

| File | Change |
|---|---|
| `app/services/bernie/semantic_extraction.py` | Add `someone` to ambiguous patient regex; upgrade additive-turn resolution from `omitted`-only to `omitted`/`ambiguous` → `exact` for patient only. Practitioner and duration restored to pre-LC4R4 `omitted → exact` only. |
| `tests/test_bernie_semantic_extraction.py` | Add 24 focused LC4R4 patient entity tests; fix test for practitioner scope creep; add duration scope-boundary test; add omitted-practitioner additive test |
| `scripts/bernie_lc4r4_report.py` | Complete rewrite: use `audit_candidates()` for aligned boundary; use runtime extractor/correction predicates for selection; SHA-256 + newline-joined hash; exact 489-record normalization signature classification via per-field source-span comparison; authoritative `--check` against frozen report; independent LC4R4 report hash |
| `docs/bernie-lc4r4-report.json` | Corrected frozen report with matching hashes, counts, signatures |
| `docs/bernie-lc4r4-implementation-note.md` | Updated with exact evidence and revision details |
| `orchestration/agent_inbox/codex/lc4r4-dw1-completion.md` | This completion artifact |

## Commands and Results

```powershell
# Full semantic extraction tests (128 passed)
pytest tests/test_bernie_semantic_extraction.py -q
# 128 passed in 25s

# LC4R4 evidence report + --check (all assertions pass)
python scripts/bernie_lc4r4_report.py --check
# LC4R4 CHECK PASSED

# git diff --check
git diff --check
# No whitespace errors
```

## Key Metrics

| Dimension | Result |
|---|---|
| Entity semantics | **300/1152** (+45 from 255 baseline) |
| Normalized values | 101/1152 (preserved) |
| Intended action | 880/1152 (preserved) |
| Action semantics | 730/1152 (preserved) |
| Temporal relation | 628/1152 (preserved) |
| Clarification | 698/1152 (preserved) |
| Safety | 1152/1152 |
| Repeat variance | 0 (2304/2304 deterministic) |
| Corpus hash | `sha256:aa2d946b60694eab96846ed77e885273c807e127f8998981a8cf8ff20ebae647` |
| Aligned nv failure records | 489 (matching contract) |

## Frozen Selection Hashes

| Family | Expected | Observed | Match |
|---|---|---|---|
| Standalone `someone` | `50260edcf0fa2c0d` (70 records) | `50260edcf0fa2c0d` (70 records) | ✅ |
| Additive resolved | `485cd258fd5ebd60` (13 records) | `485cd258fd5ebd60` (13 records) | ✅ |

Selection filtered by audit-based aligned boundary; runtime extractor/correction predicates.

## Normalization Failure Signatures (489 total aligned records)

| Signature | Count |
|---|---|
| `unsupported_expected_value_only` | 298 |
| `surface_disagrees_contract_plus_unsupported_expected` | 114 |
| `surface_disagrees_contract_only` | 31 |
| `surface_absent_from_contract_plus_unsupported_expected` | 17 |
| `all_three_conflict_types` | 15 |
| `surface_absent_from_contract_plus_surface_disagreement` | 12 |
| `surface_absent_from_contract_only` | 2 |

All seven signatures match the Sol contract.  Classification uses per-field
`source_spans` comparison over the aligned audit partition (no approximation).

## Defects Fixed

1. **Use established audit**: `audit_candidates([scenario], num_repeats=1,
   max_conflict_examples=0)` per scenario determines aligned boundary.
2. **Freeze two target families**: Selectors use runtime extractor/
   correction predicates, filtered by aligned boundary. Produces 70 and 13.
3. **Contract hash canonicalization**: SHA-256 over
   `"\n".join(sorted(scenario_ids))` truncated to 16 hex chars.
4. **Exact 489-record classification**: Per-field comparison with
   `source_spans` using four category types, aggregated to seven signatures.
5. **Scope creep removed**: Only patient additive semantics resolve
   `ambiguous → exact`. Practitioner and duration restored to `omitted → exact`.
6. **`--check` authoritative**: Compares recomputed report with frozen
   `docs/bernie-lc4r4-report.json`; enforces all counts, hashes, signatures.
7. **Trailing whitespace removed**; implementation note and completion
   artifact updated with exact evidence.

## Boundaries Preserved

- No fixture edits, expected-answer echo, or pronoun promotion
- Correction semantics unchanged
- Lossless normalized turns and `tomorrow at 3pm` intact
- Unsafe, negated, clarification, and tool/authority boundaries unchanged
- No T3 gates, providers, routes, database, UI, memory, or holdout opened
- No generated fixtures, generators, or scenario schemas edited
- No access to protected evidence, generators, providers, routes/API, DB, UI

## Zero-Variance Confirmation

2304/2304 samples deterministic (0 variant scenarios).

## Revision Candidate Commits

Branch: `codex/lc4r4-dw1-entity-evidence`
Base commit: `c43631a6`
Revision commit: (amended or added)
