# Ariadne Sydney Vertex Gemini 2.5 Flash — ADC-Restored Continuation Closeout

Date: 2026-07-24
Result: `ariadne_vertex_sydney_gemini_25_cache_control_blocked`
Terminal gate: repeated Tranche 3

## Result

The prior ADC-preflight failure remains immutable. Yuri reported that the
exact Bernie impersonated ADC had been authenticated externally, so a distinct
continuation repeated the complete read-only Tranche 3 controls.

The restored `google.auth.default()` path now returned exact impersonated
credentials for project `bernie-emr4-dev`, target service account
`emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com` and the
cloud-platform scope, and refreshed non-interactively.

The same read-only preflight established:

- existing billing entitlement and enabled Vertex AI API;
- the exact enabled target service account;
- the exact prediction-only custom role and sole
  `aiplatform.endpoints.predict` permission;
- the exact project binding with no additional bound role;
- Vertex `DATA_READ` and `DATA_WRITE` audit logging;
- request-response logging disabled or absent;
- zero user-managed service-account keys;
- current `gemini-2.5-flash` publisher-catalogue presence;
- the exact Sydney endpoint and no automatic fallback; and
- no API-key or service-account-key authentication.

The first catalogue read exposed a repository-local preflight defect: it did
not bind the read request to the exact target quota project. A focused
read-only repair added the per-command target quota-project argument and a
regression test. It changed no Google Cloud configuration, billing, IAM,
project, service account, credential or provider state.

The terminal check did not verify an explicit `disableCache: true` value for
the exact project. The read-only result does not distinguish an enabled state
from an absent or otherwise non-explicit control response. The frozen admission
contract requires explicit cache disablement, and Yuri prohibited Codex from
changing that external setting. The continuation therefore failed closed
before Tranche 4.

## Gate accounting

| Gate | Result |
|---|---|
| 1. Provider/residency admission | inherited pass |
| 2. Provider-blocked contracts | inherited pass; focused catalogue-reader regression added |
| 3. Existing ADC/entitlement | ADC and all recorded controls passed except provider in-memory cache disablement |
| 4. Provider-free real isolation | not opened |
| 5. Occupied Vertex rehearsal | not opened |
| 6. Proofreader/release | not opened |
| 7. External audit/closeout | completed for this failed continuation |

No rehearsal prompt or model payload was transmitted. No provider data-plane
inference call was made. No single-use rehearsal or occupied ledger was
opened. No container, relay, broker server, task network or task image was
started. Occupied-call count and retry count remain zero, and model-call cost
is USD 0.

## Cleanup and residue

Independent task-scoped inspection reports zero containers, networks, images,
broker processes and temporary credential files. No runtime state required
teardown because the real-isolation gate never opened.

## What the evidence proves

The continuation proves that the exact restored Bernie impersonated ADC now
refreshes non-interactively and that the existing project, API/billing,
prediction-only role/binding/permission, Vertex Data Access audit,
request-response logging, service-account-key inventory, regional endpoint
and publisher-model catalogue controls passed the recorded preflight.

It also proves deterministic refusal to proceed while provider in-memory
caching is not verified disabled, zero occupied calls and zero task-scoped
runtime residue.

It does not prove real isolation, provider request acceptance, inference, a
model draft, proofreader release, latency, token usage, Australian physical
processing or sovereign processing. A container can constrain local
capabilities; it cannot determine the remote provider's physical processing
geography.

## Required intervention

An externally authorised operator must determine the current Vertex
provider-managed in-memory cache state for `bernie-emr4-dev` and establish
explicit `disableCache: true` if needed, without weakening or changing any
other frozen boundary. After that external action, another continuation
requires a fresh five-source rehydration and repetition of the complete
read-only Tranche 3 preflight.

Codex did not alter cache configuration, credentials, API enablement, billing,
IAM, project, service account or the active human account, and did not use an
API key, static key, global endpoint, fallback, other model, other provider or
other region.
