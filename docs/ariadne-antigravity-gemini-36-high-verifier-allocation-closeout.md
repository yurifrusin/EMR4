# Ariadne Antigravity Gemini 3.6 Flash/high verifier allocation closeout

Date: 2026-08-03

Decision: `accepted`

Terminal result: `antigravity_gemini_36_high_verifier_allocation_pass`

## Accepted result

The preferred Antigravity verifier is now the single resource
`antigravity-gemini-flash-3-6-high-verifier`, using the stable
`gemini-3.6-flash-high` model slug and explicit `high` effort. It runs in a
fresh project, binds one clean non-protected worktree, uses plan mode and fails
if the reviewed HEAD or worktree changes. Its declared capabilities exclude
implementation and its policy excludes self-acceptance, integration, baton and
protected-ref authority.

The launcher also fails closed unless stdout contains exactly one terminal
`pass` or `revision_required` decision. Explicit historical Gemini 3.5 aliases
remain parseable for backward compatibility but cannot replace or silently
fallback from the 3.6-high default.

## Independent evidence

The first fresh 3.6-high review returned no finding and left its candidate
unchanged, but its raw transport output duplicated the decision and gave
conflicting trailing test-count prose. It was classified
`revision_required`, preserved and not used for acceptance.

One bounded repair added deterministic single-decision admission and zero/two
decision tests. A second fresh 3.6-high project reviewed exact candidate
`b439fb5c3bacc20c9b5f664b3af9322cfcdcbd3f`, ran 25 focused tests, found no
issue, emitted exactly one terminal `DECISION: pass`, and left the candidate
HEAD and worktree clean and unchanged. The canonical receipt is
`orchestration/agent_inbox/antigravity/ariadne-gemini-36-high-verifier-allocation-repair-review-receipt.json`.

## Local verification

The launcher, allocation-schema, DeepSeek-economy, orchestrator-preflight and
live-handover compactness tests passed. Ruff, Python compilation, YAML parsing
and `git diff --check` passed. No model response or test result is treated as
product, provider-lane, clinical or production evidence.

## Boundaries and next work

No protected holdout, historical Diary, branding asset, patient/clinical or
product-derived data, product mutation, Microsoft connection, cloud/IAM
change, deployment, protected integration, Pages rebuild, production or
release action occurred. The provider-free Office lifecycle result is
unchanged. The next safe product candidate remains the separately
authority-gated architecture/composition review for a default-off native Diary
consumer of the same active-practitioner read.
