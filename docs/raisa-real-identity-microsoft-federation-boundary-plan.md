# Raisa real-identity and Microsoft-federation boundary plan

Date: 2026-08-01

Owner: Yuri / GPT Sol

Status: `authorised_architecture_only_provider_free`

Reasoning level: Extra High for identity, protocol, persistence and failure-boundary choices; High is sufficient for deterministic artifact verification.

## 1. Authority

Yuri authorised this architecture-only descendant of the accepted shared application-authentication and Office cookie-compatibility stack, together with its next two logical candidates. The three authorised tranches are:

1. this real-identity and Microsoft-federation boundary design;
2. a default-off, route-free, provider-free, in-memory authored-synthetic admission and exact-binding runtime; and
3. reversible PostgreSQL persistence for authored-synthetic external-identity bindings and metadata-only audit, exercised only in a disposable local database.

This authority does not permit a Microsoft Entra application registration, live discovery or token exchange, Graph or Office identity access, a public login/callback route, a real identity or tenant identifier, a product-data read, a live application session, cloud/IAM mutation, deployment, production, release or protected-ref movement.

## 2. Objective

Freeze a backend-owned authentication boundary in which Microsoft Entra can establish one external authentication fact but cannot create EMR4 identity, practice membership, role, clinician status or product authority.

The design must specify:

- the supported account and tenant posture;
- the OAuth/OIDC flow and browser/Office boundary;
- token, issuer, audience, tenant, subject, replay and key-rollover checks;
- exact pre-provisioned mapping to an active EMR4 principal;
- session handoff to the already accepted application-authentication runtime;
- metadata-only audit and privacy handling;
- account-link, unlink, recovery and revocation gates; and
- exact fail-closed outcomes and later human decisions.

## 3. Frozen choices

### 3.1 One organisational tenant at first release

The first admissible provider shape is a configured Microsoft Entra organisational tenant using a tenant-specific v2.0 authority. The architecture rejects `common`, `organizations`, `consumers`, personal Microsoft accounts and any tenant not exactly allowlisted. A guest may authenticate only when it has an exact pre-provisioned tenant-local immutable binding; guest status alone grants nothing.

The Microsoft or Office account already signed into Word is a convenience context only. It is never silently adopted as the EMR4 identity.

### 3.2 Backend-mediated authorization-code flow

The candidate live protocol is OpenID Connect authorization code flow with S256 PKCE. Exact allowlisted HTTPS redirects, single-use state and nonce, bounded authorization-attempt expiry, and server-side code redemption are mandatory. Implicit, resource-owner-password, device-code, client-supplied token acceptance and token relay through Office document or browser storage are inadmissible.

No live endpoint is added by these three tranches. A future implementation must use a maintained protocol library and a confidential backend/BFF boundary; hand-written JWT cryptography is not accepted.

### 3.3 Tenant-specific validation

A future verifier must use the configured tenant-specific OpenID Connect discovery document and its `jwks_uri`, validate the signature and algorithm through a maintained library, handle multiple current keys and rollover, and fail closed on unknown keys when a bounded refresh cannot establish trust.

The accepted ID-token facts are exact issuer, exact client audience, exact configured tenant ID, immutable tenant-local object ID, subject, nonce, issuance/not-before/expiry bounds and authorization-attempt correlation. The pair `(tid, oid)` is the Microsoft identity key. `email`, `preferred_username`, `name`, domain and Office signed-in state are display-only and cannot select or create a binding.

### 3.4 Exact pre-provisioned binding

Admission requires exactly one active binding from `(provider, issuer policy, tid, oid)` to one active EMR4 user and practice. There is no just-in-time account creation, email/domain auto-linking, role inference or practice inference. Missing, ambiguous, inactive or revoked bindings deny generically.

Federation establishes authentication only. After admission, the backend must freshly load the internal user, practice, role and practitioner relationship and independently apply the existing authorization policy before any product read. A Microsoft claim is never an EMR4 role or capability.

### 3.5 Token and privacy boundary

Microsoft authorization codes and tokens remain ephemeral inside the future backend protocol handler. They are never stored in PostgreSQL, application logs, Office settings, document content, `localStorage`, `sessionStorage`, IndexedDB or client cookies. No Microsoft Graph permission or `offline_access` scope is required for sign-in. The initial scope is `openid` plus the minimum profile claims needed by the maintained library.

