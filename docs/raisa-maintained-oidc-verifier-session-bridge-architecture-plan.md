# Raisa maintained OIDC verifier and session-bridge architecture plan

Date: 2026-08-02

Owner: Yuri / GPT Sol

Status: `authorised_architecture_only_provider_free`

Reasoning level: Extra High for identity, protocol, database-capability and
session-atomicity choices; High for deterministic artifact verification.

## 1. Authority

Yuri authorised an architecture-only successor to the protected-integrated
real-identity/Microsoft-federation sequence. This tranche may freeze:

1. a maintained OIDC protocol/verifier library boundary;
2. a least-privilege PostgreSQL provider-to-practice bootstrap; and
3. a backend-owned application-session bridge that works across native browser,
   installed Word and Word Online cookie partitions.

It may add repository-local plans, designs, threat analysis, API Spine
contracts, schemas, authored-synthetic cases, deterministic acceptance, tests,
continuity evidence, task-branch commits and a draft pull request.

It may not add or change a package dependency, contact Microsoft, register an
Entra application, use a real tenant or identity, add a FastAPI/GraphQL route,
run a database migration, create a role, read product data, issue a live
session, change cloud/IAM, deploy, integrate to a protected ref, enter
production or release.

## 2. Objective

Freeze the smallest coherent bridge from one cryptographically verified,
tenant-specific Microsoft authentication result to one fresh EMR4 application
session without allowing Microsoft claims, Office state or a privileged
database owner to become EMR4 authority.

The design must answer:

- which maintained library owns protocol and token verification;
- how state, nonce, S256 PKCE, redirect, issuer, audience, tenant, subject,
  time and signing-key rollover checks fail closed;
- how a provider identity can resolve one practice without table-owner runtime
  access or broad table grants;
- how a callback crosses browser/Office cookie partitions without copying a
  session bearer through URLs or storage;
- where current internal user, practice, role and practitioner truth is reloaded;
- how one-use admission, session creation and required audit remain atomic;
- how session rotation, revocation, CSRF, cookies, redirect targets, logging,
  enumeration and rate admission remain bounded; and
- which later operational and human decisions remain closed.

## 3. Frozen choices

### 3.1 Maintained library boundary

The future implementation candidate is Microsoft Authentication Library for
Python (MSAL Python), using the stable confidential-client authorization-code
flow API. The reviewed architecture baseline is MSAL Python 1.37.0; any future
implementation must pin a current supported version after dependency, licence,
SBOM and security review. This tranche changes no dependency.

MSAL must own tenant-specific discovery, authorization-code redemption, OIDC
ID-token signature and claim validation, state handling, nonce handling and
signing-key rollover. EMR4 code may validate strict postconditions on the
library-produced result, but may not parse an untrusted JWT, choose an algorithm
from a token header, fetch an arbitrary `jwks_uri`, disable verification or
fall back to PyJWT/custom JOSE.

The future adapter uses a tenant-specific v2 authority and
`ConfidentialClientApplication.initiate_auth_code_flow()` followed exactly once
by `acquire_token_by_auth_code_flow()`. `common`, `organizations`, `consumers`,
personal accounts and arbitrary discovery URLs remain inadmissible.

### 3.2 Backend-mediated protocol

The only candidate flow is `response_type=code`, OpenID Connect scopes
`openid profile`, S256 PKCE and a confidential backend. No Graph, resource API,
`email`, `offline_access`, refresh-token, implicit, hybrid, device-code,
resource-owner-password or client-supplied bearer path is allowed.

The backend creates a five-minute authorization attempt with independently
random state, nonce and PKCE verifier. It stores only state/nonce digests and a
short-lived envelope-encrypted MSAL flow record; the raw verifier never enters
logs, cookies, URLs, Office settings or browser storage. The attempt is bound to
one exact surface, allowlisted HTTPS origin and server-side return-target enum.

