# Ariadne Antigravity Gemini 3.6 Flash/high verifier allocation

Date: 2026-08-03

Status: authorised

## Decision

Gemini 3.6 Flash at Antigravity's highest exposed reasoning level (`high`) is
the preferred independent verifier. The exact stable model slug is
`gemini-3.6-flash-high`. Each review starts in a fresh Antigravity project bound
to one clean, non-protected task worktree.

The verifier owns a genuine fresh-context veto surface: code and diff review,
adversarial security review, independent test design and reproduction of
repository-local or authored-synthetic evidence. It is not a routine
implementation worker or a second conductor.

## Controls

- The launcher passes both the stable model slug and explicit `--effort high`.
- The launcher uses plan mode and requires the candidate HEAD and worktree to
  remain unchanged after review.
- The verifier must return exactly one terminal `pass` or `revision_required`
  decision; missing or duplicated decision envelopes fail closed.
- Print-mode model resolution must fail closed; no silent fallback is allowed.
- The packet names the exact root, branch, source head, owned review artifact,
  forbidden surfaces, tests and required `pass` or `revision_required` result.
- The verifier cannot accept its own implementation, integrate, move the baton,
  push protected refs, deploy or release.
- Protected holdouts, historical Diary material, patient/clinical or other
  product-derived data and provider/product credentials remain excluded.
- Sol remains the architecture, acceptance, recovery and integration owner.

## Live capability observation

The installed `agy` CLI listed `gemini-3.6-flash-high` and exposed only
`low`, `medium` and `high` reasoning effort, making `high` the exact maximum.
This was a capability query only; no model inference call was made.

## Rollback

If the exact model is unavailable or quota-bound, stand the verifier down and
record reduced independence. Do not silently substitute Gemini 3.5 or another
provider. Any replacement requires a conductor replan and a fresh receipt.
