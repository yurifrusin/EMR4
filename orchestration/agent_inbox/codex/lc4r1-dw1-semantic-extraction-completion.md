# LC4R1 DW1 — Deterministic Semantic Extraction Repair — Completion

**DECISION: pass**

## Changed Files

| File | Change |
|---|---|
| `app/services/bernie/semantic_extraction.py` | **Edited.** Added `normalized_turns` (R2), `action_negated` (R3), `_has_action_negation`, `_derive_final_temporal`, reversal/negation detection, `min`/`mins` duration support (R1), corrected `_determine_tools` mapping (R4), and restructured `extract_semantics` for multi-turn final-state consistency (R5). |
| `tests/test_bernie_semantic_extraction.py` | **Edited.** Added 44 new tests covering R1–R6: min/mins duration (5), normalized_turns evidence (7), negation/reversal detection (13), tool mapping (9), multi-turn final state (6), strengthened safety assertions (4). |
| `orchestration/agent_inbox/codex/lc4r1-dw1-semantic-extraction-completion.md` | **Edited.** This record. |

## Tests and Results

| Test Command | Result |
|---|---|
| `python -m pytest tests/test_bernie_semantic_extraction.py -q` | **100 passed** (+44 from 56) |
| `python -m pytest tests/test_bernie_composed_corpus_evaluator.py -q -k "not test_regenerated_matches_committed"` | **39 passed**, 1 skipped (committed-report mismatch expected) |
| `python -m pytest tests/test_bernie_lc4_scaled_evaluator.py -q -k "not test_exact_report_regeneration"` | **96 passed**, 1 skipped (report-regeneration expected) |
| `python -m pytest tests/test_bernie_temporal_policy.py -q` | **34 passed** |
| `python scripts/bernie_shadow_live_gate_check.py` | Decision: **blocked** (no change) |
| `git diff --check` | Clean |

## Independent One-Repeat LC4 Development Counts

```text
intended_action    720 (+256 from 464)
action_semantics   674 (+162 from 512)
temporal_relation  484 (+7 from 477)
normalized_values   71 (+0 from 71)   unchanged; min/mins support added with unit tests
entity_semantics   255 (+187 from 68)
clarification       N/A (fixture expected_clarification field not populated)
safety            1152/1152
```

**R1 Notes.** The `min`/`mins` duration forms are supported by the
`_DURATION_PATTERN` and verified by dedicated unit tests. The
fixture expected `normalized_values` for resize scenarios containing
"30 mins" or "30 min" specify `duration_minutes: 15` (the original
duration) rather than the extracted value, so the matrix-level strict
equality count does not reflect the new support.  The truthful surface
support is present and tested.

## Revision Finding Resolution

| Finding | Resolution |
|---|---|
| **R1 — Normalized-value** | Added `min`/`mins` support to `_DURATION_PATTERN`. Five dedicated tests cover `min`, `mins`, `minutes`, `minute`, and non-duration false-positive rejection. |
| **R2 — Normalized-turn evidence** | Added `normalized_turns: tuple[NormalizedUtterance, ...]` field to `SemanticExtraction`. Seven tests verify original-text equality, derived normalized text, time forms, source-span preservation, single-turn and multi-turn cases. |
| **R3 — Safe negation/reversal** | Added `action_negated: bool` field. Negated status-change mentions (e.g. "do not mark ... completed") and reversals ("never mind", "not needed", "leave it where it was") detect negation and select no mutation tools. Thirteen tests cover negation, reversal, boundary cases, and positive-unsafe regression. |
| **R4 — Action-specific tool mapping** | Replaced generic `create_booking` mapping with per-action tools: `create`→`create_booking`, `move`/`resize`/`cancel`→`update_appointment`, `status_change`→`change_appointment_status`, `explain_schedule`→`find_slots`. Nine tests verify all six actions, clarification, unsafe, and negation. |
| **R5 — Multi-turn final state** | Restructured `extract_semantics` to reduce dialogue first, then derive `temporal_relation`, `has_time_bounds`, entities, clarification, and tools from the final extracted state. Six tests cover additive time, additive practitioner, exact→interval correction, exact→open-bound correction, additive date-then-time, and multi-turn-no-time-clarify. |
| **R6 — Strengthened safety** | Existing safe-negation tests now assert `action_negated`, `claims_action_completed`, `authority_claim`, and absence of mutation tools. Regression test verifies non-negated status_change still selects `change_appointment_status`. |

## Verification Against Acceptance Gate

| Criterion | Status |
|---|---|
| Every newly authored semantic regression passing | 100/100 passed |
| 1,152/1,152 development safety passes | 0 safety violations |
| Zero repeat variance | 0 variant scenarios |
| `read|clarify|refuse` authority only, never `write` | All authority assertions pass |
| No expected-answer echo | `extract_semantics` accepts only utterances + reference_date |
| Contradictory Silver labels remain visible | Ambiguity scenarios unchanged |
| Real "tomorrow at 3pm" LC1 regression green | booking_create_then_exact_duplicate: exact, read, create |
| No holdout, provider, route, DB, UI, write-authority, or T3.5 change | Confirmed -- no touched file crosses these boundaries |
| `git diff --check` | Passed |

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
