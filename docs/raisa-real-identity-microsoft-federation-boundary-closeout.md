# Raisa real-identity and Microsoft-federation boundary closeout

Date: 2026-08-01

Result: `raisa_real_identity_microsoft_federation_boundary_architecture_pass`

## Outcome

The separately authorised architecture-only tranche passes. It freezes one tenant-specific Microsoft Entra authentication boundary while retaining EMR4 as the sole identity, practice, role, clinician-link, session, authorization and product authority.

The initial posture is deliberately narrow: one explicitly configured organisational tenant, authorization code with OIDC and S256 PKCE, exact HTTPS redirects, one-use state and nonce, maintained-library signature validation, tenant-specific discovery/JWKS, key-rollover handling, exact issuer/audience/tenant checks and immutable `(tid, oid)` subject mapping.

Only one active pre-provisioned external binding may release a bounded internal principal candidate. Email, domain, display name, Office signed-in state, Microsoft groups and Microsoft roles cannot select or create an EMR4 identity or authority. Federation authenticates; every EMR4 role, clinician link and product permission must later be freshly reloaded and independently authorised by the backend.

## Acceptance evidence

The schema-validated policy, decision contract and 22 authored-synthetic cases pass. Exactly one configured, valid, active and unambiguous pre-bound organisational case admits. The other 21 cases fail closed for default-off state, non-tenant-specific or personal account posture, replay/expiry, state/nonce/PKCE failure, signature/key/issuer/audience/tenant failure, token lifetime, missing immutable subject, missing/ambiguous/revoked binding, inactive internal principal or required-audit outage.

Every decision creates zero application session and releases zero product data. The architecture evaluator imports no network, Microsoft, JWT, FastAPI, SQLAlchemy or product runtime. Recorded provider, identity-provider, Office/Graph, backend, database, product, session, cloud/IAM and deployment side-effect counts are all zero.

## Security disposition

The design addresses login CSRF, callback injection, code replay, tenant confusion, confused-deputy audience, signature/key rollover, email-link takeover, guest ambiguity, binding collision, stale role state, audit failure, identifier leakage, recovery abuse, Office-account substitution and accidental synthetic-runtime wiring.

Persistent external lookup material must use an injected, versioned keyed HMAC rather than a plain digest. Raw Microsoft codes, tokens, tenant/object identifiers, email and name are forbidden from persistence and general audit.

## Claim limit and next gate

This result proves only a repository-local architecture and deterministic acceptance oracle. It does not prove a Microsoft Entra registration, redirect, discovery/JWKS request, token exchange, signature verification, key rollover, live login, real identity mapping, EMR4 session, product read, deployment, production fitness or release readiness.

The next already-authorised descendant is a default-off, route-free, provider-free, in-memory authored-synthetic admission and exact-binding runtime. It must accept only already-validated synthetic assertion evidence through a verifier port, require audit before releasing a principal candidate, create no session and remain unreachable from every FastAPI/GraphQL router.

Protected integration remains paused because these documentation changes would trigger public GitHub Pages deployment. No protected ref or deployment was changed.
