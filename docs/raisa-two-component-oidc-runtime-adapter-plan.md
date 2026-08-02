# Raisa two-component OIDC runtime-adapter plan

Date: 2026-08-02

Status: authorised provider-free implementation tranche

Parent: `raisa-two-component-oidc-verifier-architecture-revision`

## Outcome sought

Implement the frozen Microsoft federation seam as a route-free, default-off
application service. MSAL 1.37.0 must remain the sole authorization-code
protocol client. Authlib 1.7.2 and JOSE RFC 1.7.4 must independently verify the
raw ID token before the adapter may release a bounded external-principal
result.

## Authority

Yuri authorised this next candidate. This tranche may add the application
adapter behind the frozen ports, a bounded provider-free encrypted attempt
store, normalized audit types, deterministic authored-synthetic fault tests,
API-contract reconciliation, evidence, documentation, continuity artifacts and
necessary task-branch commits.

It may not mount a route, contact Microsoft, use a real tenant or identity,
write database truth, create or change an identity binding, role or application
session, read product data, change cloud/IAM, deploy, release, move a protected
ref or include the concurrent `docs/branding/` work.

## Patch contract

The unsafe path is a protocol result whose MSAL-decoded `id_token_claims` looks
admissible while its raw ID token is forged. Before implementation, a regression
must show that this path cannot import the missing adapter and therefore cannot
be accepted. The completed patch must:

1. create an exact tenant-specific MSAL flow with `scopes=[]`, effective
   `openid profile`, `offline_access` excluded, S256 and `form_post`;
2. keep the entire MSAL flow in a five-minute, bounded, envelope-encrypted
   provider-free store keyed only by an HMAC of state;
3. atomically consume the attempt before one token-exchange invocation;
4. ignore MSAL claims and pass only a transient raw ID token to Authlib;
5. enforce a 16 KiB pre-parse limit, RS256, exact coherent metadata,
   issuer/audience/nonce/time claims, exact `tid`, and nonempty `oid`/`sub`;
6. retain Authlib's one forced JWKS refresh on unknown `kid`, with no fallback;
7. discard access, refresh and raw ID tokens and emit normalized audit only;
8. return no EMR4 authorization, role, binding, session or product data; and
9. remain default-off and absent from `main.py` and every router.

## Acceptance

The tranche passes only if the exploit regression, the 25-case provider-free
fault matrix, package audit, security scanning, API-spine checks and inherited
Microsoft-federation/application-authentication regressions pass. Full-repo
pytest is also run, with any parent-HEAD failure reproduced and dispositioned
exactly rather than hidden.

## Handoff

A pass proves only a dormant repository-local adapter and intercepted/provider-
free semantics. A durable distributed attempt store, route and CSRF/origin
edge, live Microsoft interoperability, real identity, binding resolution,
session issuance, product access and operations each remain later gates.
