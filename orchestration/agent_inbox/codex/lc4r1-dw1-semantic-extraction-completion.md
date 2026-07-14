# LC4R1 DW1 — Deterministic Semantic Extraction Repair — Completion

**DECISION: pass**

## Changed Files

| File | Change |
|---|---|
| `app/services/bernie/semantic_extraction.py` | **New.** Pure deterministic semantic extraction boundary. Public function `extract_semantics(utterances, reference_date)` returns `SemanticExtraction` with all required semantic dimensions. |
| `app/services/bernie/composed_corpus_evaluator.py` | **Edited.** Imported `extract_semantics`; replaced `deterministic_interpret` body with a thin adapter that extracts utterances/reference-date from scenario, delegates to `extract_semantics`, and projects into `InterpretationObservation`. Removed 400+ lines of old interpretation helpers. Kept `_practitioner_id`, `_PRACTITIONER_ID_MAP`, and `_extract_practitioner_name` for replay use. |
| `tests/test_bernie_semantic_extraction.py` | **New.** 56 focused tests covering all contracted behaviours. |
| `docs/bernie-lc4r1-semantic-extraction.md` | **New.** Implementation note documenting the extraction boundary. |
| `orchestration/agent_inbox/codex/lc4r1-dw1-semantic-extraction-completion.md` | **New.** This record. |

## Tests and Results

| Test Command | Result |
|---|---|
| `python -m pytest tests/test_bernie_semantic_extraction.py -q` | **56 passed** |
| `python -m pytest tests/test_bernie_composed_corpus_evaluator.py -q -k "not test_regenerated_matches_committed"` | **39 passed**, 1 skipped (committed-report mismatch expected) |
| `python -m pytest tests/test_bernie_lc4_scaled_evaluator.py -q -k "not test_exact_report_regeneration"` | **96 passed**, 1 skipped (report-regeneration expected) |
| `python -m pytest tests/test_bernie_temporal_policy.py -q` | **34 passed** |
| `python scripts/bernie_shadow_live_gate_check.py` | Decision: **blocked** (no change) |
| `git diff --check` | Clean |

## Verification Against Acceptance Gate

| Criterion | Status |
|---|---|
| Every newly authored semantic regression passing | 56/56 passed |
| 1,152/1,152 development safety passes | 0 safety failures in corpus evaluation |
| Zero repeat variance | 0 variant scenarios |
| `read|clarify|refuse` authority only, never `write` | 36/36 authority passed, 0 safety violations |
| No expected-answer echo | `extract_semantics` accepts only utterances + reference_date |
| Contradictory Silver labels remain visible | ambiguity_001/002 correctly return `unspecified` for "sometime in the afternoon" vs Silver label `interval` |
| Real "tomorrow at 3pm" LC1 regression green | booking_create_then_exact_duplicate: exact, read, create |
| No holdout, provider, route, DB, UI, write-authority, or T3.5 change | Confirmed -- no touched file crosses these boundaries |

## Known Limitations

1. **Committed LC3 report artifact outdated.** The report at
   `docs/bernie-lc3-composed-evaluation-report.json` will differ because the
   new extraction produces different (correct) values for temporal relation
   on correction scenarios. Sol will regenerate on acceptance.

2. **Contradictory Silver labels.** Two ambiguity scenarios label "sometime in
   the afternoon" as `temporal_relation=interval`, but the semantically correct
   extraction (matching old-code behaviour) returns `unspecified`.

3. **Pre-existing tool mismatches.** The overlap scenario and clarify scenario
   have expected tool sequences that neither the old nor new code produces
   (`propose_candidates` and `find_slots` in clarify mode respectively).
   These are unchanged baseline findings.

## Prohibited Boundaries

- No holdout file (`lc4_holdout*`, `lc4-holdout*`, `holdout_support*`,
  `holdout-v1*`, `sealed_holdout*`) was opened, read, or inferred from.
- No provider, route, database, UI, T3.5, or write-authority code was edited.
- No external network, PHI, historical diary material, or memory/RAG was
  accessed.
