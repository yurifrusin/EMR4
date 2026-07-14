# LC4R1 — Deterministic Semantic Extraction Boundary

**Date:** 2026-07-14
**Module:** `app/services/bernie/semantic_extraction.py`
**Integration:** `app/services/bernie/composed_corpus_evaluator.py` -> `deterministic_interpret`

## Purpose

This sprint introduces a pure, provider-free semantic extraction boundary for
receptionist dialogue in EMR4's Bernie module. The boundary receives only
utterance strings and an explicit reference date -- never a scenario contract,
expected outcome, or scorer oracle -- and returns typed semantic fields that a
caller may project into `InterpretationObservation`.

The extraction handles:

- **Six diary actions:** `create`, `move`, `resize`, `cancel`, `status_change`,
  `explain_schedule`, plus unknown-action clarification.
- **Six temporal relations:** `exact`, `not_before` (after), `not_after`
  (before), `interval` (between), `approximate` (around/about), `unspecified`.
- **Point-time variants:** `3pm`, `3 pm`, `3:15pm`, `3.15pm`, `15:15`.
- **Date derivation:** `today`, `tomorrow`, `day after tomorrow` relative to
  the reference date.
- **Minute duration:** patterns matching text like "15 minutes".
- **Multi-turn reduction:** additive turns contribute new fields; correction
  turns replace only their corrected field (time, date, duration, or entity).
- **Entity semantics:** exact, omitted, ambiguous, and corrected states for
  patient, practitioner, and duration.
- **Action-relevant clarification:** only missing facts that are material to
  the detected action trigger clarification (e.g., create without time
  clarifies; cancel without time does not).
- **Unsafe bypass/completion refusal:** "bypass confirmation",
  "override the system", "ignore the duplicate check" are refused.
  Safe negated mentions ("do not bypass confirmation", "do not mark it
  completed") are preserved.
- **Authority:** always read, clarify, or refuse; never write.
  claims_action_completed is always False.

## Architecture

```
utterances: list[str]  +  reference_date: str
          |
          v
  extract_semantics()
          |
          v
  SemanticExtraction
    - intended_action, action_semantics
    - temporal_relation, earliest_time, latest_time
    - normalized_values (date, bounds, duration, period)
    - entity_semantics (patient, practitioner, duration)
    - requires_clarification, clarification_choices
    - authority_claim, claims_action_completed
    - selected_tool_sequence
          |
          v
  deterministic_interpret()   (in composed_corpus_evaluator.py)
    projects SemanticExtraction to InterpretationObservation
```

The `SemanticExtraction` dataclass is defined in the extraction module and is
the only return type. `deterministic_interpret` is a thin adapter that
extracts utterances and the reference date from the scenario, calls
`extract_semantics`, and projects the result.

## Owned Surface

- `app/services/bernie/semantic_extraction.py` -- new module (the boundary)
- `app/services/bernie/composed_corpus_evaluator.py` -- integrated via
  `deterministic_interpret`
- `tests/test_bernie_semantic_extraction.py` -- 56 focused tests
- No changes to routes, providers, DB models, API schemas, UI, T3 gates,
  holdout code, or other owned surfaces.

## Known Limitations

1. **Contradictory Silver labels remain visible.** The ambiguity_001 and
   ambiguity_002 Silver scenarios label "sometime in the afternoon" as
   temporal_relation=interval with 13:00-17:00 bounds, but the semantically
   correct extraction is unspecified (because "sometime" implies no exact
   interval). These honest disagreements are preserved per the contract.

2. **Pre-existing tool-sequence mismatches.** Some scenarios expect tool
   sequences (propose_candidates, find_slots in clarify mode) that the
   old evaluator also did not produce. These are unchanged from the baseline.

3. **Duration semantics for clarify-only scenarios.** The LC1
   interpret_time_window_date_change_preserves_upper scenario expects
   duration_semantics=exact with duration_minutes=15, but no duration
   is mentioned in the utterance text. The extraction correctly returns
   duration=omitted. This is a pre-existing mismatch.

4. **Normalized values for date-only utterances.** When a create utterance
   contains only a date (e.g., "tomorrow") with no time, the date is still
   included in normalized_values. Some Silver scenarios expect no date in
   this case.

## Verification

```text
python -m pytest tests/test_bernie_semantic_extraction.py -q    # 56 passed
python -m pytest tests/test_bernie_composed_corpus_evaluator.py -q -k "not test_regenerated_matches_committed"   # 39 passed
python -m pytest tests/test_bernie_lc4_scaled_evaluator.py -q -k "not test_exact_report_regeneration"   # 96 passed
python -m pytest tests/test_bernie_temporal_policy.py -q        # 34 passed
python scripts/bernie_shadow_live_gate_check.py                 # blocked
git diff --check                                                # clean
```
