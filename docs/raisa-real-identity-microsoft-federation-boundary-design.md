# Raisa real-identity and Microsoft-federation boundary design

Date: 2026-08-01

Status: `frozen_architecture_only`

## Boundary

Microsoft Entra is an external authenticator. EMR4 remains the identity, tenancy, role, clinician-link, session, authorization and audit authority.

```text
untrusted Office/browser surface
  -> exact backend login-start boundary (later)
  -> tenant-specific Microsoft Entra authorization code + PKCE (later)
  -> exact backend callback and maintained OIDC verifier (later)
  -> validated external assertion
  -> exact active pre-provisioned binding
  -> fresh EMR4 user/practice/role reload (later)
  -> accepted parent + surface session runtime (later)
  -> endpoint-owned authorization before each product read (later)
```

The current architecture, in-memory and persistence tranches stop before every arrow labelled `later` that involves a route, Microsoft, real identity or product data.

## Trust zones

| Zone | Trusted fact | Explicitly untrusted |
|---|---|---|
| Word desktop / Word Online / browser | User can initiate an exact login attempt | Office signed-in account, email, display name, role/practice hints, tokens supplied by JavaScript |
| EMR4 protocol edge (future) | Exact redirect configuration and server-held attempt record | Query parameters before state/correlation validation |
| Microsoft Entra | Cryptographically verified authentication assertion for one configured tenant | EMR4 role, practice membership, practitioner relationship or product authority |
| Federation admission | Exact active `(tenant, object)` binding to one principal candidate | Email/domain auto-linking, unknown/ambiguous bindings, guest or tenant-wide membership as authority |
| EMR4 backend | Current internal user, practice, role, clinician linkage, session and endpoint policy | Cached external roles or client-decoded claims |
| PostgreSQL | Hash/HMAC-only bounded state under least privilege | Raw codes, tokens, external identifiers, names, emails, documents or clinical data |

## Initial account posture

The initial architecture is single-tenant and workforce-oriented. It uses a tenant-specific Microsoft Entra v2.0 authority. `common`, `organizations` and `consumers` are never accepted as issuer or discovery authorities. Personal Microsoft accounts are rejected. A personal account invited as a guest may be considered only as a tenant-local Entra object that was deliberately pre-provisioned; its original personal identity creates no authority.

This deliberately separates Word Online compatibility from EMR4 login. A user may be signed into Word with any Microsoft account and still have no EMR4 session.

## Protocol record

A future login attempt is a short-lived server-side record containing an opaque attempt reference, exact surface, exact return origin, S256 challenge, hash-only state and nonce, issue/expiry times and consumed status. The browser carries only opaque protocol values. Callback processing atomically consumes the attempt once.

The future backend uses authorization code flow with OIDC and S256 PKCE. It must:

1. validate exact callback route, method and configured redirect;
2. atomically validate and consume state before releasing any authenticated result;
3. redeem the code server-side through a maintained library;
4. validate signature, algorithm, exact issuer, exact audience, exact tenant, nonce and token time bounds;
5. require immutable `oid`, `tid` and `sub` claims for the authenticated user;
6. resolve exactly one active pre-provisioned binding by `(provider, tid, oid)`;
7. record required metadata audit; and
8. only then pass an internal principal candidate to a later current-user reload and session bridge.

Unknown signing keys trigger at most the library's bounded tenant-specific metadata refresh. Multiple keys and emergency rollover must be supported. A refresh failure, stale/untrusted metadata or still-unknown key denies; it never disables signature validation.

## Identity mapping

The canonical external key is:

```text
microsoft_entra | configured tenant policy | tid | oid
```

`sub` is retained in the verified assertion and may be audited as a keyed reference, but binding authority uses Microsoft’s recommended immutable tenant/object pair. `email`, `preferred_username`, `upn`, `name`, domain, group display names and Office account identifiers are display-only.

Each active external key maps to exactly one EMR4 user and one practice. An EMR4 user may gain another external binding only through a later explicit lifecycle command. Conflicting active bindings, duplicate subjects, an inactive user/practice, a moved practitioner or a revoked binding deny before session creation.

## Authentication is not authorization

The admission result contains only a bounded principal candidate and binding version. It contains no role, clinician status, product scope or capability. A later bridge must load current EMR4 truth and create the existing opaque parent/surface session. Every read or command is then authorised under endpoint-owned backend policy. Microsoft groups, directory roles, claims or consent scopes never become EMR4 roles automatically.

## Binding lifecycle

Binding creation, replacement, revocation and recovery are future REST/OpenAPI commands. Each must include:

- authenticated actor and target practice/user;
- recent re-authentication and required administrator policy;
- an idempotency key and correlation identifier;
- expected current binding version;
- exact collision and uniqueness checks;
- reason code, required audit and actor/approver separation for replacement or recovery; and
- central session-generation revocation after a material identity change.

GraphQL may later expose a redacted status such as provider, active/revoked state and last-used time to an authorised administrator. It must never expose raw tenant/object identifiers or a token. Async events may describe completed lifecycle facts but cannot perform the command.

## Failure semantics

Externally visible login failures are non-enumerating. Invalid protocol, tenant, token, subject, binding or internal-user state all return the same generic authentication failure; only bounded internal audit reason codes distinguish them. Rate limiting, abuse controls and incident paging are later operational gates.

Required audit failure returns a service-unavailable result and releases no principal. Database or identity-provider uncertainty denies. There is no fallback to email matching, a different Microsoft tenant, Office signed-in state, a bearer in storage, or a local session without explicit separately designed recovery policy.

## Keyed-reference persistence

The persistence descendant canonicalizes and computes versioned HMAC-SHA-256 references for issuer policy, tenant ID, object ID and correlation. A minimum 256-bit injected synthetic key is required in tests. Plain hashes of tenant/object IDs are forbidden because these identifiers are structured and enumerable. Raw external identifiers and key material never reach PostgreSQL.

Production key custody, rotation, dual-read migration and disaster recovery require a separate operational design. The synthetic persistence proof cannot be reconfigured into production by changing an environment flag.

## Explicitly closed

No live Entra app registration, secret/certificate, redirect, discovery, JWKS fetch, authorization request, token exchange, Graph call, Office identity API, real user/tenant identifier, login/callback route, product read, session issuance, identity-link command, cloud/IAM mutation, deployment, production or release is part of the authorised three-tranche sequence.
