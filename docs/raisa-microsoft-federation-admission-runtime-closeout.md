# Raisa Microsoft-federation admission runtime closeout

Date: 2026-08-01

Result: `raisa_microsoft_federation_admission_runtime_pass`

## Outcome

The first authorised architecture descendant passes. EMR4 now has one default-off, route-free, provider-free in-memory policy runtime for authored-synthetic Microsoft Entra assertion evidence and exact pre-provisioned synthetic bindings.

The module does not parse or verify a token. It accepts only an explicit `authored_synthetic` / `synthetic_oidc_verifier` evidence type with a `.invalid` tenant-specific issuer. It repeats the frozen tenant, account, attempt, state, nonce, PKCE, signature-result, algorithm, signing-key, issuer, audience, subject and lifetime admission checks before exact mapping.

Mapping returns all matches and denies ambiguity. Exactly one active binding plus one active synthetic internal user/practice can produce a bounded principal candidate. That candidate contains no role, practitioner, capability or product data and explicitly records `authorization_granted=false` and `session_created=false`.

## Acceptance evidence

All 22 parent architecture cases match the in-memory implementation. Exactly one case admits; every default-off, protocol, token, tenant, subject, binding, internal-principal or audit failure denies or errors before a candidate is returned.

Twenty-one required metadata audit events were recorded; the intentionally unavailable audit case recorded none and returned `required_audit_unavailable`. The exact successful case recorded audit before releasing its candidate. Versioned HMAC-SHA-256 references use an injected 256-bit-or-greater synthetic key, and the audit corpus contains none of the tested raw tenant, object, subject or display-email values.

The runtime imports no HTTP, socket, Microsoft, JWT, FastAPI, SQLAlchemy or subprocess client. No FastAPI/GraphQL router imports it. Provider, identity-provider, Office/Graph, HTTP/socket, route, database, session, product, clinical, cloud/IAM and deployment side-effect counts are all zero.

## Security disposition

The implementation makes accidental authority widening difficult: it is disabled by default, rejects non-synthetic evidence and non-tenant-specific account posture, fails on multiple bindings instead of selecting the first, records audit before release and returns a principal candidate that is structurally not an authorization result.

It remains a policy prototype, not an OIDC verifier. The synthetic verification flags cannot establish any real cryptographic fact and must never be wired to a route.

## Claim limit and next gate

This result proves route-free in-memory representation of the frozen admission and audit-before-release policy. It does not prove live Microsoft/OIDC behavior, durable uniqueness/revocation, cross-process replay control, real EMR4 identity reload, application-session creation, product authorization, deployment, production fitness or release readiness.

The next already-authorised descendant is reversible authored-synthetic PostgreSQL binding and metadata-audit persistence exercised only in a uniquely named disposable local database. It must add no route, no durable runtime-role grant, no real identity data and no product read.

Protected integration remains paused because repository documentation would trigger public GitHub Pages deployment.
