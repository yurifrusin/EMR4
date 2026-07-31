# Threat-model delta: Reception One product-context proposal runtime

Date: 2026-07-29

Scope: default-off authenticated authored-synthetic development runtime only

## New assets and trust boundaries

- authenticated staff/practice/surface context;
- bounded receptionist utterance;
- minimal typed product-context frame;
- request-scoped opaque patient, practitioner, appointment and slot handles;
- untrusted typed planner draft;
- deterministic plan review and reviewed-plan hash;
- proposal-only backend adapter result; and
- typesetter release envelope.

The provider work cell, when separately occupied under the frozen gate, remains
credential-free. Only the one-use host broker may use the existing keyless
impersonated ADC and regional Vertex data plane.

## Principal threats and controls

| Threat | Control |
|---|---|
| Cross-practice or cross-user context leakage | Authenticate first; enforce role and practice scope before every read; bind opaque handles to request, practice, correlation and revision. |
| Prompt-authored identity or authority | Treat utterance and planner draft as untrusted; trusted backend supplies scope; proofreader rejects literals, unknown handles and authority-shaped fields. |
| Over-broad patient/Diary context | Closed frame schema, strict count/byte ceilings, field allowlist and source labels; no notes, contact details, identifiers, clinical fields or broad history. |
| Stale availability or confused-deputy execution | Revision and expiry checks plus independent fresh adapter revalidation before proposal output. |
| Model-to-database mutation | Planner has no database/session/HTTP client; catalogue excludes confirmation/write operators; adapter dispatcher admits only read/proposal functions. |
| GraphQL command tunnelling | GraphQL remains read-only and is not used by the planner; product effects stay in named REST/OpenAPI proposal/confirm commands. |
| Rejected draft leakage | Diagnostics retain allowlisted paths/codes only; typesetter receives only atomic admitted fields. |
| Credential or API-key leakage | Cell child environment omits credential/API-key variables and receives no ADC; broker alone refreshes keyless ADC; audit records only authentication class. |
| Provider/region fallback | Exact hostname, project, model, identity and region pre-call gates; no alternate provider or global endpoint. |
| Retry/cost runaway | Distinct single-use ledger per call, cumulative USD 1 guard and immediate stop after first admitted result. |
| Feature accidentally enabled | Separate default-off setting and runtime policy; production and non-authored-synthetic contexts fail closed. |
| Legacy gate weakening | Existing Interpretation Harness gate remains blocked and its config validator remains unchanged. |

## Required deterministic evidence

- practice and role isolation;
- handle forgery, replay, stale revision and expiry rejection;
- exact schema and size ceilings;
- no free literal or unknown operator execution;
- zero writes and unchanged appointment/audit counts;
- provider-blocked default and legacy-gate invariants;
- credential-free cell and exact broker endpoint;
- audit redaction; and
- complete container/network/image/process/temp cleanup.

## Residual risk

Authored-synthetic development evidence cannot establish safety for real patient
or product-derived data. The runtime remains default-off and no such data may
enter a provider call without a later explicit privacy, residency, retention,
authorization and product-release decision.
