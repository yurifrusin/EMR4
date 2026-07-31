# Yuri Authority Delta — Gemini 2.5 Flash Sydney Reorientation

Date: 2026-07-24
Authority owner: Yuri
Repository custodian: GPT Sol
Authority status: active, conditional and bounded

## Decision

After the Gemini 3.5 Flash documentary admission gate failed closed, Yuri
explicitly directed:

> I think we can use Gemini 2.5 Flash instead so reorient the tranche work to
> that.

This is fresh authority to replace the selected model in the conditional
Sydney Vertex tranche sequence with the officially published model ID
`gemini-2.5-flash`. It does not alter the provider, project, identity,
credential class, region, endpoint, data class, isolation, audit, proofreader,
cost, retry, cleanup or stop boundaries frozen in
`docs/ariadne-vertex-sydney-bounded-work-cell-authority.md`.

## Exact reoriented binding

- provider: Google Vertex AI only;
- model: `gemini-2.5-flash` only;
- project: `bernie-emr4-dev`;
- target service account:
  `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com`;
- authentication: `keyless_impersonated_service_account_adc`;
- required permission: `aiplatform.endpoints.predict`;
- location: `australia-southeast1`;
- base URL:
  `https://australia-southeast1-aiplatform.googleapis.com`;
- data: authored-synthetic only;
- primary occupied call ceiling: one;
- conditionally eligible deterministic request-contract repair retry: one;
- absolute occupied call ceiling for this new descendant: two;
- application cost ceiling: USD 1;
- provider, model and regional fallback: prohibited; and
- product, database, clinical, patient, command, production, deployment and
  release authority: none.

The Gemini 3.5 Flash Tranche 1 result remains immutable
`ariadne_vertex_sydney_provider_admission_blocked`: it consumed zero provider
calls and grants no unused-call carry-forward. The Gemini 2.5 Flash sequence
uses a fresh Continuity descendant, fresh receipts and, if later gates pass,
fresh single-use occupied ledgers.

## Lifecycle interpretation

Historical T3R5 evidence records `gemini-2.5-flash` as GA and Sydney-supported
with a documented retirement date of 2026-10-16. Yuri's explicit model
selection authorises the short-lived model for this one bounded
authored-synthetic rehearsal despite the former T3R5 180-day product-foundation
preference. It does not select Gemini 2.5 Flash for product, production,
long-lived platform, promotion or post-retirement use.

Current official documentation must still confirm the exact model ID,
`australia-southeast1` model-location support and lifecycle before the next
gate opens.

## Unchanged stop boundaries

The sequence still stops for Yuri if existing impersonated ADC is unusable; an
interactive login, credential reconfiguration, API/billing/IAM/project/service
account change or broader permission is required; audit or logging controls
fail; in-memory caching is not verified disabled under the frozen no-cache
boundary; the exact model is not currently supported in Sydney; a global or
fallback endpoint, API/static key, other provider/model/identity/region,
non-synthetic data, higher cost, credential exposure, weakened isolation or
audit, unexpected external charge or broader authority would be required.

No external state may be changed to satisfy a failed gate.
