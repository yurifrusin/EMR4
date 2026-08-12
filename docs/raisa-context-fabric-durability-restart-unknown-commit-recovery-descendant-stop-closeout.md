# CF-D2 restart and unknown-commit recovery descendant stop closeout

Date: 2026-08-12

Result: `stopped_unproved_after_diagnostic_attempt_002`

Last accepted durability position: Continuity 243 / Compass 225 (CF-D1)

Reviewed runtime source:
`fe8313d224a92115aa31bea14f0cd3b14e4c9967`

## Outcome

The recovery descendant does not release a CF-D2 pass, crash/restart claim or
unknown-commit claim.

Phase A passed deterministic verification and a fresh exact-HEAD Gemini 3.6
Flash/high implementation veto. Diagnostic attempt 001 then passed all ten
setup preconditions and the exact position-one atomic delta before stopping at
`cfd2_r01_append_anchor_2`. Repository reconciliation identified a real
revision inconsistency: the second anchor ordinal was being called with
lifecycle revision two even though position one had advanced the checkpoint
only to revision one.

The one plan-authorised correction changed only that harness argument and its
expectations. The first correction review was rejected for command-manifest
drift. A genuinely fresh replacement review at exact source
`fe8313d224a92115aa31bea14f0cd3b14e4c9967` reproduced all nine literal
commands, including 95 focused CF-D2 tests and 223 register tests, and reported
zero P0–P2 findings with no runtime or external operation.

Immutable diagnostic attempt 002 then passed the same ten preconditions and
position-one delta but stopped again at `cfd2_r01_append_anchor_2` with
`unexpected_terminal_success`. Its evidence SHA-256 is
`c595cd56b5b9a24dfdecc77fe12d998d1f16d593a33142cc3e9e9deffe7f1d12`.
The exact owned container was removed and proven absent. `SIGKILL`, restart,
participant retry, provider, product-read, product-command and external-
network counts are all zero.

## Diagnosis boundary

The lifecycle-revision correction was a valid necessary correction but was not
sufficient. Diagnostic attempt 002 therefore falsifies the earlier sole-cause
claim. Repository-only inspection shows that the accepted anchor entry point
performs several subsequent fail-closed consistency checks, but the minimized
terminal envelope collapses them into the same nonzero/null-SQLSTATE result.
The remaining internal cause is unresolved. No narrower cause is guessed.

AER-0284 records the reasoning error at register revision 252. The immutable
attempt-001 and attempt-002 diagnostics remain failure evidence, not acceptance
evidence.

## Authority stop

The recovery descendant's two diagnostics and sole correction are consumed.
Its gate requires a passing diagnostic before full attempt 003, so attempt 003
is ineligible and was not run. No further CF-D2 probe, correction, crash run or
rerun is authorised. Key rotation and retention/purge remain dependency-
blocked because CF-D2 has not passed.

Yuri has authorised an independent workflow-incident diagnosis next. That
repository-only tranche will examine why the process produced repeated
ceremony without enough discriminating evidence and will implement a bounded
workflow simplification. It cannot reopen CF-D2 runtime or broaden any data,
provider, product, deployment or protected-ref boundary.

All real/product/patient/clinical data, operational database/source or watcher
access, provider use, credentials/IAM, server-log/WAL inspection, executable
tools or commands, reusable runtime, deployment, production, release, Pages
and protected refs remain closed. `docs/branding/` and all unrelated untracked
files remain preserved and excluded.
