# Threat-model delta: Raisa Microsoft-federation admission runtime

Date: 2026-08-01

Parent: `docs/security/raisa-real-identity-microsoft-federation-boundary-threat-model-delta.md`

Scope: Default-off, route-free, provider-free, in-memory authored-synthetic admission runtime only.

## Runtime-specific risks

| Risk | Control in this tranche | Residual boundary |
|---|---|---|
| Synthetic evidence is mistaken for a verified real token | exact authored-synthetic data class and verifier label; `.invalid` issuer; synthetic reference grammar; no token parser | build/deployment gating and a separately reviewed maintained-library verifier |
| First-match lookup hides duplicate binding | store returns all matches; any count other than one denies | database uniqueness and durable concurrency in the next tranche |
| Email or Office context influences mapping | runtime never reads those fields for validation or lookup; tests retain misleading values | real multi-account UX proof remains closed |
| Audit leaks enumerable external identity | injected minimum-256-bit HMAC key and versioned reference; no raw values in event | production key custody/rotation remains closed |
| Audit fails after identity resolution | audit completes before candidate return; failure overrides admission | durable transaction/session bridge remains closed |
| Candidate is treated as authorization | candidate explicitly carries `authorization_granted=false` and no role/capability | fresh internal reload and endpoint policy remain closed |
| Runtime is accidentally exposed | default-off config, no router imports, static forbidden-import tests | packaging and deployment enforcement remains later |
| Concurrent callers mutate shared evidence | bindings/principals are immutable tuples; audit append uses a lock | distributed replay and durable attempt consumption remain closed |

## Preserved threats

The parent controls for CSRF, PKCE, state, nonce, issuer, audience, tenant, immutable subject, signing key, token lifetime, binding status, internal-principal state and required audit remain represented as fail-closed inputs. This runtime does not claim to implement the upstream cryptographic or browser controls.

## Closed gates

No provider, Microsoft, token, route, cookie, real identity, database, application session, product read, patient/clinical data, cloud/IAM, deployment, production or release authority is opened.

---
Reviewed-by: Codex Security threat-model workflow
Review-date: 2026-08-01
Repository: EMR4
Version: ed45c098
