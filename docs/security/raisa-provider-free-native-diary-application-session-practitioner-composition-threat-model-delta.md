# Threat-model delta: provider-free native-Diary application-session practitioner composition

Date: 2026-08-03

Status: architecture-only

## Boundary change

No product or data boundary opens. This delta freezes how the native Diary
surface may deterministically consume the already accepted application-session
practitioner-directory read while the existing bearer-authenticated
GraphQL/REST-fallback path remains unchanged when the feature is off (the
default).

| Threat | Control | Failure outcome |
|---|---|---|
| The composition silently replaces the existing bearer path or its REST fallback | Default-off unmounted composition; existing native Diary read/auth/fallback frozen byte-for-byte | Candidate rejected as a material product fork |
| The native Diary composition is routed through Bernie or Davida | Separate deterministic consumer branch; no probabilistic work cell dependency | Composition rejected before product wiring |
| An agent proofreader becomes a dependency of the deterministic consumer | Deterministic composition reuses only the lower application-session/product-read bridge | Schema or static contract test fails |
| Office one-use terminal reload/logout lifecycle is reused in the long-lived Diary | Surface-specific composition; Office adapter remains Office-only | Static contract or lifecycle test fails |
| A new policy/action/resource or a general GraphQL migration is introduced | Contract binds the exact existing policy/action/resource and read only | Contract validation fails |
| The composition admits a different projection or field selection | Exact display-safe shape `{id displayName roleLabel active defaultLocation {id name}}` | Projection drift rejected |
| Stale or superseded session response is rendered as truth | Fail-closed stale/superseded rejection; fresh read required | Stale/session output rejected; no UI update |
| Session artifacts, authority envelopes or raw identifiers leak into UI | They are declared not UI data; evidence carries counts/labels only | Privacy contract test fails |
| A client selects practice, role, policy, resource, fields or operation | Fixed read variables `activeOnly=true`, `limit=200`, `offset=0`; no client-selected scope | Non-exact request rejected before auth |
| Inactive staff enumeration is opened | Active-only only; inactive enumeration closed for every role | Denial before product data access |
| GraphQL mutation, command tunnel, new REST surface or event actuator is introduced | API Spine stays scoped read-only; no such surface is declared | API Spine conformance test fails |
| Providers, real identity, Microsoft federation, deployment or production is implied | Closed gates listed explicitly; no runtime or usability claim | Gate test fails; candidate not accepted |
| Convenience staging captures the user-owned branding directory | Explicit-path staging only; `git add -A`/`.` forbidden | Pre-commit gate fails |

## Residual gates

Live providers, memory/RAG/GraphRAG, real identity, patient/clinical/document
data, model-to-database writes, GraphQL mutations, external identity writes,
cloud/IAM, deployment, production, release, protected evidence and protected
refs remain separately closed. No runtime or usability claim is made.
