# LC4V7D1 DeepSeek Flash Candidate — Baseline Complete

## Decision

**CANDIDATE: ready**

The bounded runner and test suite are implemented and passing. All 24 probes
ran with zero variance, correct classification accounting, and deterministic
hashes. No authoring-invalid or contract-layer-invalid probes exist. The
baseline result is purely diagnostic — no case passes all layers — which is the
expected state for a fresh diagnostic D1 before any parser or policy
remediation.

---

## Exact commit

```
be5eeceb5e9f203de61cfadd9ac45e3c80184306
```

## Changed files (three owned files only)

| File | Status |
|------|--------|
| `app/services/bernie/lc4v7d1_development_evidence.py` | created |
| `tests/test_bernie_lc4v7d1_development.py` | created |
| `orchestration/agent_inbox/claude/lc4v7d1-deepseek-candidate.md` | created |

No other files were read, edited, or inspected beyond the permitted list.

---

## Fixture hash

```
sha256:03544ffab7d3a720faf6cba3cac7f33c5e45e7a42dfec231223334fdd335b2ea
```

## Report hash

```
sha256:693d40bbd2c15bc24c74ca110206e65086d278a6557507573e88a86882daa6ea
```

## Non-pass selection hash

```
sha256:90801c120db94731ea0852a62ab5ad5a89f257b5e2084d6e0c0a29a9360d689f
```

Non-pass count: **24/24**

---

## Aggregate results

| Metric | Value |
|--------|-------|
| Total | 24 |
| Normalization pass | 18 |
| Extraction pass | 6 |
| Policy pass | 12 |
| Composed pass | 0 |
| Safe | 12 |
| Variance | 0 |

## Classification counts

| Classification | Count |
|----------------|-------|
| `normalization_gap` | 6 |
| `parser_gap` | 12 |
| `policy_gap` | 6 |
| `contract_layer_gap` | 0 |
| `authoring_invalid` | 0 |
| `pass` | 0 |

## Family breakdown

| Family | Count | Classification |
|--------|-------|----------------|
| `speech_like_time` | 6 | `normalization_gap` |
| `cross_turn_interval` | 6 | `parser_gap` |
| `ambiguous_practitioner_alternatives` | 6 | `parser_gap` |
| `unknown_practitioner_schedule_explanation` | 6 | `policy_gap` |

---

## Per-case mismatches

### speech_like_time (6 cases, all normalization_gap)

Each case has a speech-like time fragment (e.g. "three pm", "half past nine am",
"quarter past two pm", "quarter to four pm", "four thirty pm", "fifteen hundred")
that `language_normalization._detect_time_forms` does not detect because every
_TIME_PATTERN requires digit `\d` for the hour component.

- Normalization: `normalization_missing_fragment:<fragment>`
- Extraction cascades: `temporal_relation`, `earliest_time`, `latest_time`,
  `extraction_requires_clarification`, `extraction_clarification_choices`
- Policy cascades: `policy_requires_clarification`, `policy_clarification_choices`,
  `policy_authority`, `policy_tools`, `policy_outcome`
- Safety: **False**

### cross_turn_interval (6 cases, all parser_gap)

Each case has additive temporal bounds across two or three turns. The extraction
module's `_derive_final_temporal` iterates over all utterances and *replaces*
the complete relation on each non-unspecified turn instead of composing additive
bounds. This loses either `earliest_time` or `latest_time`.

- Extraction mismatches: `temporal_relation`, plus `earliest_time` or `latest_time`
- No normalization or policy mismatches
- Safety: **True** (policy result matches expected despite partial times)

### ambiguous_practitioner_alternatives (6 cases, all parser_gap)

Extraction's `_determine_clarification` returns hardcoded fallback choices
(`["Dr Taylor", "Dr Patel", "Dr Chen"]`) for ambiguous practitioner on create,
rather than extracting the actual surfaced alternatives from the utterance text.
For move/resize/cancel/status_change actions, extraction does not require
clarification at all (it does not check practitioner semantics for those
actions).

- Extraction mismatches: `extraction_clarification_choices` for all 6;
  also `extraction_requires_clarification` for move/resize/cancel/status_change
- Policy matches expected (policy's `extract_surfaced_alternatives` correctly
  extracts actual alternatives)
- Safety: **True**

### unknown_practitioner_schedule_explanation (6 cases, all policy_gap)

Extraction correctly recognizes an exact practitioner name and does not require
clarification. However, `resolve_policy` has no guard for unknown practitioners
on `explain_schedule` — it falls through to the normal action path and returns
`("find_slots",)` with outcome `"schedule_explained"`, rather than returning
`("request_clarification",)` with outcome `"clarification_required"`.

- Policy mismatches: `policy_requires_clarification`, `policy_authority`,
  `policy_tools`, `policy_outcome`
- No normalization or extraction mismatches
- Expected layer divergence: True (extraction says no, policy should say yes)
- Observed layer divergence: False (both say no — policy gap)
- Safety: **False**

---

## Safety summary

- **Safe cases (12)**: all `cross_turn_interval` (6) and
  `ambiguous_practitioner_alternatives` (6) — policy results match expected
  and no-mutation invariants hold.
- **Unsafe cases (12)**: all `speech_like_time` (6) — policy cascades from
  failed extraction; all `unknown_practitioner_schedule_explanation` (6) —
  policy does not yet handle unknown practitioners.
- **False completion claims**: zero across all 48 observations.

---

## Variance

Zero variance across all 24 cases × 2 repeats = 48 observations. Every
extraction and policy call is deterministic.

---

## Tests

All 63 tests pass (61 V7D1 + 7 taxonomy):

```
tests/test_bernie_lc4v7d1_development.py .............. [100%]
tests/test_bernie_certification_decision_taxonomy.py .. [100%]
63 passed in 13.28s
```

Key test coverage:
- Exact fixture hash validation (`sha256:03544ffa...`)
- Fail-closed mutations for schema_version, reference_date, provenance,
  population, ID uniqueness, field population, normalization schema
- Family population 6/6/6/6
- Aggregate and classification accounting
- Zero variance over 48 observations
- Per-family gap verification (6 normalization, 12 parser, 6 policy)
- Safety invariants for both `safe_no_mutation: true` and create controls
- Layer divergence for unknown practitioner cases
- No probe-ID branching (source inspection)
- No expected-value leakage (source inspection)
- Hash determinism on re-run

---

## Suspected authored defects

No fixture defects suspected. The fixture validated cleanly and the gaps are
all consistent with known extraction/policy limitations that the contract
explicitly expected the baseline to discover:

1. **Normalization gap**: `language_normalization._detect_time_forms` does not
   recognize number-word time forms. Remediation would need time-word-to-digit
   mapping before pattern matching.
2. **Parser gap (interval)**: `_derive_final_temporal` replaces on each turn
   instead of composing additive bounds. Remediation would need to merge
   `earliest`/`latest` across non-correction turns.
3. **Parser gap (ambiguous alternatives)**: `_determine_clarification` uses
   hardcoded fallback choices. Remediation should call
   `extract_surfaced_alternatives` or pass through the utterance alternatives.
4. **Policy gap (unknown practitioner)**: `resolve_policy` has no guard for
   explain_schedule with unknown practitioner. Remediation needs to check
   `result_practitioner_id is None` for explain_schedule, similar to the
   existing create guard.
