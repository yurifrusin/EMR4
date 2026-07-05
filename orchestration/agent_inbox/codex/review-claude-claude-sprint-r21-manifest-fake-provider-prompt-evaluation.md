# review-claude-claude-sprint-r21-manifest-fake-provider-prompt-evaluation

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-r21-manifest-fake-provider-prompt-evaluation` |
| Status | queued |

## Review Request

R21 eval seam ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - NEW: `app/services/ai/evals/manifest_eval.py` — fake-provider evaluation seam.
    Provides `ManifestPromptInput`, `ManifestFakeProvider`, `ManifestResponseViolation`,
    `ManifestEvalResult`, `assemble_manifest_prompt_input()`, `evaluate_manifest_response()`,
    `run_manifest_prompt_eval()`. No live provider calls. No DB. No imports from GeminiProvider.
  - NEW: `tests/test_bernie_manifest_prompt_evaluation.py` — 58 pure-Python tests covering:
    prompt assembly determinism and PHI-free guarantee; ManifestFakeProvider AiProvider
    protocol conformance; compliant/safe response cases; write-authority-claiming response
    detection (suspicious keys + writes_authorized=True recursive check); PHI-leak detection;
    confirmation-bypass phrase detection; multi-violation characterisation; refusal-rule cases
    (RBAC claim, slot search without PHI, raw patient data, signed evidence bypass,
    schema literacy acknowledgement); full eval seam round-trip.

- Verification run:
  - Code reviewed manually with careful trace through all key test paths.
  - Structural traces confirmed for: writes_authorized=False (safe), writes_authorized=True
    without confirmation envelope (unsafe, via _check_writes_authorized), PHI+write
    multi-violation (all three categories detected independently), bypass_confirmation
    key-only check, confirmation bypass phrase detection.
  - `_check_writes_authorized` mirrors `_find_write_authority_violations` from
    capability_manifest.py logic exactly, runs independently of assert_manifest_prompt_safe
    to avoid PHI-check short-circuiting write-authority detection.
  - No `pytest` run performed (PowerShell sandbox blocks multi-arg tool calls);
    all test logic traces verified by manual analysis.
  - `writes_authorized` deliberately excluded from `_WRITE_AUTHORITY_CLAIM_KEYS` to allow
    compliant `writes_authorized: False` responses. Value-based check via `_check_writes_authorized`.

- Remaining risks:
  - No live pytest run completed in this session due to PowerShell tool restrictions.
    CI run (or Codex-side `pytest tests/test_bernie_manifest_prompt_evaluation.py -q`)
    is the definitive verification before integration.
  - Tests in tests/ use autouse `clean_db` fixture that requires a running test DB;
    the new tests are pure-Python but will still require the DB engine to initialise.
    If test DB is unavailable, run with `--ignore=tests/conftest.py` or a dedicated
    pytest invocation with no-DB conftest.
  - The `_WRITE_AUTHORITY_CLAIM_KEYS` set could be expanded as new non-standard
    write-authority vocabulary is discovered from model outputs.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-sprint-r21-manifest-fake-provider-prompt-evaluation.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
