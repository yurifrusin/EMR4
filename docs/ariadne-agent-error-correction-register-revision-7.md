# Ariadne agent-error register revision 7

Date: 2026-08-04

Status: recurring orchestrator error and verifier claim error corrected

## AER-0014: detached verifier worktree recurred

Root created the exact clean Gate -1 Gemini worktree at candidate
`b3c5208476642517b850dd6160a84869d605ca71` but left it detached. The local
Antigravity wrapper rejected the launch before project creation or any model
call. This repeats the exact `AER-0012` recurrence signature, so the earlier
prose-only prevention control was insufficient.

The same unchanged commit was placed on
`codex/review-model-required-bureau-gate-minus-one`. A new deterministic
`ariadne_verifier_worktree_preflight.py` control now checks exact HEAD, clean
status and a non-protected `codex/review-` branch before a pre-verifier receipt
may be issued. The verifier execution policy and tests make that ordering
explicit. This is an observed orchestrator output-contract error, not a claim
about Gemini or Antigravity quality.

## AER-0015: review transport was reported as zero-call candidate evidence

The first Gemini review returned one `pass`, zero candidate findings, unchanged
HEAD and a clean worktree. Its claims-not-established section nevertheless said
that no model invocation or external prompt transmission occurred. That is
accurate only for the reviewed candidate runtime. The review itself was a
Gemini invocation and transmitted the bounded source-only packet and candidate
context through Antigravity.

Root preserved the raw receipt hash and a sanitized exact failure record,
refused to admit the first decision, and kept the candidate unchanged. The
fresh correction packet must report two separate scopes:

- candidate runtime side effects and authorities; and
- development-review transport, model invocation and bounded source
  transmission.

It may not use an unqualified zero-call statement.

The fresh corrected review ran in the exact clean worktree at candidate
`2b62f040bcc1c300dca6fb730e0f986d22f3be85`. Gemini 3.6 Flash/high returned
one `pass`, 79 passing tests and zero findings without changing HEAD or the
worktree. Its accounting explicitly records zero candidate product/runtime
side effects and the non-zero Antigravity/Gemini development-review invocation
and bounded source-only transmission. That receipt supplies the missing
correction evidence, so `AER-0015` is now corrected; the rejected first decision
remains preserved and unadmitted.
