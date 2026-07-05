# review-codex-codex-sprint-r24-deepseek-adversarial-provider-output-review

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/current` |
| Source Task | `codex-sprint-r24-deepseek-adversarial-provider-output-review` |
| Status | integrated |

## Review Request

codex-sprint-r24-deepseek-adversarial-provider-output-review ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - NEW: `orchestration/provider_output_adversarial_review.md` ? structured adversarial review artifact with 42 model-style sample outputs across 8 threat categories (frame-shape, write-authority vocabulary, PHI casing, availability synonyms, ambiguity-default synonyms, confirmation-bypass phrasings, nested write claims, multi-frame/list handling). Each sample includes expected violation kinds, rationale, and documented gap status.
  - NEW: `tests/test_adversarial_provider_outputs.py` ? 44 deterministic, no-DB pytest tests covering: 9 frame-shape detection checks, 6 write-authority coverage/detection-gap tests, 8 PHI casing/underscore gap tests, 6 availability synonym gap tests, 5 ambiguity-default gap tests, 5 confirmation-bypass phrasing gap tests, 3 nested write claim coverage tests, 3 multi-frame/list output handling tests.
- Verification run:
  - `python -m py_compile tests/test_adversarial_provider_outputs.py` ? clean.
  - `pytest tests/test_adversarial_provider_outputs.py -v` ? `44 passed` (0 failed, no DB needed).
  - Pre-existing tests unaffected (same DB-dependent errors as baseline).
- Remaining risks:
  - WA-5 (capital W write claim): the `_check_writes_authorized` case-sensitivity gap is the highest-severity finding ? a capital `W` in `Writes_Authorized` bypasses both the key-set check (lowered `writes_authorized` deliberately excluded from banned set) and the structural check (`.get("writes_authorized")` is case-sensitive). Verified experimentally: `safe=True` even with `Writes_Authorized: True` when `writes_authorized: False` satisfies the schema.
  - PHI casing gap (PH-1 through PH-4): PascalCase/camelCase PHI keys like `DateOfBirth`, `MedicareNumber`, `PatientID` are invisible after lowering because `_PHI_KEY_PATTERNS` uses underscore-separated names. Set intersection is exact-match, so `medicarenumber` ? `medicare`.
  - Multi-frame/list (ML-1): `evaluate_manifest_response` crashes with AttributeError/TypeError on `list[dict]` input. A provider that returns multiple frames per turn cannot be evaluated by the current single-dict entry point.
  - All gaps documented with test evidence; none are production code changes.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/codex/codex-sprint-r24-deepseek-adversarial-provider-output-review.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result: Integrated selectively. Ariadne used the worker's bypass findings to harden the evaluator and added passing R24 dry-run gate tests rather than merging tests that expected unsafe outputs to pass.
- Follow-up required: Use observed provider dry-run samples to extend phrase/key detectors before live prompt wiring.
