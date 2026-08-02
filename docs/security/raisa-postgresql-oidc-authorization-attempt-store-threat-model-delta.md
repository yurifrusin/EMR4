# Threat-model delta: PostgreSQL OIDC authorization-attempt store

Date: 2026-08-02

Parent: `docs/security/raisa-two-component-oidc-runtime-adapter-threat-model-delta.md`

## New trust boundary

One provider-free database implementation can now retain an encrypted
authorization attempt across processes. PostgreSQL transaction isolation,
role privileges and RLS join the adapter's state, nonce, PKCE and encryption
boundary. The implementation remains dormant and synthetic-only.

## Assets

- state, nonce and PKCE correlation material inside the encrypted envelope;
- versioned state/nonce HMAC references and encryption-key identifiers;
- the five-minute expiry and maximum-128 capacity invariant;
- exact one-use consume-before-exchange semantics; and
- the separation between database access and all identity/session authority.

## Threats and controls

| Threat | Control | Failure |
|---|---|---|
| Plaintext flow disclosure in database | Authenticated encrypted envelope; only state/nonce HMAC references outside | No plaintext flow residue |
| Ciphertext or row substitution | Envelope repeats references and expiry; flow state/nonce are revalidated with constant-time comparison | Consumed, generic unavailable/deny |
| Key rotation loses live attempts | Bounded active-plus-retained cipher and digest keyrings | Consume with exact retained key or fail closed |
| Unknown or removed key becomes fallback | Exact key identifier lookup; no default/alternate decrypt path | Consumed, generic unavailable |
| Concurrent callback replay | One `DELETE ... RETURNING` transaction commits before decrypt or exchange | One completion at most |
| Expired/corrupt attempt becomes reusable after error | Matched row deletion commits before expiry/decrypt checks | Terminal deny/unavailable |
| Capacity race across processes | Transaction advisory lock, expiry purge, collision lookup, count and insert in one short transaction | Generic unavailable |
| Database role expands into product data | Exact NOLOGIN role; only schema usage and attempt-table select/insert/delete | No product privilege |
| Direct update weakens one-use semantics | No role `UPDATE`; no update policy | Permission/RLS denial |
| Accidental grant bypasses table policy | Forced RLS and allowlisted effective role-name family | Zero visible rows / insert denial |
| RLS owner or superuser bypass mistaken for runtime proof | Acceptance uses `SET ROLE` into the exact non-bypass capability role and records effective/session role separation | Acceptance fails |
| Oversized encrypted residue | 64 KiB plaintext bound and 128 KiB database ciphertext check | Generic unavailable/constraint denial |
| Database/driver diagnostic leakage | SQLAlchemy errors are normalized; evidence excludes URL, role name, SQL text and secrets | Generic unavailable |
| Runtime activation by migration | No router/main import, no LOGIN credential or settings wiring | No application call path |

## Verification

Disposable live-local authored-synthetic PostgreSQL acceptance covers migration
reversibility, schema drift, exact grants, forced RLS, outsider denial,
durability across store instances, rotation, raw-residue scanning, expiry,
capacity, collision, tamper, discard, and concurrent adapter completion with
one exchange. Cleanup must prove the exact database and cluster roles absent.

## Residual risk and next gates

This does not establish production key custody/rotation, a deployment LOGIN or
bounded pool, a mounted callback edge, distributed rate limiting, incident
paging/SIEM, live Microsoft metadata or code exchange, real identity governance,
binding/session/product access, deployment, production or release. Each remains
a separately authorised gate.
