
# LC4V8 Pre-Content Framework Veto Review

- **Status:** Complete
- **Date:** 2026-07-16
- **Reviewer:** Gemini 3.5 Flash/medium via Antigravity
- **Worktree:** `C:/Users/sarashera/EMR4-worktrees/lc4v8-gemini-framework-review`
- **Branch:** `antigravity/lc4v8-framework-review`
- **Source Head Commit:** `3c3a2662f1a40a5ccc63160edac0a2fab1ef2d2c`

---

## Audit Checklist & Verification

### 1. Exact Nested Schemas, Fixed Shape, and Unknown-field Rejection
- **Findings:**
  - `validate_fixture_schema` strictly checks fields using the `_unknown` helper. It validates the version, ensures counts (`total_groups`, `total_scenarios`) are not booleans and match expected integers, and checks nested group and scenario schemas (including utterances, diary_state, and expected dimensions).
  - `validate_fixed_shape` verifies group distribution (exactly 24 groups, order `g01` through `g24`), action mapping (4 groups per action for the 6 valid actions), scenario distribution (12 per group, 2 scenarios per form, 3 multi-turn scenarios per group), and coverage cells (must be 288 unique cells).
  - `validate_manifest_schema`, `validate_seal_schema`, `validate_threshold_schema`, and `validate_report_schema` each enforce exact fields and reject unknown properties.
- **Verdict:** **Pass**. All schemas reject unknown fields at all levels.

### 2. Direct Source Ancestry/Blob Binding
- **Findings:**
  - `validate_source_binding` leverages CLI execution of Git commands to directly query repository metadata.
  - It runs `git merge-base --is-ancestor` to verify that the manifest's `corpus_source_commit` is an ancestor of the current execution `HEAD`.
  - It executes `git show <commit>:<path>` to retrieve original committed file blobs and checks that currently loaded file bytes (`fixture`, `framework`, `thresholds`) match their respective committed states exactly.
- **Verdict:** **Pass**. No caller-supplied assertions are trusted; ancestry and blob content are locked directly via Git.

### 3. Manifest, Thresholds, Seal, Attempt ID, and Exclusive Marker Binding
- **Findings:**
  - `run_one_shot` verifies that the `seal.attempt_id` matches the `expected_attempt_id`, and that `seal.manifest_sha256` matches the SHA-256 hash of the manifest bytes.
  - The manifest path configurations are verified to match resolved relative paths.
  - Exclusive marker instantiation uses `os.open` with `os.O_CREAT | os.O_EXCL`, guaranteeing atomic creation.
- **Verdict:** **Pass**.

### 4. Irreversible Consumption on Exit Paths
- **Findings:**
  - The outer `try`/`finally` block in `run_one_shot` ensures that `marker.consume` is called on any return, validation error, or exception path.
  - `AttemptMarker.consume` transitions the state to `"consumed"` on disk. The class does not offer any deletion or restoration logic.
  - If any validation or run error is encountered before scenario execution, the marker still transitions to `"consumed"`.
- **Verdict:** **Pass**.

### 5. Evaluator Callback Isolation
- **Findings:**
  - The `evaluator` callback receives a `ScenarioInput` object containing only `utterances` and `diary_state`.
  - The callback has no access to the scenario's `coverage_cell`, `group_id`, `action`, `language_form`, `multi_turn`, or `expected` Gold fields.
- **Verdict:** **Pass**.

### 6. Raw-output Two-repeat Variance and 13 Dimensions
- **Findings:**
  - `evaluate_scenario` executes the callback twice per scenario.
  - Output validation enforces the presence of all 13 fields in `DIMENSION_NAMES`.
  - Variance is detected by comparing the `_output_fingerprint` of the first and second run. Any variance is registered in the report and invalidates the run.
- **Verdict:** **Pass**.

### 7. Aggregate-only Report
- **Findings:**
  - `_finalize_report` recursively scans the final report structure for forbidden keys (such as `"utterance"`, `"expected"`, `"coverage_cell"`, `"diary_state"`, etc.).
  - If any forbidden key is detected, `evidence["case_artifacts"]` is incremented and the decision becomes `certification_invalid`.
  - A cryptographic `report_hash` binds the complete report contents.
- **Verdict:** **Pass**.

### 8. Evidence-invalid versus Product-fail Taxonomy
- **Findings:**
  - Precedence in `classify_certification` properly prioritizes `evidence_failures` (resulting in `certification_invalid`) over `product_gate_failures` (resulting in `certification_fail`).
  - Evaluator policy or integration failures are tracked as product-level counters, not validation errors.
- **Verdict:** **Pass**.

### 9. Runtime Isolation
- **Findings:**
  - Imports in `lc4v8_content_blind_framework.py` are limited to standard libraries and the local taxonomy classification module. No clinical modules, parsers, or prior holdouts are imported.
  - Isolation verification tests run and pass.
- **Verdict:** **Pass**.

---

## Verdict

The framework successfully implements a fail-closed, isolated, and strictly bound verification lifecycle that fully adheres to the Sol contract and one-shot acceptance rules.

**DECISION: pass**