Persistent lookup material must use a versioned keyed HMAC over canonical provider/tenant/subject values. A plain SHA-256 of a low-entropy external identifier is inadmissible. Keys and their production custody remain a later operational decision; the authorised persistence tranche may accept only an injected synthetic test key.

### 3.6 Audit before session creation

Every admission result requires a typed metadata audit before a principal candidate may be returned. Audit may contain correlation, provider, policy version, decision, reason, hash-only external reference, binding reference, internal synthetic references and time. It may not contain raw tokens, codes, state, nonce, PKCE verifier, Microsoft tenant/object identifiers, email, name, document, patient or clinical content.

If required audit is unavailable, admission returns a service error and releases no principal. Session creation is a later bridge and must be in the same fail-closed security transaction or have a compensating revocation design.

### 3.7 Link lifecycle is a command boundary

Creating, replacing, revoking or recovering a real external-identity binding is an auditable REST/OpenAPI command, not GraphQL and not a configuration side effect. It requires separate authority, current privileged EMR4 authentication, recent re-authentication, idempotency, explicit target practice/user, collision checks and a second authorised human for replacement or recovery. No such route or command is authorised here.

## 4. API Spine classification

- Microsoft browser redirect and callback: future REST protocol boundary; closed now.
- Binding create/revoke/recover: future REST/OpenAPI commands with idempotency and audit; closed now.
- Current binding status for an authorised administrator: future narrowly scoped read model; closed now.
- Session issuance: future internal service call into the accepted application-auth runtime; no generic client-selected authorization API.
- Asynchronous notifications: may report a completed binding lifecycle event later but cannot create authority or complete a command.

## 5. Acceptance gates

### Gate A — architecture artifacts

- The policy and decision schemas validate.
- Every authored-synthetic case matches the frozen exact outcome.
- Microsoft/Office signed-in context, email and domain never create a binding.
- `tid` plus `oid`, exact tenant/issuer/audience, state, nonce, PKCE, lifetime and signature evidence are required.

### Gate B — threat and failure closure

- Login CSRF, code interception, replay, confused deputy, tenant confusion, key rollover, account-link takeover, guest ambiguity, inactive internal identity, audit failure and token leakage are represented.
- Every unknown or ambiguous state denies before principal or session release.
- No fallback to localStorage, Office identity, email matching, a personal Microsoft account or a different tenant exists.

### Gate C — non-wiring

- No FastAPI/GraphQL router imports the acceptance evaluator or later route-free runtime.
- No network, provider, Microsoft, browser automation, database or product service is called by architecture acceptance.
- Side-effect counts are exactly zero.

## 6. Next two authorised candidates

The in-memory descendant may consume only authored-synthetic, already-validated assertion evidence through a verifier port, exact synthetic bindings and an in-memory required-audit sink. It remains default-off and route-free and cannot create a session.

The PostgreSQL descendant may add a reversible migration, keyed-HMAC identity lookup, exact binding lifecycle persistence and append-only metadata audit. It may run only against a uniquely named disposable local database and must be fully removed afterward. It cannot migrate an existing environment, grant a durable runtime role, add a route or accept real identity data.

## 7. Claim limit

A pass proves a coherent, typed, repository-local security architecture for connecting one configured organisational Microsoft Entra tenant to pre-provisioned EMR4 identities. It does not prove interoperability with Microsoft, token cryptography, live login, account linking, identity governance, secure production key custody, product-read safety, deployment, production fitness or release readiness.

## 8. Primary protocol references

- Microsoft, [Secure applications and APIs by validating claims](https://learn.microsoft.com/en-us/entra/identity-platform/claims-validation)
- Microsoft, [OAuth 2.0 authorization code flow](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-auth-code-flow)
- Microsoft, [OpenID Connect on the Microsoft identity platform](https://learn.microsoft.com/en-us/entra/identity-platform/v2-protocols-oidc)
- Microsoft, [Access tokens in the Microsoft identity platform](https://learn.microsoft.com/en-us/entra/identity-platform/access-tokens)
- Microsoft, [Signing key rollover](https://learn.microsoft.com/en-us/entra/identity-platform/signing-key-rollover)
