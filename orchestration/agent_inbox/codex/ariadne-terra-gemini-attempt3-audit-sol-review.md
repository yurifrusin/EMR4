# Ariadne Terra/Gemini Attempt 003 Audit — Sol Review

Date: 2026-07-24
Reviewer: GPT Sol
Decision:
`ariadne_terra_gemini_comparative_rehearsal_attempt3_revision_required`

The authorised attempt was bounded and correctly consumed: one Terra call,
complete teardown, then one Gemini call, with no retry or fallback. Terra
returned five typed authored-synthetic drafts that passed both schemas and the
deterministic proofreader. Gemini returned HTTP 400 `INVALID_ARGUMENT` before
any typed candidate.

The audit mechanism materially succeeds at showing which typed “keys” Terra
pressed: provider contact, request/response hashes, five draft identifiers,
ports, types, field names, hashes and the host proofreader disposition are
visible without exposing draft values or hidden reasoning. It also proves the
Gemini one-call rejection and both cleanups.

Acceptance is nevertheless withheld for two independent reasons:

1. Gemini presented no candidate, so there is no two-model comparison.
2. The original sanitized durable event copies omitted four hashed
   `broker-ready` fields and were not independently self-verifying.

The second issue is preserved as an immutable audit incident. A separate
deterministic reconstruction proves both original live chains, and the future
export allowlist is corrected. This does not change the attempt result.

No retry, provider call, container start, diagnostic disclosure expansion,
product connection or durable audit-store authority follows from this review.
