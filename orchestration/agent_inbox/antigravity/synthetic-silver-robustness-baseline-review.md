# Gemini Synthetic Silver Robustness Baseline Review

- **Worktree:** `C:\Users\sarashera\EMR4-worktrees\synthetic-silver-robustness-review`
- **Branch:** `codex/synthetic-silver-robustness-review`
- **Source Head:** `ec3d32dca17b583b7e7f7f05939e235b43e2ff3a`
- **Report Hash:** `sha256:18501cf5c8d28c0e660a9f5c7b15f7690622e44c90b248d51301c6ece03973c5`
- **Candidate Hash:** `sha256:ae14c613ecdd87aac39201d44a8024f3b9216f871c7d5859c4249e7f4026c665`
- **Model:** Gemini 3.5 Flash (Medium) via fresh Antigravity project
- **Role:** independent exact-baseline reviewer and veto
- **Acceptance/integration owner:** GPT Sol

---

## Executive Summary

We have performed an independent exact-baseline review of the synthetic Silver receptionist robustness evaluations. Based on our analysis and execution of the verification suite:
- The admitted population of 192 candidates and all input hashes bind exactly to the frozen contracts.
- Candidate scenario specs are reconstructed correctly, preserving the ordinary development semantic and diary oracles.
- The deterministic interpretation path operates purely on dialogue utterances and reference dates, with zero oracle/expected value leakages.
- The existing replay and scorer pipeline runs without any evaluator-specific custom fallbacks or product behaviour repair.
- The reported metrics reproduce perfectly: 2/192 candidates complete product pass, 190/192 candidates failed, 384/384 safety checks passed, with zero repeat variance.
- No source utterances are leaked in the final JSON report.
- The `baseline_complete` flag is appropriately restricted to represent evaluation execution completeness rather than product performance.
- The historical metadata-only protected filename incident has been fully contained and had no influence on inputs, execution, or results.

Accordingly, the baseline is verified as valid evidence.

---

## Detailed Check Verification

### 1. Exact Binding of Populations and Hashes
The file hashes and counts correspond exactly to the frozen contract:
- **Candidates File:** `tests/fixtures/bernie_synthetic_noise/candidates_sol_recovery.jsonl`
  - Canonical Hash: `sha256:ae14c613ecdd87aac39201d44a8024f3b9216f871c7d5859c4249e7f4026c665`
  - File Payload Hash: `sha256:193b705e0ce06fa32b72a063dec659e52a584fc489137bd7cbad8e511940e37f`
- **Semantic Seeds Manifest:** `tests/fixtures/bernie_synthetic_noise/semantic_seeds.json`
  - Manifest Hash: `sha256:fd1c619cf826d72b57ffdfc62cafbafa209f8aed87a8f8e6bad6c22c2f93c7cb`
- **Source Development Corpus:**
  - Corpus Hash: `sha256:af8f3276a50a2defcf4e4f65570a5dd4de0d252544ff6d695792d63e7e518195`
- **Admission Record:** `tests/fixtures/bernie_synthetic_noise/admission.json`
  - Decision: `accept_development_silver`
  - Candidate Count: 192 (fully accepted, 0 quarantined, 0 rejected)

### 2. Candidate Reconstruction Integrity
The `_candidate_scenario` function in `app/services/bernie/synthetic_noise_robustness.py` correctly instantiates each candidate as a `ReceptionScenarioSpec` by:
1. Cloning the source development scenario loaded from the `DevelopmentOnlyLoader` (representing the semantic and diary oracle).
2. Swapping only the candidate ID, description, provenance, adjudication status, dialogue turns, source evidence spans, and noise/language form metadata.
This guarantees that all oracle semantic rules and diary expectations are preserved during adaptation.

### 3. Dialogue Isolation in `deterministic_interpret`
Verification of `deterministic_interpret` in `app/services/bernie/composed_corpus_evaluator.py` confirms that the interpretation function extracts dialogue turns and references `reference_date` dynamically. Only these extracted parameters are passed down to `extract_semantics`. Expected outcomes, expected tool sequences, deltas, and other oracle fields from the scenario contract are never leaked or referenced during interpretation.

### 4. Existing Replay/Scorer Path Execution
The baseline script executes the standard `deterministic_replay` and `score_interpretation_replay_pair` compose-scoring methods. No custom mock adapters, product repairs, or evaluator-specific fallback conditions are present in the pipeline.

### 5. Report Completeness and Leak Prevention
All 192 candidates are fully evaluated twice, resulting in 384 observations. Detailed per-case failure breakdowns are recorded for every failing candidate in the JSON report under `failure_cases`. A grep scan of `docs/bernie-synthetic-silver-robustness-baseline-report.json` shows no turns or source utterances were recorded inside the final report, verifying `contains_source_utterances: false`.

### 6. Reproduction of Metrics and Zero Variance
Running the automated test suite and check script verifies that the baseline report reproduces with:
- **Total Candidates:** 192
- **Evaluated Observations:** 384
- **Product Complete Candidates:** 2/192
- **Product Failed Candidates:** 190/192
- **Safety Passed Observations:** 384/384
- **Repeat Variance:** 0 (all candidate observation fingerprints match exactly across runs)

### 7. Evidence vs. Product Pass Distinction
The script utilizes the `baseline_complete` decision flag purely to denote execution completeness (192 candidates, 384 runs, no safety violations, zero repeat variance). It does not mask or misrepresent the poor product pass rate (2/192).

### 8. Containerization of the Metadata Discovery Incident
No files outside the authorized development bounds were opened, loaded, read, or hashed. The metadata-only discovery of filenames from protected directories remains entirely contained.

---

DECISION: pass
SOURCE_HEAD: ec3d32dca17b583b7e7f7f05939e235b43e2ff3a
REPORT_SHA256: sha256:18501cf5c8d28c0e660a9f5c7b15f7690622e44c90b248d51301c6ece03973c5
CANDIDATES: 192
OBSERVATIONS: 384
COMPLETE: 2
FAILED: 190
SAFETY_PASS: 384
VARIANCE: 0
PROTECTED_ACCESS: false
