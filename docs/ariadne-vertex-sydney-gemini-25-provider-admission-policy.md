# Ariadne Sydney Vertex Gemini 2.5 Flash — Provider Admission

Date: 2026-07-24
Decision:
`ariadne_vertex_sydney_gemini_25_provider_admission_pass`

Current official Google documentation publishes `gemini-2.5-flash` as a GA
model ID, supports structured output, and explicitly lists
`australia-southeast1` for both model availability and ML processing. The
published retirement date is 2026-10-16; Yuri accepted that short runway only
for this one bounded authored-synthetic rehearsal.

Google's locational-endpoint contract says ML processing remains within the
associated broader multi-region or country jurisdiction. Global endpoints
provide no regional isolation or residency guarantee. This admission therefore
permits only the exact Sydney hostname and makes no claim of independently
observed physical or sovereign locality.

Authored-synthetic content is the only admitted data class. Product-derived,
patient/health, practice, historical, protected and external-corpus content
remain rejected. A container constrains local capabilities but cannot determine
remote provider geography.

Training controls, abuse-monitoring retention, request-response logging and
provider-managed in-memory caching remain distinct. Provider training controls
and abuse-monitoring retention were not independently verified by this
documentary tranche; only authored-synthetic content is admitted and no
zero-data-retention claim is made. Google documents
project-isolated, not-at-rest, 24-hour in-memory caching as enabled by default.
The later read-only control preflight must prove it disabled for
`bernie-emr4-dev` or stop for Yuri; this authority does not permit changing the
setting.

The admission rejects the Developer API,
`generativelanguage.googleapis.com`, global Vertex, cross-region fallback,
API/static keys, another Google model, OpenAI, Terra, DeepSeek, another
provider/project/identity/region and any model without published Sydney
support.

This tranche proves current documentary model-location admission only. It
does not prove project entitlement, ADC usability, IAM/audit/logging/cache
posture, provider request acceptance, inference, typed output, proofreader
release, Australian physical processing or sovereign processing.

Official sources:

- [Gemini 2.5 Flash model card](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/2-5-flash?hl=en)
- [Model data residency](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/data-residency?hl=en)
- [Model lifecycle](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/model-versions?hl=en)
- [Zero-data-retention controls](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/zero-data-retention?hl=en)
- [Service endpoints](https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/rest)
