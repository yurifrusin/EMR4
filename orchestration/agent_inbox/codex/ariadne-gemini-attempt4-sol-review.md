# Sol Review — Ariadne Gemini Repaired-Request Attempt 004

Date: 2026-07-24
Decision:
`ariadne_gemini_repaired_request_attempt4_revision_required`

I accept the containment and external-audit evidence, but not a generated-draft
or proofreader claim.

The distinct ledger was consumed exactly once. Gemini returned HTTP 400
`INVALID_ARGUMENT` before a candidate, so no provider schema, full schema or
proofreader gate ran. The repaired request is therefore still not admitted.
No retry or fallback occurred.

The durable attempt-004 audit independently verifies one call, one completion
and complete cleanup, without credentials, prompts, raw responses, draft
values or hidden reasoning. It passes separately as
`ariadne_gemini_attempt4_external_audit_pass`.

The direct Gemini Developer API route carries no Australian-processing claim.
Any future clinical-data route must separately prove an eligible
Australia-bound Vertex endpoint and all applicable privacy, contractual and
product controls.
