# S7 Lane 1: Contract Audit Revision 2 — DeepSeek Flash Review Artifact

Role: implementation owner, same lane
Resource: `deepseek-flash-workers`
Model: `deepseek-v4-flash`
Reasoning: high

---

## Summary

All five required corrections from the revision-2 packet have been applied and
verified. 82/82 focused tests pass, CLI smoke test passes, `git diff --check` is
clean, and `orchestration_harness/__init__.py` is absent from `git diff --name-only`.

---

## Correction 1 — Marker parsing matches `runner.mjs::validArtifact()`

**Problem:** The previous whole-line regex accepted a one-cell row
(`| DECISION: pass |`) but rejected a normal multi-column row such as
`| Verdict | **DECISION: pass** | Notes |`.

**Fix:** Replaced the multiline regex approach (`_DECISION_RE`, `_COMPLETION_RE`,
`_VERDICT_ONLY_RE`, `_canonicalise_marker()`, `_parse_artifact_marker()`) with a
line-by-line cell-splitting algorithm in `_parse_artifact_marker()` that mirrors
the exact JS logic from `runner.mjs::validArtifact()`:

- Iterate each line of the artifact text
- If the line contains `|`, split on `|` to get individual cells
- Trim each cell and strip surrounding `*`, `_`, `` ` `` markdown formatting
- Apply the exact case-insensitive regex against each normalised cell

**New tests added to `TestAcceptDecision`:**
- `test_decision_multi_column_row_accepted` — `| Verdict | **DECISION: pass** | Notes |`
- `test_completion_multi_column_row_accepted` — `| Status | `STATUS: complete` | Notes |`
- `test_multi_column_wrong_kind_rejected` — multi-column DECISION with artifact_kind=completion

---

## Correction 2 — `artifact` and `artifact_kind` added to `ReviewAcceptance`/JSON

**Problem:** The JSON contract omitted declared `artifact` and `artifact_kind`
fields that the prior packet explicitly required.

**Fix:** Added fields to the `ReviewAcceptance` dataclass:

```python
artifact: str | None
artifact_kind: str | None
```

Populated in `accept_review_artifact()` with the resolved artifact path and the
`artifact_kind` parameter. Updated `_check_json_contract()` in tests to assert
both fields are present and non-null. Updated `test_cli_json_output_shape` to
include both fields in the expected-key list and assert their values.

---

## Correction 3 — `orchestration_harness/__init__.py` restored to HEAD

**Problem:** The file had an out-of-scope line-wrap diff despite the prior
artifact claiming it was reverted.

**Fix:** Executed `git checkout HEAD -- orchestration_harness/__init__.py`
before any other changes. Confirmed absent from `git diff --name-only`.

---

## Correction 4 — Runtime validation for `review_mode` and receipt type

**Problem:** Type aliases are not runtime validation. A direct API caller could
pass an invalid `review_mode`. A receipt JSON value that is not an object would
raise an uncaught `.get` error.

**Fix:**
- Added `_VALID_REVIEW_MODES = frozenset({"executable", "static_evidence"})`
  and an early `if review_mode not in _VALID_REVIEW_MODES: raise ValueError(...)`
  check in `accept_review_artifact()` before any I/O or git calls.
- Added runtime `isinstance(receipt_data, dict)` check after `json.loads()` in
  the receipt content validation block. Non-dict receipts produce a structured
  rejection reason instead of an uncaught `.get` error.

**New tests in `TestInvalidReviewMode`:**
- `test_invalid_mode_raises_value_error` — API-level `ValueError` for
  `review_mode="invalid_mode"`
- `test_cli_invalid_mode_rejected` — CLI exits 2 (argparse-level rejection)

**New tests in `TestRejectDecision`:**
- `test_non_dict_receipt_rejected` — JSON array as receipt
- `test_non_object_receipt_top_level_string_rejected` — JSON string as receipt

---

## Correction 5 — Existing functionality preserved

- Both Pro fallback quirks preserved: `worker_pool.yaml` and
  `test_ariadne_deepcode_adapter_settings.py` changes remain as-is.
- Relative path/worktree containment, direct CLI bootstrap, strict collection
  parsing, branch/ancestry checks all unchanged.
- All existing focused tests continue to pass.

---

## Verification Evidence

```powershell
# Focused test suite
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest `
  tests/test_ariadne_deepcode_adapter_settings.py `
  tests/test_ariadne_review_acceptance.py -q --tb=short
# Result: 82 passed (54 + 28), 0 failed

# CLI smoke test
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts/ariadne_review_acceptance.py --help
# Result: exit 0, usage displayed

# Whitespace check
git diff --check
# Result: no whitespace errors

# __init__.py absent from diff
git diff --name-only
# Result: orchestration_harness/__init__.py NOT present
```

**Diff summary (pre-existing Pro fallback work only):**
- `orchestration/harness_settings/worker_pool.yaml` — 1 line changed (permission_prompts_are_not_authority quirk added)
- `tests/test_ariadne_deepcode_adapter_settings.py` — 51 insertions, 24 deletions (Pro conductor fallback tests)

**New/modified untracked files (review_acceptance module):**
- `orchestration_harness/review_acceptance.py` — corrections 1, 2, 4 applied
- `scripts/ariadne_review_acceptance.py` — unchanged (CLI argparser already enforces choices)
- `tests/test_ariadne_review_acceptance.py` — corrections 1, 2, 4 test additions

STATUS: complete
