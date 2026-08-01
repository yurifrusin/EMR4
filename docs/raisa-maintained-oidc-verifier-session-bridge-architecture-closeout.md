# Raisa maintained OIDC verifier and session-bridge architecture closeout

Date: 2026-08-02

Result: `raisa_maintained_oidc_verifier_session_bridge_architecture_pass`

## Outcome

The authorised architecture-only descendant passes. It freezes one maintained
Microsoft OIDC boundary, one least-privilege provider-to-practice bootstrap and
one backend-owned application-session bridge across native Diary, installed
Word and Word Online cookie partitions.

MSAL Python is the sole future provider-facing implementation candidate. The
future adapter uses a tenant-specific confidential-client authorization-code
flow through `initiate_auth_code_flow()` and
`acquire_token_by_auth_code_flow()`. It permits no custom JWT/JOSE verifier,
alternate tenant, arbitrary discovery URL or fallback. A future implementation
must independently review and pin a current supported package; this tranche
adds no dependency and makes no provider request.

## Security architecture

The pre-practice database boundary replaces a table-owner runtime connection
with an execute-only `NOLOGIN`, `NOBYPASSRLS` capability. Its exact
`SECURITY DEFINER` resolver is owned by a separate non-table-owner role, fixes
`search_path` to `pg_catalog`, schema-qualifies every application object,
accepts only versioned fixed-length HMAC references, returns four bounded
references and records required metadata audit before returning. Direct table
grants, superuser, `BYPASSRLS`, owner-login and dynamic SQL paths are forbidden.

The Microsoft callback creates neither an application session nor a session
cookie. After maintained-library verification and initial audited binding
resolution, it may create only a random, digest-persisted, 60-second one-use
admission grant bound to surface, origin, audience, return enum, policy and
binding version. A no-store bridge page sends that opaque grant in an
exact-origin message body, never through a URL, browser storage, Office
settings, document content or a cookie.

The original cookie partition redeems the grant with the accepted CSRF pair.
Redemption locks the grant, repeats the binding lookup, freshly loads current
internal user/practice/role/practitioner truth, and atomically consumes the
grant, creates parent/surface session state and writes required audit. A cookie
may be emitted only after commit. Callback and redemption read no patient,
appointment, diary, document or clinical truth.

## Acceptance evidence

The deterministic provider-free runner schema-validates the architecture
policy, decision contract, 33 authored-synthetic cases and the unmounted API
Spine document. All 33 cases match their exact expected outcome. Three positive
cases cover native Diary, installed Word and Word Online; every accepted case
still records zero provider call, database write, admission grant, session,
cookie and product-data release. Negative cases close custom verification,
tenant/redirect/state/nonce/PKCE/signing-key failures, mutable-claim authority,
owner/direct-table bootstrap, unconstrained security definer, missing forced
RLS, raw identity, callback cookie, URL/cross-origin grant handoff, missing
CSRF, stale binding/internal truth, non-atomic session/audit, cookie-before-
commit, product read and token persistence.

The evidence records exactly zero provider calls, real identity values,
database reads/writes/migrations/roles, mounted routes, dependencies, sessions,
product reads, patient/clinical fields, cloud/IAM mutations, deployments and
protected-ref movements.

## Claim limit and next gate

This pass proves a coherent repository-local architecture. It does not prove a
package installation, live Microsoft discovery/token exchange, real identity,
database role/function/RLS implementation, callback, application session,
Office organisational deployment, product authorization, distributed abuse
resistance, production key custody, monitoring/SIEM, deployment, production
fitness or release.

The next safe candidate is a provider-free maintained-verifier dependency and
offline adapter-admission tranche: review and pin the supported MSAL Python
package, implement only the provider adapter seam behind deterministic
synthetic/fault fixtures, and keep routes, real identities, product reads,
database changes and live network closed. Package and licence acceptance are a
fresh material decision and require Yuri's explicit authority. A later, separate
candidate may implement and disposable-PostgreSQL-test the resolver/grant
capability.

Protected integration and any further GitHub Pages rebuild remain closed.

