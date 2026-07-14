# LC4R4 — Patient Entity Evidence Repair — Implementation Note

## Changes

### `app/services/bernie/semantic_extraction.py`

Three narrow, oracle-free edits:

1. **Standalone `someone` → `ambiguous`**
   Added `"someone"` to `_AMBIGUOUS_PATIENT` regex (line 327).
   Previously, `someone` passed through to `_PATIENT_PATTERN` without matching
   (lowercase doesn't satisfy `[A-Z][a-z]+`) and fell back to `omitted`.
   Now it is recognised as an ambiguous patient reference.
   Does not affect existing `a patient`, `this patient`, etc.

2. **Additive non-correction turn resolves only patient `ambiguous` → `exact`**
   In `_extract_entity_semantics()`, changed the additive-turn condition for
   patient from `== "omitted"` to `in ("omitted", "ambiguous")` (line 798).
   Practitioner and duration additive semantics remain at pre-LC4R4
   `== "omitted"` only — they do NOT resolve `ambiguous → exact`.
   Previously (LC4R4 initial), all three entity fields gained `ambiguous → exact`
   resolution; this revision restricts that to patient only.
   Correction semantics (`corrected`) are unchanged.

### `tests/test_bernie_semantic_extraction.py`

Added `TestLC4R4PatientEntity` class (24 tests) covering:

- Standalone `someone` is `ambiguous` (4 tests)
- Additive ambiguous → exact for patient only (4 tests)
  - Practitioner ambiguous stays ambiguous (bounded boundary)
  - Duration ambiguous stays ambiguous (bounded boundary)
  - Practitioner omitted → exact still works
- Pronouns `she`/`he`/`they` not promoted (3 tests)
- Correction semantics preserved (3 tests)
- Substring overmatch protection (2 tests)
- Lossless normalization preserved (2 tests)
- Unsafe/negated/clarification boundaries (3 tests)
- Oracle independence and no-default-synthesis (2 tests)

### `scripts/bernie_lc4r4_report.py`

Complete rewrite to fix six defects:

1. Uses `audit_candidates()` for aligned boundary classification instead
   of heuristic string matching.
2. Selection now filters by aligned boundary + uses runtime
   extractor/correction predicates. Hash uses SHA-256 over
   newline-joined sorted scenario IDs truncated to 16 hex characters.
3. Normalization failure signatures computed via per-field comparison
   with `source_spans` using exact category definitions.
4. `--check` compares recomputed report against frozen
   `docs/bernie-lc4r4-report.json` and enforces all hashes, counts,
   signatures, baselines, safety, and variance.
5. LC4R4 report has its own deterministic hash computed with the
   hash field excluded.
6. No approximation note emitted — exact reproduction achieved.

## Whole-corpus effect

| Metric | Pre-LC4R4 | Post-LC4R4 |
|---|---|---|
| Entity semantics | 255/1152 | **300/1152** |
| Normalized values | 101/1152 | 101/1152 (preserved) |
| Intended action | 880/1152 | 880/1152 |
| Safety | 1152/1152 | 1152/1152 |
| Repeat variance | 0 | 0 |

70 aligned standalone-`someone` scenarios now return `ambiguous` (previously `omitted`).
13 aligned additive ambiguous→exact scenarios now resolve correctly.
Net entity-semantics improvement: **45 new passes** (the remainder have
additional entity issues beyond patient).

The runtime rules match a wider Silver/pending surface than the bounded
acceptance target: 126 scenarios contain standalone `someone`, and 16 have an
initial ambiguous patient followed by an explicit name in a non-correction
turn. These are disclosed as development effects, not promoted to aligned or
adjudicated coverage.

## Frozen selection

| Family | Expected | Observed | Match |
|---|---|---|---|
| Standalone `someone` | `50260edcf0fa2c0d` (70 records) | `50260edcf0fa2c0d` (70 records) | ✅ |
| Additive resolved | `485cd258fd5ebd60` (13 records) | `485cd258fd5ebd60` (13 records) | ✅ |

Selection uses the audit-based aligned boundary and runtime predicates.
Hashes use SHA-256 over ``\\n``.join(sorted(scenario_ids)) truncated to 16 hex chars.

## Normalization failure signatures

All seven exact signatures match the Sol contract (total 489 aligned records).
No approximation — signatures derived from per-field `source_spans` comparison
over the aligned audit partition.
