# LC4V7 Source-Binding Amendment Independent Review

Date: 2026-07-16
Reviewer: Gemini 3.5 Flash through a fresh Antigravity project
Worktree: `C:\Users\sarashera\EMR4-worktrees\antigravity`
Branch: `antigravity/current`
Reviewed HEAD Commit: `b4f8cb18fe4229aea7fe230822a9b2832f906bc9`

## Verification Summary

This independent review evaluates the source-binding changes introduced between commits `186ccf44` and `b4f8cb18` to resolve the pre-content integration flaw (where the seal could not contain the future commit hash). The runner was amended to split the reference into a committed corpus-source commit (`source_commit`) and verify its presence, ancestry, and contents.

### 1. Focused Tests Execution
The focused test files were run serially in the `.venv` virtual environment:

- **Framework Tests (`tests/test_bernie_lc4v7_content_blind_framework.py`):**
  - Command: `.venv\Scripts\pytest tests/test_bernie_lc4v7_content_blind_framework.py`
  - Result: **19 passed** (1 warning) in 4.71s.

- **Acceptance Rule Tests (`tests/test_bernie_lc4v7_acceptance_rule.py`):**
  - Command: `.venv\Scripts\pytest tests/test_bernie_lc4v7_acceptance_rule.py`
  - Result: **21 passed** (1 warning) in 4.71s.

All compilation and style checks pass cleanly.

---

## Detailed Findings

### 1. Source Commit Format is Exact
- The runner uses a strict regular expression `COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")` inside `validate_source_binding` to match exactly 40-character hexadecimal git commit hashes.
- Format mismatches immediately reject the run with `"source commit format is invalid"`.

### 2. Corpus Path Remains Inside the Repository
- The path check `corpus_path.resolve().relative_to(ROOT.resolve()).as_posix()` is used.
- Any attempt to reference external or parent paths outside the repository triggers a `ValueError` which is caught to return `"corpus path is outside the repository"`.

### 3. Source Commit is an Ancestor of Execution HEAD
- The runner executes `git merge-base --is-ancestor <source_commit> HEAD` inside the repository.
- If the return code is non-zero, it appends `"source commit is not an ancestor of the execution head"`, successfully blocking commits from unrelated histories or future branches.

### 4. Committed Blob Has the Live Canonical Corpus Hash
- The runner retrieves the committed file contents using `git show <source_commit>:<relative_path>`.
- The retrieved blob is verified to be valid canonical JSON, and its canonical SHA-256 hash is compared to the live `corpus_hash`.
- Any mismatch returns `"source corpus blob hash drift"`.

### 5. Manifest/Seal Source and Hash Checks Fail Closed
- The function `validate_consumed_binding` enforces alignment between the manifest and the seal:
  - `manifest_hash` matches `seal.manifest_hash`.
  - `corpus_hash` matches `seal.corpus_hash`.
  - `source_commit` matches `seal.source_commit`.
  - `attempt_id` matches `manifest.attempt_id`.
- Any misalignment appends a specific drift error, forcing the run to fail closed into an invalid report state (`certification_invalid`).

### 6. Seal Consumption Occurs Before Validation/Execution
- In the `run()` CLI entry point, the seal is loaded and immediately updated to `consumed` on disk via `consume_seal` at lines 384-389.
- This file I/O writes the `"consumed"` state before the corpus or manifest are validated and before any evaluation starts, preventing reuse or bypass in case of execution failure.

### 7. No Real V7 Content, Gold, or Prior Holdouts Introduced
- The working tree and commit diff were inspected. No real receptionist utterances, expected semantic values, scenario IDs, family IDs, or real coverage cells exist in the workspace.
- The framework and tests contain only structural placeholders and mock unit tests.
- Holdouts v1-v6 remain fully sealed and no references to their files exist.

### 8. Layer-Specific Scoring and Aggregate-Only Gates Intact
- No changes were made to `lc4v7_acceptance_rule.py`.
- The independent layer scoring (scoring `extraction_clarification` and `policy_clarification` independently against their respective Gold expectations, then scoring `clarification_composition`) remains untouched.
- The aggregate thresholds (576/576 for safety/policy/composition, >=548/576 for semantic dimensions/complete, >=22/24 for families, >=87/96 for styles) remain unchanged and fully enforced.

---

## Conclusion

The source-binding amendment successfully establishes robust, fail-closed verification that binds the execution HEAD to the committed historical corpus-source state without self-referential commit hash loops. All security boundaries, layer isolation gates, and validation checks perform exactly as required.

DECISION: pass
