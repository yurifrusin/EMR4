# Gemini Synthetic Silver Robustness Baseline Review Packet

Date: 2026-07-17

## Binding

- Worktree: `C:\Users\sarashera\EMR4-worktrees\synthetic-silver-robustness-review`
- Branch: `codex/synthetic-silver-robustness-review`
- Exact source head: `ec3d32dca17b583b7e7f7f05939e235b43e2ff3a`
- Report hash:
  `sha256:18501cf5c8d28c0e660a9f5c7b15f7690622e44c90b248d51301c6ece03973c5`
- Candidate hash:
  `sha256:ae14c613ecdd87aac39201d44a8024f3b9216f871c7d5859c4249e7f4026c665`
- Model: Gemini 3.5 Flash through a fresh Antigravity project
- Role: independent exact-baseline reviewer and veto
- Acceptance/integration owner: GPT Sol

Read completely:

- `AGENTS.md`;
- `docs/bernie-synthetic-silver-robustness-baseline-contract.md`;
- `app/services/bernie/synthetic_noise_robustness.py`;
- `scripts/bernie_synthetic_silver_robustness_baseline.py`;
- `tests/test_bernie_synthetic_noise_robustness.py`;
- `docs/bernie-synthetic-silver-robustness-baseline-report.json`;
- `tests/fixtures/bernie_synthetic_noise/admission.json`;
- `tests/fixtures/bernie_synthetic_noise/semantic_seeds.json`; and
- `tests/fixtures/bernie_synthetic_noise/candidates_sol_recovery.jsonl`.

You may inspect the ordinary LC4 development sources only through the named
`DevelopmentOnlyLoader` path needed to verify the adapter. Do not read, list,
search, hash, import, run, infer, or otherwise access any protected V1-V10
fixture, support, manifest, seal, receipt, or case report. Do not use
historical diary or external corpus material.

## Task

Independently decide whether the exact baseline is valid evidence. In
particular, verify:

1. The admitted 192-candidate population and all input hashes bind exactly.
2. Candidate reconstruction preserves the ordinary-development semantic and
   diary oracle while replacing only synthetic dialogue/evidence and benign
   metadata.
3. `deterministic_interpret` receives only dialogue turns and reference date;
   no expected semantic, policy, replay, or delta field leaks into extraction.
4. The existing replay/scorer path is invoked without a product-code repair or
   evaluator-specific fallback.
5. All 192 candidates and 384 observations are evaluated, every failing
   candidate has exact per-case evidence, and no source utterance appears in
   the report.
6. The reported 2/192 complete candidates, dimension counts, primary
   diagnostic categories, zero repeat variance, and 384/384 safety pass
   reproduce.
7. `baseline_complete` is used only for evidence completeness and does not
   misrepresent the poor product result as a product pass.
8. The metadata-only protected-filename discovery incident is accurately
   contained and did not influence inputs, implementation, or results.

Do not repair parser/policy behaviour or edit the report. A conceptual flaw,
oracle leakage, incompleteness, protected access, non-reproducibility, safety
failure, or incorrect count requires `revision_required`.

Run:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\bernie_synthetic_silver_robustness_baseline.py --check
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_synthetic_noise_robustness.py tests\test_bernie_synthetic_noise_corpus.py tests\test_bernie_synthetic_noise_sol_recovery.py -q
git diff --check
```

Write only
`orchestration/agent_inbox/antigravity/synthetic-silver-robustness-baseline-review.md`,
commit it on the disposable branch, and do not push.

Forbidden: all protected or historical evidence, external corpora, live
providers, product runtime, parser/policy changes, routes, API, GraphQL,
database, UI, confirmation, write authority, deployment, release, Gold
promotion, certification, and every unowned file.

End exactly:

```text
DECISION: pass|revision_required
SOURCE_HEAD: ec3d32dca17b583b7e7f7f05939e235b43e2ff3a
REPORT_SHA256: sha256:18501cf5c8d28c0e660a9f5c7b15f7690622e44c90b248d51301c6ece03973c5
CANDIDATES: 192
OBSERVATIONS: 384
COMPLETE: 2
FAILED: 190
SAFETY_PASS: 384
VARIANCE: 0
PROTECTED_ACCESS: false
```
