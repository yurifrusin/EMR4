# LC4 DW2 bounded evaluator revision packet

Date: 2026-07-14
Owner: DeepSeek 4 Flash / high, disposable DW2 worktree only
Protected orchestrator: GPT Sol

## Workspace preflight

- Work only in `C:\Users\sarashera\EMR4-worktrees\lc4-dw2`.
- Expected branch: `codex/lc4-dw2-scaled-evaluator`.
- Expected source commit: `762f01aa6938ad6c06da77e7d278813dc34afc8d`,
  with only this protected-orchestrator packet commit on top at dispatch.
- The worktree must be clean at dispatch.
- Do not read or create any actual LC4 holdout fixture, label, utterance, or result.
- Do not edit routes, providers, database code, UI, historical diary material, T3.5 adapters, or write authority.

This is a bounded revision of your existing DW2 implementation. Preserve its honest development results and its successful reuse of LC3 interpretation/replay/scoring.

## Required corrections

### 1. Actually bound development findings

`build_bounded_findings` currently serializes all 2,304 samples. That violates the tranche contract and creates an 85,925-line report.

- Set an explicit maximum of 96 findings.
- Deterministically select useful failures across the corpus rather than taking an order-dependent prefix. Deduplicate the two deterministic repeats and include no more than one finding per scenario.
- Preserve coverage across failure layers and the required critical slice dimensions as far as the available failures allow; document the deterministic selection policy in report metadata.
- Report `case_findings_limit`, `case_findings_included`, `case_findings_omitted`, and the selection policy.
- Tests must prove the cap, repeat deduplication, deterministic/shuffle-stable selection, and correct omitted arithmetic. Remove the test that requires one finding per sample.

### 2. Make the report hash authority-bearing for the report evidence

The current hash covers only corpus hash and aggregate passed/failed counts. A mutation to dimensions, slices, variance, lattice, or findings therefore goes undetected.

- Build the report first without `report_hash`, then compute SHA-256 over the canonical complete report payload and insert the hash.
- Provide a public validation helper that recomputes and rejects a mismatched report.
- Test mutations to each major section: manifest/partition, per-dimension evidence, critical slices, variance, bounded findings, and lattice. Every mutation must invalidate the hash.
- Prove exact regeneration and deterministic shuffle stability without weakening content binding.

### 3. Fail closed independent of Python optimization

Replace the production `assert` checks for exact scenario/sample counts and repeat contract with explicit `ValueError` checks. Validate `repeats == 2` before evaluation. Add negative tests.

### 4. Harden the generic sealed-holdout boundary using dummy data only

- The purpose must be exactly `sealed_baseline_evaluation`; it must not be caller-configurable to another matching string.
- Reject blank/malformed manifest hashes, evaluator identities, and evaluation IDs; the supplied expected evaluator/evaluation ID must match the sealed receipt as well as the manifest hash.
- Single use must only be consumed after every credential check passes.
- Holdout report validation must use a strict recursive allowlist/schema. Reject unknown nested keys, non-aggregate nested structures, identifier/utterance/expected/observed/tool/delta/span/normalized/finding/per-case key aliases case-insensitively, and forbidden strings at any nesting depth including tuple/list values.
- Hash a sanitized holdout aggregate report over its complete payload excluding `report_hash`, and provide validation tests.
- Use generic dummy names only. Do not infer or inspect the actual holdout.

### 5. Evidence and artifact

- Regenerate `docs/bernie-lc4-development-evaluation-report.json` exactly. The bounded report should be materially smaller while preserving all aggregate scores, slices, variance, and the `3 Gold / 152,061 adjudicated gaps` baseline.
- Update tests with real adversarial mutations, not tautological assertions.
- Run:
  - `C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_bernie_lc4_scaled_evaluator.py -q --tb=short`
  - `C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts/bernie_lc4_scaled_evaluation.py --check`
  - `git diff --check`
- Commit only your owned revision files. Do not push or integrate.
- Write the durable completion artifact at `orchestration/agent_inbox/codex/lc4-dw2-scaled-evaluator-revision-completion.md` with exact commit, files, tests, report size/hash, retained aggregate counts, remaining limitations, and `DECISION: complete` or `DECISION: revision_required`.

The artifact is the authority-bearing worker result. Terminal prose is not.
