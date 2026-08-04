# Ariadne agent-error register revision 12

Date: 2026-08-04

Status: AER-0017 and AER-0019 corrected and independently accepted

Review 9 ran in a genuinely fresh Windows worktree at exact candidate HEAD
`063153b9a799b32d125084fb77134588c9a6ac76`. The A3/B3 audit JSONL checked out
with `eol: lf` and exact SHA-256
`27d665f162ead5ee70d9db9cb39500bbe621e63b5bc0168b91ec6fb43d82bcad`.
Provider-free acceptance passed, all 305 review tests passed, Ruff and both diff
checks passed, and the worktree remained clean and unchanged. Gemini 3.6
Flash/high returned one exact `pass` with no findings.

AER-0017 is therefore corrected: the provider-free finalizer reconciles the
parent ledger to exactly one reserved and consumed USD 0.25 call, emits exact
no-release terminal evidence, and stops before correction or Davida. Its
finalizer and acceptance make zero provider calls.

AER-0019 is also corrected: the scoped `.gitattributes` LF rule makes the
hash-bound A3/B3 JSONL checkout byte-stable in a fresh supported Windows
worktree, with a mechanical attribute/byte/hash regression. AER-0018 remains
contained as a rejected duplicate-decision envelope; it established no
candidate finding.

Revision 12 retains all 19 bounded incidents and has no open incident. The
register remains workflow-learning evidence only, not model/provider quality
scoring or autonomous fine-tuning.
