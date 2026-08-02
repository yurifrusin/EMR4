# Threat-model delta: PostgreSQL OIDC operational connection boundary

Date: 2026-08-02

Parent: `docs/security/raisa-postgresql-oidc-authorization-attempt-store-threat-model-delta.md`

## New trust boundaries

1. A finite authenticating LOGIN now sits before the accepted NOLOGIN
   capability role.
2. A reused physical PostgreSQL connection crosses mutually untrusted logical
   borrowers and must be restored on both checkout and return.
3. A runtime key provider resolves opaque references into encryption and digest
   material during startup without placing credentials in repository config.

The implementation remains dormant, provider-free and authored-synthetic-only.

## Threats and controls

| Threat | Control | Failure |
|---|---|---|
| Deployment credential directly owns table/product access | Exact NOINHERIT LOGIN has membership only; explicit SET ROLE enters the NOLOGIN capability | Direct LOGIN query denied |
| Pool exceeds the database principal limit | Validated size plus overflow cannot exceed finite role connection limit | Construction rejected |
| Returned connection retains elevated role or weakened timeout | Custom reset rolls back, RESET ROLE/ALL, verifies LOGIN identity and commits cleanup | Connection invalidated/unavailable |
| Checkout trusts contaminated session state | Checkout starts from reset LOGIN, applies exact role/settings and verifies readback | Checkout fails closed |
| URL options bypass exact role/session setup | Reject service/options/role-changing query parameters and mismatched username | Construction rejected before connect |
| Pool exhaustion stalls request workers | Finite queue, overflow and checkout timeout; live contention proof | Bounded unavailable result |
| Raw keys are embedded in config | Typed config stores references only; structural provider owns byte resolution | Configuration rejected |
| Missing/unknown secret silently falls back | Exact reference calls, no alternate provider/default key and atomic builder | No runtime released |
| Same material is reused for encryption and lookup | Separate keysets, unique references and constant-time material comparison | Construction rejected |
| Secret or reference leaks through errors/evidence | Fixed errors; sanitized evidence and raw-value scans | Acceptance fails |
| Builder activates identity/product behavior | No router/main import and no provider, binding, session or product dependency | No application call path |

## Verification

Disposable loopback PostgreSQL acceptance exercises exact roles and grants,
direct-LOGIN denial, effective-role access, checkout/readback, deliberate
session contamination, reset and physical-connection reuse, pool exhaustion,
key resolution/separation/rotation, fresh-runtime store/consume, raw-residue
scanning and complete database/two-role cleanup.

## Residual risk and next gates

This does not establish production password or key custody, secret rotation or
revocation, managed pooler compatibility, TLS/CA policy, distributed abuse
resistance, monitoring/SIEM, a mounted callback edge, live Microsoft metadata
or code exchange, real identity governance, binding/session/product access,
cloud/IAM, deployment, production or release. Each remains separately gated.
