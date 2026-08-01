# Ariadne Sydney Vertex Tranche 1 — Independent Audit

Date: 2026-07-24
Role: repository-read-only independent reviewer
Result:
`ariadne_vertex_sydney_tranche_1_external_audit_pass_with_closeout_revisions_required`

## Independent result

The fail-closed stop is correct. On 2026-07-24, current official Google Cloud
documentation published `gemini-3.5-flash` as a GA model ID but did not list
`australia-southeast1` among its model-availability or ML-processing
locations.

Google separately published
`https://australia-southeast1-aiplatform.googleapis.com` as a service
endpoint. Endpoint existence is not evidence that the named model is
available at that location. Google's current data-residency documentation says
locational endpoints bind ML processing to the associated country or
multi-region only for models supported there; global endpoints provide no
regional guarantee.

The provider-admission decision therefore correctly fails closed as
`ariadne_vertex_sydney_provider_admission_blocked`, consumes no occupied call,
and opens no successor tranche.

## Findings

1. The initial Continuity revision 30 and Compass revision 18 remained
   internally bound but still marked the descendant active. Durable closeout
   requires a synchronized increment recording the blocked result.
2. Google documents that published Gemini models cache inputs, outputs and
   derived customer data in memory by default, isolated at project level and
   not at rest, with a 24-hour TTL. The frozen no-cache boundary therefore
   requires a future preflight to verify caching disabled or stop for Yuri.
   This authority does not permit changing that project setting.
3. The repository validator proves schema, semantic and canonical-hash
   consistency. It trusts the frozen source observation and does not itself
   authenticate or refresh Google documentation. The audit independently
   checked the official sources and reproduced the three canonical hashes.
4. The exact project, service account, keyless ADC class, Sydney endpoint,
   authored-synthetic, isolation, audit, USD 1, 1+conditional-retry/2-call,
   no-fallback and stop boundaries are preserved. Historical Terra/Gemini
   nodes remain immutable.

## Exclusions

The reviewer made no file edit and accessed no credential, ADC, token, project
entitlement, Cloud control plane, container, prompt or provider runtime.

This evidence proves only the current documentary model-location gap and
internal artifact/hash consistency. It does not prove project entitlement, ADC
usability, provider acceptance, inference, Australian physical or sovereign
processing, zero data retention or the project cache setting.

## Official sources

- [Gemini 3.5 Flash model card](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-5-flash?hl=en)
- [Model data residency](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/data-residency?hl=en)
- [Service endpoints](https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/rest)
- [Zero-data-retention controls](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/zero-data-retention?hl=en)
