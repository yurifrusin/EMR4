# Fresh Gemini adversarial review packet

Role: independent red verifier only

Model/effort: exact `gemini-3.6-flash-high` / explicit `high`

Candidate branch: `codex/review-ariadne-handover-verifier-red`

Review-projection HEAD: `f5c81243a34b17cd65cc9cb20822aa80e0eaefc8`

Task candidate HEAD: `50b11485d73ea8ee6660d1070890302c755af398`

Baseline HEAD: `167618a9806cfb5431f0c55ddaa4dcef5b51e8b6`

## Authority and independence

Review only in the exact bound worktree. Do not edit, create, delete, stage,
commit, push or deploy. Do not use any prior Antigravity project or read any
prior review artifact, including the parallel DeepSeek result. Do not access
protected refs, patient/clinical/product-derived data, protected holdouts,
historical Diary material, credentials or `docs/branding/`. This is
repository-local security-control evidence only.

The review projection has the exact task candidate's live handover, ledger,
settings, implementation and tests, but deliberately excludes the parallel
blue-review packet, analysis and receipts. Sol verified no diff across those
source/control paths and the same stable settings fingerprint
`sha256:71b4cdb0e461a900b76517a1744dd5ef45a59b2b44a478d1fb245842dc7786b9`.

## Adversarial focus

Attempt to falsify the candidate's claims:

- find a way for a missing, empty, malformed or ambiguously prefixed source to
  yield a passing five-source receipt;
- find an allowed continuation event that evades five-source enforcement;
- find a ledger/manifest edit, omitted row or live/index authority ambiguity
  that the tests fail to detect;
- find a policy path that permits model review before deterministic gates,
  implementation by the Gemini lane, self-acceptance, silent model fallback or
  parallel PostgreSQL pytest;
- identify stale statements, unsafe scope expansion or a branding/protected-ref
  collision in the exact diff.

Review the exact diff from
`167618a9806cfb5431f0c55ddaa4dcef5b51e8b6` to the projection HEAD. You may run
the seven focused pytest files named in the plan and any read-only static reproduction
needed for a concrete finding. Do not inspect prior review outputs.

## Required response

List findings first with severity and precise file/line evidence. If none,
state that explicitly. Name checks actually run and confirm the exact HEAD and
clean unchanged worktree. End with exactly one terminal line:

`DECISION: pass`

or

`DECISION: revision_required`
