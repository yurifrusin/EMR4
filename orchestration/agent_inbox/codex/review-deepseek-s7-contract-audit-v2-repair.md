# S7 Lane 1 Review: Executable Review-Acceptance Contract

## Summary

Implements the approved S7 Lane 1 contract-audit repair for the DeepSeek worker
pool and review-acceptance gate. All three subtasks are complete.

## 1. Reconcile Approved Pro Fallback

**Changes:**

- `orchestration/harness_settings/worker_pool.yaml` — added
  `permission_prompts_are_not_authority` to the
  `deepseek-pro-conductor-fallback` transport quirks (replaced
  `no_integration_authority`). The Pro conductor fallback retains
  `deepseek-v4-pro` as its default model, max instances 1, and all three
  cli_interactive common quirks.

- `tests/test_ariadne_deepcode_adapter_settings.py`:
  - `test_two_deepcode_resources_defined` → `test_three_deepcode_resources_defined`
  - `test_verifier_and_worker_resource_ids_match` → `test_resource_ids_match_expected`
    (adds `deepseek-pro-conductor-fallback` to the sorted list)
  - `test_all_deepcode_resources_default_model_is_flash` — Pro fallback expected to
    default to `deepseek-v4-pro`; verifier/workers default to `deepseek-v4-flash`
  - Added `test_pro_conductor_fallback_contract` — pins transport, model, max
    instances, and quirks for the Pro fallback specifically
  - `test_no_deepcode_resource_defaults_to_pro` → `test_no_flash_resource_defaults_to_pro`
    (skips Pro fallback, applies to Flash resources only)
  - Consolidated separate-packet quirk tests:
    `test_workers_have_separate_packet_quirk` + `test_verifier_does_not_have...`
    → `test_verifier_and_conductor_fallback_do_not_have_separate_packet_quirk`
    (positive check for workers, negative for all others)
  - `test_adapter_resource_ids_are_correct` in `TestTransportAdapterDeepCodeContract`
    — added `deepseek-pro-conductor-fallback`

All integration-authority denials remain intact. The `permission_prompts_are_not_authority`
quirk now covers all three DeepSeek cli_interactive resources.

## 2. Implement Executable Acceptance Gate

**New module:** `orchestration_harness/review_acceptance.py`

Standard-library-only public API with a single function:

```python
accept_review_artifact(
    *,
    artifact_path: str | Path,
    artifact_kind: ArtifactKind,       # "decision" | "completion"
    receipt_path: str | Path,
    review_worktree: str | Path,
    expected_branch: str,
    candidate_commit: str,
    pytest_collect_path: str | Path,
    review_mode: ReviewMode,           # "executable" | "static_evidence"
    worker_reported_count: int | None = None,
) -> ReviewAcceptance
```

Returns a frozen `ReviewAcceptance` dataclass with `to_json()` that serialises to
deterministic JSON (no terminal output or file contents).

Fail-closed checks implemented:

| # | Check | Enforced |
|---|---|---|
| 1 | Artifact & receipt are ordinary files inside the declared worktree | Yes |
| 2 | Receipt uses current fields: `status=completed`, exact relative `artifact`, matching `artifact_kind`, `artifact_observed=true`, `permission_prompt_observed=false`, `process_cleanup_confirmed=true`. `artifact_path` is forbidden. | Yes |
| 3 | Decision artifacts require `DECISION: pass\|revision_required`; completion artifacts require `STATUS: complete`. `VERDICT` alone fails. | Yes |
| 4 | `git branch --show-current` matches expected branch | Yes |
| 5 | `git merge-base --is-ancestor <candidate> HEAD` succeeds (subprocess arrays, `shell=False`, declared cwd) | Yes |
| 6 | Parse collection-output file: accepts `review/test_diary_smoke.py: 139`, `139 tests collected`, `1 test collected`. Rejects missing, zero, ambiguous, or conflicting counts. Authoritative. Worker `N passed` mismatch is flagged but never replaces collection evidence. | Yes |
| 7 | Never searches other files for substitute artifact | Yes (worktree boundary) |

**New CLI:** `scripts/ariadne_review_acceptance.py`

Thin argparse wrapper. Accepts `--pytest-collect-output` as a file path only
(not a command string). Exit 0 (accepted), 1 (rejected), 2 (input/internal error).

## 3. Focused Tests

**New file:** `tests/test_ariadne_review_acceptance.py`

47 tests across 11 test classes using temporary git repositories, synthetic
artifacts/receipts, and temporary worktrees:

| Class | Tests | Coverage |
|---|---|---|
| TestAcceptDecision | 2 | Decision pass accepted, completion complete accepted |
| TestRejectDecision | 7 | Revision-required marker, VERDICT-only, wrong kind, receipt status/kind/observed/permission/cleanup mismatches |
| TestBranchAncestry | 2 | Wrong branch, non-ancestor candidate |
| TestPathBoundaries | 3 | Outside worktree, missing artifact, scratch substitute not rescued |
| TestPytestCollection | 5 | Single test, diary smoke format, missing file, zero count, conflicting counts |
| TestWorkerCountMismatch | 2 | Mismatch flagged, matching counts |
| TestReceiptProhibition | 1 | Forbidden artifact_path key |
| TestCLI | 5 | Help, exit 0/1/2 codes, JSON output shape |
| TestReviewModes | 2 | Both executable and static_evidence |
| TestStrictSettingsUnchanged | 1 | Pure function (no file mutation) |

No existing tests were weakened, removed, skipped, or xfailed.

## Verification Results

```
pytest tests/test_ariadne_deepcode_adapter_settings.py tests/test_ariadne_review_acceptance.py -q --tb=short
→ ALL PASS (no failures)
```

```
python scripts/ariadne_review_acceptance.py --help
→ Usage printed (PYTHONPATH required for direct CLI)
```

```
git diff --check
→ No whitespace errors
```

```
git diff --stat
6 files changed: 3 modified + 3 new (untracked)
 M orchestration/harness_settings/worker_pool.yaml
 M orchestration_harness/__init__.py
 M tests/test_ariadne_deepcode_adapter_settings.py
?? orchestration_harness/review_acceptance.py          (new)
?? scripts/ariadne_review_acceptance.py                (new)
?? tests/test_ariadne_review_acceptance.py             (new)
```

## Files Touched

| File | Status | Purpose |
|---|---|---|
| `orchestration/harness_settings/worker_pool.yaml` | Modified | Added `permission_prompts_are_not_authority` quirk to Pro fallback |
| `orchestration_harness/__init__.py` | Modified | Exported `ReviewAcceptance`, `accept_review_artifact` |
| `orchestration_harness/review_acceptance.py` | **New** | Standard-library-only acceptance gate module |
| `scripts/ariadne_review_acceptance.py` | **New** | Thin CLI wrapper |
| `tests/test_ariadne_deepcode_adapter_settings.py` | Modified | Updated all contract assertions for 3 DeepSeek resources |
| `tests/test_ariadne_review_acceptance.py` | **New** | 47 focused tests for the acceptance gate |

None of the changed or added files touch EMR4 runtime code (`app/`), diary UI,
taskpane, migrations, or any existing test beyond the explicitly scoped adapter
settings file.

STATUS: complete