The callback consumes the attempt atomically before its one provider exchange.
A failed exchange requires a new attempt. Exact redirect URI comparison,
state/nonce/PKCE correlation, exact issuer/audience/tenant, immutable `tid` plus
`oid`, non-empty `sub`, token lifetime and library-established signing-key trust
are mandatory. Email, domain, display name, Office account, groups, directory
roles and consent scopes never establish an EMR4 identity or role.

### 3.3 Least-privilege provider-to-practice bootstrap

The future deployment must replace the accepted persistence proof's table-owner
lookup with one audited, HMAC-only PostgreSQL resolver function:

- the deployment LOGIN remains `NOINHERIT` and has no direct table grants;
- one `NOLOGIN`, `NOBYPASSRLS` bootstrap capability can only execute the exact
  resolver signature;
- a separate `NOLOGIN` routine owner owns the `SECURITY DEFINER` function but
  owns no schema or table and has only the minimum binding `SELECT` and audit
  `INSERT` privileges;
- `PUBLIC` execution is revoked and `search_path` is fixed to `pg_catalog`, with
  every application object schema-qualified;
- forced RLS policies admit only the function owner and exact transaction-local
  HMAC lookup/correlation context set inside the function;
- the function accepts fixed-length versioned HMAC references, not raw provider
  identifiers, and returns only binding/user/practice references and version;
- zero or ambiguous rows return one generic denial after required metadata
  audit, including a practice-null rejection audit when no practice is known;
  and
- required audit is inserted before any row is returned.

The runtime never connects as a table owner, migration owner, superuser or
`BYPASSRLS` role. Binding create/revoke/recover remains a separate, closed,
dual-authorised REST command capability.

### 3.4 Partition-safe session bridge

The Microsoft callback never sets or returns an EMR4 application-session
cookie. After maintained-library verification and first audited binding
resolution it creates a random 60-second, one-use admission grant. PostgreSQL
stores only the grant digest plus binding version, HMAC external reference,
surface, exact origin, return enum, correlation and expiry. Raw Microsoft
tokens, claims and the raw grant are not persisted.

The callback page is `Cache-Control: no-store`, has a restrictive CSP and
referrer policy, places no credential in its URL, and sends the opaque grant
only to the exact allowlisted opener/Office dialog parent origin. It then
closes. The original native-browser or Office taskpane partition redeems the
grant with the existing pre-authentication CSRF cookie/header pair.

Redemption locks the grant, re-resolves the active binding, checks its version,
freshly reloads the internal user, practice, role and practitioner relationship,
and then creates the existing opaque parent and surface session plus required
audit in one database transaction. Grant consumption, session rows and audit
commit together. The `Set-Cookie` response is emitted only after commit. A
concurrent or repeated redemption releases no cookie. A failed transaction
leaves no session; an unauditable result returns a generic 503-style error.

The first implementation must use the accepted cookie contract:
`__Host-emr4-application-session` and `__Host-emr4-application-csrf`, `Secure`,
`HttpOnly`, `Path=/`, no `Domain`, `SameSite=None`, `Partitioned`, plus the
`X-EMR4-CSRF` header. Surface/origin/audience binding remains backend-owned.
The raw parent session never reaches a client.

### 3.5 Session and product boundary

Authentication rotates away every pre-authentication or prior session value.
Parent and surface identifiers are CSPRNG-generated opaque bearers; only hashes
are stored. The accepted eight-hour parent maximum, thirty-minute idle maximum,
central principal generation, logout/revocation and role/practice/practitioner
change revocation remain authoritative. No Microsoft refresh token extends an
EMR4 session.

The bridge releases only an application session. Every later GraphQL read or
REST command must resolve that session, freshly apply endpoint-owned practice,
role, practitioner, resource and audit policy, and deny on changed/revoked
truth. The callback and redemption perform no patient, appointment, diary,
document or clinical read.

## 4. API Spine classification

