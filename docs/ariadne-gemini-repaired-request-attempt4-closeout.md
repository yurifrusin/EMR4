# Ariadne Gemini Repaired-Request Rehearsal — Attempt 004 Closeout

Date: 2026-07-24
Owner: GPT Sol
Result:
`ariadne_gemini_repaired_request_attempt4_revision_required`

## Outcome

Attempt 004 consumed its distinct Gemini single-use ledger and made exactly one
`gemini-3.5-flash` Developer API `generateContent` request through the repaired
shared request constructor. Google returned HTTP 400 `INVALID_ARGUMENT` before
presenting a typed candidate.

The provider schema, full release schema and deterministic proofreader were
therefore not reached. No retry, fallback, model substitution, Terra/OpenAI
call, cross-model input, tool use, vote or downstream delivery occurred.

Removing `candidateCount` did not make this exact request acceptable. Because
the audit policy intentionally excludes the provider's free-form error message
and raw response, the exact remaining rejected field or constraint is not
proved by this attempt.

## External audit

The independently read durable audit passes as
`ariadne_gemini_attempt4_external_audit_pass`:

- one broker-ready event;
- exactly one provider-call start;
- exactly one provider-call completion;
- HTTP 400 / `INVALID_ARGUMENT` / numeric code 400;
- no typed-output manifest;
- no schema or proofreader disposition;
- a complete durable SHA-256 chain; and
- complete work-cell, broker, private-network and Gemini image-tag cleanup.

Unlike the original attempt-003 sanitized copies, the attempt-004 durable
events revalidate directly. The fail-closed exporter retained every allowlisted
hashed field.

## Containment

Only the sealed authored-synthetic task entered the work cell. The broker alone
received `GEMINI_API_KEY`. No credential, prompt, raw provider response, draft
value, hidden reasoning or arbitrary provider message was retained.

No PostgreSQL or other database, product API or product data, event feed, live
mailbox, EMR command, PII, protected holdout, historical Diary material,
production, deployment or release surface was accessed. Post-run inspection
found no attempt-004 container, network or image-tag residue.

## Residency finding

This attempt used the direct Gemini Developer API endpoint
`generativelanguage.googleapis.com`. It is not evidence of Australian-local
processing. Google's current Gemini API terms permit paid-service prompts and
responses to be stored transiently or cached in any country where Google or
its agents maintain facilities.

Google's separate Gemini Enterprise Agent Platform documentation now lists
`gemini-3.5-flash` as supported for ML processing through the Sydney
`australia-southeast1` location and says locational endpoints keep processing
within the associated country jurisdiction. That route requires a separate
Vertex/Google Cloud authentication, project, billing and data-location tranche;
it was not used or authorised here.

OpenAI's current API data-residency table offers Australian regional storage
through `au.api.openai.com`, but not Australian regional processing. The
announced OpenAI/NEXTDC sovereign-compute partnership is therefore strategically
relevant but does not change the present API processing contract.

## Verification

- provider-free real-isolation preflight: passed;
- Gemini credential-presence gate: passed without recording a value;
- focused contract/audit suite: 43 passed;
- fixed repository-only population: 266 passed;
- static validation, Python compile and Ruff: passed;
- durable audit revalidation: passed;
- Docker residue inspection: empty.

## Continuing gate

The attempt is consumed and is not retried under this plan.

A provider-blocked diagnostic that retains a separately reviewed bounded error
detail, another direct Gemini call, migration to the Interactions API, or an
Australian Vertex route each requires a new exact plan and authority. PII,
database copies, product/runtime wiring and a durable practice-scoped audit
sink remain separately closed.
