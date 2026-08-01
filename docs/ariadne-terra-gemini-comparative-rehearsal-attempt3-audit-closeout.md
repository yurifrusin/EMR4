# Ariadne Terra/Gemini Comparative Rehearsal — Attempt 003 Audit Closeout

Date: 2026-07-24
Owner: GPT Sol
Result:
`ariadne_terra_gemini_comparative_rehearsal_attempt3_revision_required`

## Outcome

Attempt 003 consumed both new single-use process ledgers in the authorised
order. No retry, fallback, model substitution, cross-model input, tool use,
vote or downstream delivery occurred.

Terra completed one `gpt-5.6-terra` Responses API request with HTTP 200. It
returned five typed drafts. The provider envelope and full release schema
both passed, and the deterministic proofreader released all five declared
edges: three to their typed downstream recipients and two to human gates. No
safe repair was needed.

After complete Terra teardown, Gemini completed one
`gemini-3.5-flash` GenerateContent request. Google returned HTTP 400 with the
allowlisted status `INVALID_ARGUMENT` and numeric code 400 before presenting a
typed candidate. The provider schema, full schema and proofreader therefore
were not reached. Because the raw provider error message is deliberately not
retained, the exact rejected request field is not proven. The consumed Gemini
lane is not retried.

## External audit finding

The live broker chains were valid when checked by the host. Terra recorded:

1. broker ready;
2. exactly one provider call started;
3. exactly one provider call completed with HTTP 200; and
4. one typed-output manifest covering five draft IDs, output ports, frame
   types, field names and draft hashes without draft values.

The host evidence records Terra's full-schema result and proofreader
disposition `release-verified-outputs`. Gemini records broker ready, exactly
one provider call, HTTP 400 / `INVALID_ARGUMENT`, no typed-output manifest and
no proofreader disposition. Both lanes record complete cell, broker, network
and image-tag cleanup.

A fresh regression found that the original durable sanitized copies omitted
four non-sensitive fields which participated in each `broker-ready` event
hash: `allowed_path`, `upstream_host`, `upstream_path` and
`maximum_provider_calls`. Consequently, the original durable copies could not
independently reproduce their first event hash even though live host
verification had passed.

The original attempt evidence remains unchanged. A separate audit analysis
reconstructs only those four values from frozen broker constants and the
comparison manifest; both complete chains then verify exactly. The durable
export allowlist now retains these fields for future attempts. This is closed
as `ariadne_terra_gemini_attempt3_external_audit_revision_required`, not
retrofitted to pass.

## Safety and containment

- Only authored-synthetic task data entered either work cell.
- The broker alone received each provider credential.
- No credential value, raw prompt, raw provider response, draft payload,
  hidden reasoning or arbitrary error message was retained.
- No PostgreSQL, product API, event feed, mailbox, EMR command, PII,
  protected/historical evidence, production, deployment or release surface
  was accessed.
- Both work cells, brokers, private networks and image tags were removed.

## Verification

- fixed repository-only verifier: 259 passed, with repository `conftest.py`
  and plugin autoload disabled;
- static protocol validation: passed without a provider call;
- attempt-003 real-isolation preflight: passed with no prompt transmission,
  no provider call and complete cleanup;
- Ruff: passed;
- Python compile: passed;
- Node syntax checks: passed;
- Bandit medium/high: passed;
- post-run Docker container and network residue checks: empty.

## Decision boundary

Attempt 003 proves that Terra can perform the bounded multi-output work and
that the existing deterministic proofreader can constrain and route its typed
results. It does not establish a Terra-versus-Gemini quality comparison
because Gemini produced no candidate.

Any Gemini diagnostic that retains or classifies more provider error detail,
request-contract repair, further provider call, or another model attempt
requires a fresh Yuri decision. A durable practice-scoped audit store and
product/runtime integration also remain separately closed.
