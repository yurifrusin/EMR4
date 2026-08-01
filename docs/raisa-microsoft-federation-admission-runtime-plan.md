# Raisa Microsoft-federation admission runtime plan

Date: 2026-08-01

Owner: Yuri / GPT Sol

Status: `authorised_route_free_provider_free_authored_synthetic_implementation`

Parent result: `raisa_real_identity_microsoft_federation_boundary_architecture_pass`

## 1. Authority and objective

This is the first of the two logical descendants explicitly authorised with the parent architecture. It may implement one default-off, route-free, provider-free, in-memory admission policy for authored-synthetic Microsoft assertion evidence, exact authored-synthetic bindings, synthetic internal principal state and required metadata audit.

It must prove that the frozen architecture can be represented as code without adding Microsoft discovery, token parsing or cryptography, a browser/login/callback route, application-session creation, a product service, database access or real identity data.

## 2. Frozen implementation boundary

- The input is `SyntheticMicrosoftAssertionEvidence`, explicitly labelled `authored_synthetic` and `synthetic_oidc_verifier`. It is not a JWT, ID token, access token or claim dictionary.
- The runtime repeats the security-relevant admission checks; it does not claim to verify cryptography.
- Configuration is disabled by default and accepts only a `.invalid` tenant-specific synthetic issuer and synthetic tenant/audience references.
- Mapping is exact on provider, synthetic tenant and synthetic object ID. The store returns all matches so ambiguity cannot be hidden by `first()` behavior.
- The internal principal store supplies only active flags and synthetic user/practice references. It supplies no role, practitioner, capability or product record.
- The return value contains at most binding reference/version and user/practice references, with `authorization_granted=false` and `session_created=false`.
- A minimum 256-bit injected key creates versioned HMAC-SHA-256 audit references. Raw tenant/object/email/Office context does not enter audit.
- Required audit occurs before the principal candidate is returned. Audit failure overrides an otherwise valid admission with a 503-style error and no principal.
- No FastAPI/GraphQL router may import the module.

## 3. Acceptance gates

1. All 22 parent architecture cases produce the same exact decision and reason.
2. Exactly one case admits and returns a bounded unauthorised, session-free principal candidate.
3. Default-off, tenant/account/protocol/token/binding/principal failures deny generically.
4. Required audit failure returns an error and no candidate.
5. Audit contains a keyed reference and no raw tenant, object, subject, email or Office value.
6. The module imports no HTTP, socket, Microsoft, JWT, FastAPI, SQLAlchemy, subprocess or product service.
7. Every app router remains free of the runtime import.
8. Provider, database, product, session, cloud/IAM and deployment side-effect counts remain zero.

## 4. Closed boundaries

Live Microsoft calls, real token validation, real identifiers, routes, cookies, application sessions, binding writes, database access, product/internal user reads, role or clinician authorization, cloud/IAM change, deployment, production and release remain closed.

## 5. Claim limit and next gate

A pass proves one route-free in-memory implementation of the frozen synthetic admission policy and audit-before-release behavior. It does not prove a live verifier, durable uniqueness or revocation, cross-process behavior, real principal reload, session creation or product authorization.

The next already-authorised descendant is reversible authored-synthetic PostgreSQL binding and metadata-audit persistence in a uniquely named disposable local database. It must use injected keyed references, add no route, grant no durable runtime role and leave every existing database untouched.
