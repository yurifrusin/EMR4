# LC4R4 — Patient Entity Evidence Repair — Implementation Note

## Changes

### `app/services/bernie/semantic_extraction.py`

Two narrow, oracle-free edits:

1. **Standalone `someone` → `ambiguous`**  
   Added `"someone"` to `_AMBIGUOUS_PATIENT` regex (line 327).  
   Previously, `someone` passed through to `_PATIENT_PATTERN` without matching
   (lowercase doesn't satisfy `[A-Z][a-z]+`) and fell back to `omitted`.  
   Now it is recognised as an ambiguous patient reference.  
   Does not affect existing `a patient`, `this patient`, etc.

2. **Additive non-correction turn resolves `ambiguous` → `exact`**  
   In `_extract_entity_semantics()`, changed the additive-turn conditions from
   `== "omitted"` to `in ("omitted", "ambiguous")` for patient, practitioner,
   and duration semantics (lines 794, 798, 802).  
   Previously, only `omitted` → `exact` was supported; an initially ambiguous
   reference followed by an explicit name remained `ambiguous`.  
   Correction semantics (`corrected`) are unchanged.

### `tests/test_bernie_semantic_extraction.py`

Added `TestLC4R4PatientEntity` class (22 tests) covering:

- Standalone `someone` is `ambiguous` (4 tests)
- Additive ambiguous → exact (3 tests)
- Pronouns `she`/`he`/`they` not promoted (3 tests)
- Correction semantics preserved (3 tests)
- Substring overmatch protection (2 tests)
- Lossless normalization preserved (2 tests)
- Unsafe/negated/clarification boundaries (3 tests)
- Oracle independence and no-default-synthesis (2 tests)

## Whole-corpus effect

| Metric | Pre-LC4R4 | Post-LC4R4 |
|---|---|---|
| Entity semantics | 255/1152 | **300/1152** |
| Normalized values | 101/1152 | 101/1152 (preserved) |
| Intended action | 880/1152 | 880/1152 |
| Safety | 1152/1152 | 1152/1152 |
| Repeat variance | 0 | 0 |

126 standalone-`someone` scenarios now return `ambiguous` (previously `omitted`).  
13 additive ambiguous→exact scenarios now resolve correctly.  
Net entity-semantics improvement: **45 new passes** (the remainder have
additional entity issues beyond patient).

## Frozen selection discrepancy

The contract states 70 standalone-someone and 13 additive-resolved aligned
records with selection hashes `50260edcf0fa2c0d` and `485cd258fd5ebd60`.
My recomputation finds 126 someone scenarios (all corpus scenarios with
expected `patient_semantics=ambiguous` and `\bsomeone\b` in the first turn)
and the same 13 additive scenarios.  The someone selection hash
(`1d99c3484497bc86`) and additive hash (`8c3ce5ddf6347607`) differ from the
contract's expected values.  This is reported as `revision_required`.

## Normalization

No normalization parser was changed.  Normalized values remain at 101/1152.
The seven normalization failure signatures are reported diagnostically but
exact scenario-level reproduction requires the aligned audit module, which
is outside the bounded implementation surface.
