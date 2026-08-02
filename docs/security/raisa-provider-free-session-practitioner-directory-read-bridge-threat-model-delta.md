# Threat-model delta: provider-free session practitioner-directory read bridge

Date: 2026-08-02

Parent: `docs/security/raisa-provider-free-oidc-admission-grant-redemption-bridge-threat-model-delta.md`

## New trust boundaries

1. One opaque application-session cookie and CSRF pair cross into a default-off
   GraphQL context factory bound to an exact server-selected surface/origin.
2. One injected synthetic reference-to-UUID mapping crosses from accepted auth
   state into disposable product user/practice truth.
3. One endpoint-owned authorization decision and required durable audit cross
   before the existing shared practitioner-directory query.
4. Five display-safe practitioner fields cross into the GraphQL response.

No patient, clinical, provider, real-identity or write boundary opens.

## Threats and controls

| Threat | Control | Failure |
|---|---|---|
| Cookie replay on another surface/origin | Factory-fixed surface, exact origin/audience, accepted session generation/expiry checks | Generic 401; no product query |
| Cross-site cookie read | Exact origin plus accepted CSRF cookie/header pair and no permissive mount | Generic request denial; no data |
| Client selects role/practice/policy | Server-fixed policy/action/resource; synthetic mapping and current product user reload | 401/403 before directory access |
| Shared-schema query escapes the directory surface | Bounded JSON POST parser admits one exact `practice.practitioners` selection and safe fields; GET, aliases, fragments, directives, introspection, health, practice-id-only and mutations are rejected | 403/405 before auth or product SQL |
| Synthetic map is mistaken for real identity | Process-local injected mapping, bounded `synthetic-*` refs, disposable UUIDs, no persistence/provider fields | Construction or acceptance failure |
| Role/practice changed after session issue | Fresh product user reload plus exact session principal/role/practice/link comparison | Denial audit; no directory access |
| Inactive staff are enumerated | Bridge always denies `activeOnly=false`, including admin roles | Generic GraphQL `FORBIDDEN`; no query |
| Cross-practice enumeration | Existing practice root no-leak `null`; shared service filters exact current practice | Empty/no-leak result |
| Resolver bypasses authorization | Optional callback is invoked before shared service; bridge context always supplies it; static and runtime tests | Test/acceptance failure |
| Required audit unavailable | Allow is not returned until append-only audit commits | Unavailable response; no product data release |
| Audit leaks staff/session material | Fixed hash/synthetic metadata only; product UUIDs, names, email, cookies, CSRF and query bodies forbidden | Residue gate fails |
| Sensitive practitioner fields expand | Existing fixed GraphQL type and shared projection; exact response-key assertions | Schema/response gate fails |
| GraphQL becomes a command tunnel | Existing query-only schema; no mutation/subscription/provider/write dependency | Static/API Spine gate fails |

## Residual gates

This does not establish safety for patient or clinical reads, real identity or
principal mapping, product-table RLS, a generally mounted application-session
GraphQL endpoint, live Microsoft interoperability, production session/key
custody, hosted networking, distributed abuse resistance, monitoring/SIEM,
deployment, protected integration, production or release.
