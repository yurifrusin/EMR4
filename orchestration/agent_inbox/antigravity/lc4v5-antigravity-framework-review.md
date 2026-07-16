# LC4V5 Content-Blind Framework Independent Review

Date: 2026-07-16
Reviewer: Gemini 3.5 Flash through a fresh Antigravity project
Worktree: `C:\Users\sarashera\EMR4-worktrees\lc4v5-framework-gemini`
Branch: `antigravity/lc4v5-content-blind-framework-review`
Reviewed Git HEAD: `4cfa2c45c24719c1cf6f7d756f0533056eb08004`

## Mandatory Rehydration and Ariadne Preflight Receipt

In accordance with `AGENTS.md` rehydration rules, a fresh Ariadne orchestrator receipt was generated. The preflight script successfully validated all five rehydration sources:
- `live_handover_current_baton`
- `current_authority_allocation`
- `active_plan_and_acceptance`
- `protected_evidence_boundaries`
- `git_refs_and_worktree`

### Preflight Output

```json
{
  "authority_boundary": "receipt_only_no_worker_control_or_integration_authority",
  "continuation_event": "post_compaction",
  "planned_action": "sprint_planning",
  "reasons": [],
  "schema_version": "ariadne.orchestrator_receipt.v1",
  "settings_fingerprint": "sha256:30e48e4a6bac8f20617d0f8fd0a6e24992d278151a92b85b09da65b1603ee7a2",
  "status": "passed",
  "worker_dispatch_permitted": true
}
```

## Validation Tests Run

The focused synthetic test suite and ordinary dependency tests were executed serially:
```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_bernie_scenario_spec.py tests/test_bernie_composed_evaluator.py tests/test_bernie_lc4v5_holdout_framework.py -q
```
**Result:** 113 passed. The codebase successfully compiled, and `git diff --check` returned no style or formatting violations.

## Review Findings

1. **Strict Unknown-Field Rejection and Lossless Hashing:**
   - All Pydantic models inherit from `StrictModel` setting `extra="forbid"` and `frozen=True`.
   - `canonical_json_bytes` enforces strict key sorting, compact spacing, and forbids NaNs/Infs, ensuring lossless SHA-256 canonical hashing of all content.

2. **Exact Population Shape:**
   - `V5Corpus` strictly validates the fixed shape: 24 groups, 12 scenarios per group (288 scenarios), 288 unique scenario IDs, 288 unique coverage cells.
   - Splits scenarios into exactly 216 one-shot and 72 multi-turn scenarios.
   - Ensures the 6 implemented actions are represented: `create`, `move`, `resize`, `cancel`, `status_change`, `explain_schedule`.
   - Validates that all scenarios are synthetic `gold`/`adjudicated`.
   - `_validate_complete_repeats` verifies exactly 576 samples (2 repeats per scenario, indexes 0 and 1) with zero tolerance for missing/duplicate indexes.

3. **Lossless Hash Binding and Trust Gates:**
   - Precondition checks bind `source_commit`, `framework_hash` (`file_hash(paths.framework)`), `evaluator_hash` (`file_hash(paths.evaluator)`), `corpus_hash`, and `manifest_hash` through the `V5Seal` and `V5Manifest`.
   - `execute_one_shot` reads the persisted report and seal back from disk and verifies the consumed seal cryptographically binds the final report hash and attempt ID. No trust gap or mutability exists.

4. **Exclusive One-Shot State Machine:**
   - The framework acquires an exclusive marker file using `"x"` mode before starting the evaluation. Reruns are denied if the file exists.
   - The marker file is never deleted on error, exception, or success, successfully burning the attempt on any failure.

5. **Aggregate-Only Output:**
   - `V5AggregateReport` strips all case-level data.
   - If an exception occurs, only a fixed error code is written to the receipt, preventing exception text or case info from being persisted.
   - `report_contains_case_level_keys` performs recursive checks for forbidden keys (`scenario_id`, `scenario_ids`, `utterance`, `utterances`, `case_ids`, `failed_case_ids`), failing closed if any are present.

6. **Twelve Semantic Dimensions and Four Failure Layers:**
   - The framework enforces exactly the 12 frozen dimensions and 4 failure layers. Any extra or missing fields fail validation closed.

7. **Exact Frozen Thresholds:**
   - Enforces `complete_contract` and all 12 dimensions >= 548/576.
   - Enforces `safety` == 576/576, with zero safety-layer failures.
   - Enforces interpretation/policy/integration failure layers <= 28.
   - Enforces predefined slices >= 90%, worst slice >= 0.90, and zero repeat variance.

8. **Evidence Invalidity Precedence:**
   - If `evidence_valid` is False (failed manifest, mismatched commit/hashes, or evaluation exceptions), the decision is strictly resolved as `"evidence_invalid"`, taking precedence over any product-pass checks.

9. **No Open Authority Surfaces:**
   - No runtime adapters, provider access (T3.5), DB operations, REST routes, or sidebar APIs are imported or opened.

DECISION: pass
