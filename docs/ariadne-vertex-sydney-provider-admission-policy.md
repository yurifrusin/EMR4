# Ariadne Sydney Vertex Provider-Admission Policy

Date: 2026-07-24
Owner: GPT Sol
Evidence class: official-provider-contract plus independently inspected
repository observation
Decision: `ariadne_vertex_sydney_provider_admission_blocked`

## Purpose

This provider-neutral policy decides whether a named model/provider route may
enter an occupied Ariadne work cell. Passing requires every data,
geography, identity, endpoint, retention, audit, isolation and cost condition.
One missing condition blocks the route without fallback.

The machine-readable source is
`orchestration/continuity/ariadne-vertex-sydney/provider-admission-policy.json`.

## Data classification

- **Authored-synthetic:** deliberately created for the rehearsal and not
  derived from EMR4, patients, practices, historical material, protected
  evidence or an external corpus. This is the only admissible class.
- **Product-derived:** copied, transformed, summarized or inferred from product
  state, databases, logs, audits or operational traffic. Rejected.
- **Patient or health information:** identified, identifiable, pseudonymized or
  real patient, clinical, appointment, contact, Medicare or practice
  information. Rejected.

## Geography and evidence

- **Australian regional processing** means the provider's contractual
  commitment that ML inference processing stays within the country
  jurisdiction associated with the exact `australia-southeast1` locational
  endpoint. It is not a claim that a particular building, zone, sovereign
  facility or personnel boundary was independently observed.
- **Regional storage** concerns data intentionally stored at rest in a selected
  location. It is separate from inference processing. No provider storage,
  explicit cache or retained prompt/response is authorised here.
- **Global endpoints** can route and process globally and provide no regional
  isolation or residency guarantee. They are always rejected.
- **Container isolation** constrains the model-facing process's local
  capabilities. It does not determine the remote provider's processing
  geography.
- **Independent observation** records what the official pages and their
  per-model table cells show. **Provider-contractual evidence** records the
  provider's stated processing, storage, training and retention commitments.
  Neither is project entitlement or an observed provider request.

## Provider controls

Google's current terms state that customer data is not used to train or
fine-tune managed models without prior permission or instruction. No such
permission is granted.

Google also states that prompts can be logged for abuse monitoring for
customers in scope unless an exception applies, and that some advanced
features can have additional retention. This rehearsal therefore remains
authored-synthetic and makes no zero-data-retention claim.

Request-response logging is disabled by default but can be configured. A later
preflight would have to confirm it is disabled or absent for the exact project
and model before content transmission.

Google separately documents that published Gemini models cache inputs, outputs
and derived customer data in memory by default, isolated at project level with
a 24-hour TTL and not at rest. Because Yuri authorised no cache creation, a
later preflight must verify that in-memory caching is disabled for the exact
project. If the read needs broader permission or caching is enabled, the
sequence must stop for Yuri; this authority does not permit changing the
project setting.

## Exact route

The only potentially admissible route is:

- provider: Google Vertex AI;
- model: `gemini-3.5-flash`;
- project: `bernie-emr4-dev`;
- service account:
  `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com`;
- authentication: `keyless_impersonated_service_account_adc`;
- location: `australia-southeast1`;
- hostname: `australia-southeast1-aiplatform.googleapis.com`; and
- automatic fallback: false.

Developer API, `generativelanguage.googleapis.com`, global Vertex, API/static
keys, automatic fallback, OpenAI, Terra, DeepSeek, another provider, model
family, project, identity or region are rejected.

## Current official finding

Google's current Gemini 3.5 Flash model card resolves the stable model ID as
`gemini-3.5-flash`, identifies it as GA and supports structured output. Its
published model-availability and ML-processing regions omit
`australia-southeast1`.

Google's current per-model data-residency matrix likewise leaves the Australia
column unsupported for Gemini 3.5 Flash. The regional Vertex service hostname
exists, but endpoint existence is not model support.

Therefore the exact route is blocked before ADC inspection, entitlement
preflight, container launch or provider contact. Tranches 2-7 do not open.

## Claim boundary

This evidence proves the published GA identifier, the existence of the regional
service hostname, the provider's general locational/global endpoint contract
and the exact documentary model-location gap.

It does not prove project entitlement, ADC usability, provider request
acceptance, inference, a typed draft, proofreader behavior, Australian physical
processing, Australian sovereign processing, zero data retention or the
project's in-memory cache setting.

## Official sources

- [Gemini 3.5 Flash model card](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-5-flash?hl=en)
- [Model data residency](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/data-residency?hl=en)
- [Model lifecycle](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/model-versions?hl=en)
- [Zero data retention and abuse monitoring](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/zero-data-retention?hl=en)
- [Vertex/Agent Platform service endpoints](https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/rest)
- [Google Cloud Service Specific Terms](https://cloud.google.com/terms/service-terms)
