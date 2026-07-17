# DeepSeek Synthetic Noise Recovery Review Round 2

Date: 2026-07-17

Reviewer: DeepSeek V4 Flash/high via Claude Code `--bare` (fresh independent context)

## Source verification

| Item | Expected | Actual | Status |
|---|---|---|---|
| Source HEAD | `b1380f6aaf6eb21d9af763cfcc8db5130cba138d` | `b1380f6aaf6eb21d9af763cfcc8db5130cba138d` | ✅ |
| Candidate path | `tests/fixtures/bernie_synthetic_noise/candidates_sol_recovery.jsonl` | Same | ✅ |
| Canonical hash | `sha256:ae14c613ecdd87aac39201d44a8024f3b9216f871c7d5859c4249e7f4026c665` | `sha256:ae14c613ecdd87aac39201d44a8024f3b9216f871c7d5859c4249e7f4026c665` | ✅ |
| Record count | 192 | 192 | ✅ |
| Seeds count | 96 | 96 | ✅ |
| Variants per seed | 2 (medium, high) | 96 × 2 = 192 | ✅ |

## Mechanical validation

- Candidate validation script: **pass, 192/192**
- `pytest tests/test_bernie_synthetic_noise_corpus.py tests/test_bernie_synthetic_noise_sol_recovery.py -q`: **11 passed**
- `git diff --check`: **clean**

## Round 1 disposition verification

Round 1 was superseded because 18 records declared `correction` without an explicit correction surface. Sol removed only those 18 labels, added a regression test, and regenerated.

**Verification:**

1. **30 records** now declare `correction` in `noise_operations` (24 correction-form + 6 entity_state=corrected on other forms).
2. **Every correction declaration has an explicit `Correction—` or `—sorry,` surface** in the dialogue text. The regression test `test_every_declared_correction_is_explicit_in_the_dialogue` passes.
3. **Removing the 18 labels did not invalidate any operation count:**
   - All medium (variant 1) records have ≥4 noise operations (minimum 2 required).
   - All high (variant 2) records have ≥6 noise operations (minimum 3 required).
   - No record dropped below the minimum threshold after correction-label removal.

## Semantic review (all 192 records)

### 1. Action/entity/temporal/duration/status semantics

All 192 candidates preserve their seed's:
- **Intended action**: create (32), move (32), resize (32), cancel (32), status_change (32), explain_schedule (32) — each action appears exactly 32 times across 8 dialogue forms × 2 variants.
- **Temporal/duration semantics**: normalized date/time/duration values match the seed contract.
- **Patient/practitioner semantics**: exact, ambiguous, omitted, corrected, negated, mismatched — all faithfully reflected.

### 2. Dialogue form correctness

| Form | Count | Turn count | Pattern verified |
|---|---|---|---|
| one_shot | 24 | 1 turn | Single receptionist utterance |
| clarification | 24 | 2 turns | Context-setting turn + clarifying request |
| correction | 24 | 2 turns | First turn has "a doctor", final turn has "Dr Shera" after `Correction—` |
| reversal | 24 | 2 turns | Explicit reversal surface ("stop", "leave unchanged") |
| ellipsis | 24 | 2 turns | Omitted recoverable syntax in second turn |
| anaphora | 24 | 2 turns | Pronoun/noun-phrase reference in second turn |
| repeated | 24 | 2 turns | Repeated request with identical or near-identical wording |
| session_restart | 24 | 2 turns | Fresh start marker + repeated request |

### 3. Receptionist-to-Bernie naturalness

All dialogue reads as a receptionist issuing instructions to Bernie (assistant). Language is appropriately concise, uses Australian English conventions ("appt", "mins", "tomorrow"), and fits the staff-to-assistant register. No patient-facing, clinical, or triage language appears.

### 4. Variant distinction (medium vs high)

- **Medium** (variant 1): 4–5 noise operations per record. Baseline: `filler`, `abbreviation`, `punctuation_case`, `staff_shorthand` plus optional form-specific operation (`correction`, `reversal`, `ellipsis`, `anaphora`).
- **High** (variant 2): 6–8 noise operations per record. Baseline: `filler`, `abbreviation`, `speech_disfluency`, `reordered_slots`, `staff_shorthand`, `dictation_artifact` plus form-specific operation(s).

### 5. Evidence spans

Every record's `evidence_spans` contains exactly the keys from its seed's `required_evidence_keys`. Every coordinate slices the correct named utterance in the correct turn. Spans are placed on the latest turn containing the evidence surface.

### 6. Ambiguity/omission preservation

Records for seeds with `patient_semantics: ambiguous` or `omitted` correctly use "someone" or omit the patient entirely. Records with `practitioner_semantics: ambiguous` or `omitted` use "a doctor". No specific names leak into semantically ambiguous/omitted slots.

### 7. Closed authority

Every record has:
```json
"authority_grant": {
  "provider_write": false,
  "diary_write": false,
  "confirmation": false,
  "override_authority": false
}
```
`semantic_change`: "none", `provenance`: "silver", `adjudication`: "pending".

### 8. Noise operations truthfulness

All declared noise operations are truthful and supported by the dialogue text. Every operation is from the allowlist. No operation is declared without a corresponding surface in the text.

### 9. Protected/external/corpora boundaries

No protected holdout (v1-v10), historical diary, Kaggle appointment-call, or external corpus reference detected. No email, phone, long identifier, URL, or clinical detail present.

## Classification

**ACCEPT: 192**
**QUARANTINE: 0**
**REJECT: 0**

No record requires quarantine or rejection. Every candidate is mechanically valid, semantically faithful to its seed, truthfully declared in noise operations, and consistent with the Silver corpus contract.

---

**DECISION: pass**
**SOURCE_HEAD: b1380f6aaf6eb21d9af763cfcc8db5130cba138d**
**CANDIDATE_SHA256: sha256:ae14c613ecdd87aac39201d44a8024f3b9216f871c7d5859c4249e7f4026c665**
**REVIEWED: 192**
**ACCEPT: 192**
**QUARANTINE: 0**
**REJECT: 0**
**PROTECTED_ACCESS: false**
**EXTERNAL_CORPUS_ACCESS: false**
