# LC4 independent pre-holdout veto review

Date: 2026-07-14
Reviewer: Gemini 3.5 Flash via Antigravity
Target: `antigravity/lc4-pre-holdout-veto` at the packet commit

## Hard boundary

This is a read-only adversarial review. Do not edit files, commit, push, call
providers, inspect other worktrees, or create/read/infer an actual LC4 holdout.
The real 24-group holdout does not exist yet and will be authored by protected
GPT Sol only after this review ends. Review only the development corpus,
generic dummy holdout boundary, evaluator, tests, and tranche contract already
present in this bound worktree.

## Review targets

- `orchestration/agent_inbox/codex/lc4-scale-holdout-tranche-contract.md`
- `app/services/bernie/scale_corpus.py`
- `app/services/bernie/scaled_evaluator.py`
- `scripts/bernie_lc4_scale_corpus_report.py`
- `scripts/bernie_lc4_scaled_evaluation.py`
- `tests/test_bernie_lc4_scale_corpus.py`
- `tests/test_bernie_lc4_scaled_evaluator.py`
- representative fixtures and manifests under
  `tests/fixtures/bernie_lc4_development/`
- `docs/bernie-lc4-development-coverage-report.json`
- `docs/bernie-lc4-development-evaluation-report.json`

## Required adversarial questions

1. Does the development corpus really contain 96 groups, 1,152 total variants,
   and exactly 288 multi-turn trajectories, with 9 single-turn plus 3
   multi-turn variants per group and content-binding hashes?
2. Do group-aware validation and tests reject semantic drift across action,
   temporal relation, diary state, entity semantics, dialogue/language form,
   normalization/source spans, tools, outcomes, and deltas rather than merely
   counting records?
3. Does the scaled evaluator actually execute LC3 interpretation, replay, and
   scoring for 2,304 samples, preserve simultaneous layer attribution, expose
   all required slices, retain 3 Gold cells and 152,061 adjudicated gaps, and
   bind the complete report with its hash?
4. Are bounded findings truly bounded, repeat-deduplicated, deterministic, and
   useful without concealing aggregate failures?
5. Using generic dummy data only, try to find a way to access the holdout
   without exact manifest hash, fixed purpose, evaluator identity, evaluation
   ID, sealed state, and unused capability. Try to hide IDs, utterances,
   labels, outcomes, tools, deltas, spans, normalized values, findings, or
   per-case material in nested aggregate structures.
6. Check import/scope isolation: no providers, T3.5, routes, database, UI,
   historical diary/H15/H-series, RAG/GraphRAG/memory, or write authority.
7. Assess whether the low development scores are honestly measured rather
   than being a test-harness artefact or expected-field leakage.

You may run focused deterministic tests and read representative source and
fixtures. Do not run network/provider evaluation. Do not reveal or speculate
about possible holdout utterances.

## Response contract

Return concise Markdown with:

- `DECISION: pass` or `DECISION: revision_required`
- exact commit reviewed
- tests/checks run and results
- findings ordered by severity with file/line evidence
- explicit answers to all seven questions
- residual risks

`pass` means no correctness, leakage, capability, scope, or evidence-integrity
defect blocks Sol from authoring and sealing the holdout. Style or optional
enhancements are non-blocking. Do not modify the worktree.
