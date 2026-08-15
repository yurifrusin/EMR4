# Ariadne Antigravity Gemini 3.7 Flash/high verifier allocation

Date: 2026-08-15

Timestamp: 2026-08-15T15:57:19+10:00 (Australia/Brisbane)

Status: `active_direct_user_allocation`

## Decision

Yuri directly replaces the preferred independent Antigravity verifier with
Gemini 3.7 Flash/high. The exact model slug is `gemini-3.7-flash-high` and the
reasoning effort is explicitly `high`.

The installed `agy` 1.1.13 CLI advertised the high, medium and low Gemini 3.7
Flash slugs on 2026-08-15. No provider/model call was used for that observation.
Yuri expressly declined a separate trial or transition gate: the model enters
ordinary exact-candidate veto work immediately, and operational problems are
handled through the existing fail-closed review workflow as they arise.

## Runtime allocation

- Live resource id: `antigravity-gemini-flash-3-7-high-verifier`.
- Default and requested model: `gemini-3.7-flash-high`.
- Effort: `high`.
- Project: fresh for every review.
- Worktree: exact named non-protected clean read-only candidate.
- Decision: one schema-constrained `pass` or `revision_required` envelope.
- Candidate postcondition: unchanged HEAD and clean worktree.
- Fallback: none silently. Gemini 3.6 slugs remain launcher-compatible only for
  historical receipts or a future explicit user selection.

The current delete-confirm physical-design veto is the first ordinary 3.7 High
use. This allocation change itself makes no claim about comparative model
quality and creates no extra acceptance authority.

## Authority boundary

Gemini remains an independent reviewer only. It may inspect exact non-protected
repository code, diffs, tests and authored-synthetic evidence and may execute
only an exact deterministic command manifest. It receives no implementation,
self-acceptance, integration, baton, protected-ref, patient/clinical/product
data, provider-product, credential/IAM, deployment, production, release or
Pages authority.