- `POST /api/v1/application-auth/federation/microsoft/start`: future external
  REST protocol/command boundary; creates one bounded attempt; closed now.
- `GET /api/v1/application-auth/federation/microsoft/callback`: future provider
  callback protocol boundary; consumes one attempt and emits one admission
  grant through a no-store bridge page; closed now.
- `POST /api/v1/application-auth/federation/session/redeem`: future one-use REST
  redemption command; creates one application session and cookie after atomic
  audit; closed now.
- Binding create/revoke/replace/recover: future idempotent dual-authorised REST
  commands; not included.
- Redacted binding status: future resolver-authorised GraphQL read model; no
  mutation and not included.
- Session issuance: internal backend service operation; never a generic
  client-selected role/practice/session API.
- Async events: completed facts only; they cannot authenticate, bind or create
  a session.

## 5. Acceptance gates

### Gate A — maintained verifier contract

- The policy selects MSAL Python confidential-client auth-code flow and no
  alternate verifier.
- Tenant authority, redirect, state, nonce, S256 PKCE, issuer, audience, `tid`,
  `oid`, `sub`, time and signing-key trust are all mandatory.
- No acceptance artifact imports MSAL, JWT, HTTP, socket, database, FastAPI or
  product runtime; side-effect counts are zero.

### Gate B — least-privilege bootstrap

- Runtime LOGIN/table-owner/BYPASSRLS paths are forbidden.
- The exact executor/routine-owner/function/RLS/search-path/grant boundaries are
  represented and direct table access fails the cases.
- Unknown bindings can be audited without giving the runtime table-owner
  authority or leaking raw provider identifiers.

### Gate C — session bridge and host reconciliation

- Callback releases no cookie or session bearer.
- Native Diary, installed Word and Word Online use the same one-use grant
  redemption semantics in their original cookie partition.
- Redemption repeats binding resolution and fresh internal truth reload.
- Grant consumption, session creation and required audit are atomic; cookies
  follow commit only.
- CSRF, exact origin/surface/audience, return allowlist, non-enumerating errors,
  bounded rate admission and no-store/logging rules are explicit.

### Gate D — non-wiring

- The OpenAPI document is architecture-only and not mounted.
- No application router imports an acceptance evaluator or new bridge module.
- No migration, dependency, role, network, provider, identity, product,
  deployment or protected-ref side effect occurs.

## 6. Claim limit and next gates

A pass proves a coherent repository-local architecture for maintained
tenant-specific Microsoft OIDC verification, least-privilege HMAC-only identity
bootstrap and partition-safe application-session handoff. It does not prove the
library against Microsoft, a live callback, real identity governance, database
function/RLS correctness, a real session, Office organisational deployment,
distributed abuse resistance, secret/certificate or HMAC-key custody,
monitoring/SIEM, product-read authorization, production fitness or release.

Any dependency addition, migration/role/function implementation, route wiring,
live Entra registration/call, real identity or product read, cloud/IAM change,
protected integration, deployment, production or release requires fresh
authority.

## 7. Primary references

- Microsoft, [OAuth 2.0 authorization code flow](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-auth-code-flow)
- Microsoft, [Acquire tokens with MSAL Python](https://learn.microsoft.com/en-us/entra/msal/python/getting-started/acquiring-tokens)
- Microsoft, [Tokens and claims overview](https://learn.microsoft.com/en-us/entra/identity-platform/security-tokens)
- Microsoft, [Signing-key rollover](https://learn.microsoft.com/en-us/entra/identity-platform/signing-key-rollover)
- Microsoft, [ID-token claims reference](https://learn.microsoft.com/en-us/entra/identity-platform/id-token-claims-reference)
- [OAuth 2.0 Security Best Current Practice, RFC 9700](https://www.rfc-editor.org/rfc/rfc9700.html)
- OpenID Foundation, [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0-final.html)
- OWASP, [Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- OWASP, [CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
