# LC4 pre-holdout independent veto review

Date: 2026-07-14
Reviewer: Gemini 3.5 Flash (High) through the bound-worktree Antigravity wrapper
Protected orchestrator: GPT Sol

## Decision

`DECISION: pass`

No correctness, leakage, capability, scope, or evidence-integrity defect blocks
Sol from authoring and sealing the 24-group protected holdout. The holdout did
not exist during either review call.

## Receipt and provenance chain

The first wrapper receipt bound the substantive review to clean commit
`d8ad334830e3090f2f7a07323e12bfd23be95c41` before and after execution. Gemini's
inline review returned `DECISION: pass`, reported 76 corpus tests and 94 scaled
evaluator tests passing, and answered all seven adversarial questions. Its prose
mistyped the reviewed SHA even though the wrapper receipt contained the correct
value, so Sol did not accept the prose as exact provenance.

A bounded correction call ran at clean commit
`06f3611d7009ffa27530963e81a6c2e76c58c786`. Its wrapper again recorded identical
before/after SHAs and a clean worktree. Gemini verified that exact SHA, the empty
porcelain status, and the real report scripts:

- `scripts/bernie_lc4_development_report.py`
- `scripts/bernie_lc4_scaled_evaluation.py`

The correction stated that the substantive findings, answers, and residual
risks did not change. Antigravity also referenced a polished artifact in its
private tool-state directory; that out-of-worktree file is deliberately not an
authority-bearing project artifact and was not used for acceptance.

## Adversarial conclusions

Gemini independently concluded that:

- the development corpus has exactly 96 groups, 1,152 variants, and 288
  multi-turn trajectories, with nine single-turn plus three multi-turn variants
  per group and content-binding hashes;
- group-aware validation rejects semantic drift rather than merely validating
  record counts;
- the evaluator executes two deterministic LC3 interpretation/replay/scoring
  samples for every variant, preserves simultaneous failure layers, binds the
  complete report, and keeps the three Gold cells and 152,061 adjudicated gaps;
- the 96 development findings are bounded, repeat-deduplicated, deterministic,
  and do not conceal aggregate failures;
- the generic holdout capability fails closed on manifest, purpose, identity,
  evaluation ID, seal, or single-use mismatch, while nested output validation
  rejects case-level leakage;
- provider, T3.5, route, database, UI, historical-diary, memory/RAG, and write
  surfaces remain outside the tranche; and
- the 0/2,304 complete-pass result represents measured capability gaps, not
  expected-field leakage or an evaluator that cannot produce a pass.

Sol independently reran the 76 corpus tests, the 94 evaluator tests, both exact
report checks, and diff checks before accepting this review chain.

## Residual risks

The present deterministic interpretation path performs very poorly across the
larger Silver/pending corpus. That is the evidence LC4 is intended to expose,
not a reason to tune against or inspect the protected holdout. Provider adapters
remain deferred until the language bridge is credible and a later user-approved
gate opens T3.5 work.
