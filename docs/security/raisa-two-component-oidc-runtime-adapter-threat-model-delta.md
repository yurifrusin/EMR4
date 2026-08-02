# Threat-model delta: two-component OIDC runtime adapter

Date: 2026-08-02

Parent: `docs/security/raisa-two-component-oidc-verifier-architecture-threat-model-delta.md`

## New trust boundary

The repository now contains dormant application code capable of constructing a
Microsoft authorization request and, when explicitly enabled and supplied a
credential/transport later, invoking token redemption and verifier metadata
requests. It is not wired, enabled, configured from runtime settings or called
against a provider in this tranche.

## Assets

- state, nonce and S256 PKCE correlation material;
- the encrypted MSAL flow envelope and its five-minute lifetime;
- raw authorization code and transient provider token result;
- discovery metadata and JWKS trust;
- verified immutable Microsoft `tid`/`oid`/`sub`; and
- the boundary between authentication evidence and EMR4 authorization.

## Threats and controls

| Threat | Control | Failure |
|---|---|---|
| Trust MSAL-decoded claims without signature proof | Adapter has no `id_token_claims` path; only raw ID token enters Authlib | Generic 401 |
| State replay or concurrent callback | State-HMAC lookup and atomic removal before the only exchange | One completion at most |
| PKCE/nonce substitution in stored flow | Authenticated encrypted envelope plus flow/URI correlation checks | Generic unavailable/deny |
| Flow secret leakage at rest | Only ciphertext plus state/nonce HMACs in the bounded store | No plaintext flow residue |
| Attempt-store exhaustion | Five-minute purge and hard maximum of 128 entries | Generic unavailable |
| Algorithm or issuer/tenant confusion | Exact RS256 metadata, issuer, audience, tenant and fixed endpoints | Generic unavailable/deny |
| Attacker-selected metadata, JWKS or redirect | Derived exact URLs, pinned GET-only transport, no redirects | Generic unavailable |
| Metadata/JWKS response memory pressure | 128 KiB streamed response bound and short timeouts | Generic unavailable |
| Stale signing keys | Authlib cache, one forced unknown-`kid` refresh, 24-hour client recycle | Verify or fail closed |
| Token or provider diagnostic leakage | 16 KiB pre-parse bound, normalized exceptions, cleared token map | Generic external error only |
| Access/refresh token authority expansion | No resource scopes; no output, audit, persistence or downstream token use | Discard |
| Mutable profile or directory claims grant authority | Output contains only verified `tid`/`oid`/`sub` and explicit false authorization/session flags | No binding, role or session |
| Required audit outage | Fail closed; remove a just-created attempt or consume a completed attempt without release | Generic unavailable |
| Accidental runtime activation | Default off, no route/import from application runtime, no credential settings | No call path |

## Verification

The authored-synthetic matrix covers a valid signature, tampering, HS256,
issuer/audience/nonce/tenant/time/identifier failures, token oversize, coherent
metadata, algorithm mismatch, valid and invalid rollover, refresh outage,
MSAL-claims bypass, encrypted residue, wrong state, failed-exchange replay,
concurrency, audit outage and non-wiring. MSAL start and one rejected redemption
are exercised only over an in-memory intercepted HTTP client.

## Residual risk and next gates

The in-memory attempt store is neither durable nor distributed and has no
cross-process atomicity. No real metadata, signing-key rollover, tenant policy,
credential custody, callback edge, CSRF/origin check, rate admission, browser
bridge or Office dialog has been exercised. Real identity governance, binding
resolution, database capabilities, sessions, monitoring/SIEM, deployment,
production and release remain closed and require separate authority.
