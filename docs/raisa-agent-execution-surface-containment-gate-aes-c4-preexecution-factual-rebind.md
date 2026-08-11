# AES-C4 preexecution provider-fact rebind

Date: 2026-08-11

Status: `rebound_before_inference_fresh_exact_head_veto_required`

## Observation

The preexecution public-source recheck found that Google had updated the
published facts used when the AES-C4 envelope was first frozen:

- the current Gemini 2.5 Flash model page and current model-lifecycle table
  give `gemini-2.5-flash` a retirement date of 2026-10-20, extending the
  earlier 2026-10-16 date retained in an April release-note entry; and
- current Standard pricing is USD 0.30 per million input tokens and USD 2.50
  per million text-output tokens including reasoning, replacing the earlier
  split values recorded in the plan.

The current model page still records launch stage GA and includes
`australia-southeast1` in both model availability and ML processing. No
provider prompt or inference call occurred before this rebind.

Authoritative pages rechecked:

- <https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/2-5-flash>
- <https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/model-versions>
- <https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing>
- <https://docs.cloud.google.com/vertex-ai/generative-ai/docs/release-notes>

## Disposition

The provider, model, project, identity, region, data, one-call/no-retry rule,
USD 0.25 application ceiling and all containment boundaries remain unchanged.
The updated unit prices still put a deliberately overestimated maximum bounded
request below USD 0.008. This document, plan, envelope, enforcement and tests
therefore rebind only current public facts; they do not broaden provider or
cost authority.

The prior exact-head veto remains valid evidence for its reviewed source but
cannot admit the rebound source. Regenerate a distinct provider-free zero-call
ledger and obtain a fresh exact-head veto before repeating cloud/ADC/CLI checks
or opening the sole occupied ledger.
