# Raisa provider-free OIDC start/callback transport boundary plan

Date: 2026-08-02

Status: authorised implementation tranche

Parent: `raisa-postgresql-oidc-operational-connection-boundary`

## Outcome sought

Mount the accepted Microsoft OIDC adapter behind exact, default-off FastAPI
start and callback protocol routes. Prove the ordinary local HTTP path with the
accepted PostgreSQL attempt runtime and authored-synthetic protocol/verifier
ports, while releasing no binding, admission grant, application session or
product authority.

## Authority

Yuri authorised this fresh gate and the next two logical descendants unless a
material directional choice arises. This tranche may add exact REST schemas,
two default-off routes, bounded start idempotency, exact origin and existing
pre-authentication CSRF admission, strict `form_post` parsing, generic errors,
a restrictive no-store exact-origin bridge page, disposable loopback
PostgreSQL/HTTP acceptance, documentation, continuity and task-branch
publication.

It may not call Microsoft or any provider, use a real tenant or identity,
resolve or create a binding, issue an admission grant or application session,
read product/patient/clinical data, persist a deployment credential, change
cloud/IAM, deploy, release, move a protected ref, rebuild Pages, decide
Dependabot alert 17 or include `docs/branding/`.

## Frozen contract

1. The routes are always represented in OpenAPI but fail closed with 404 until
   a task-scoped `OIDCStartCallbackTransport` dependency is injected. No
   environment flag or implicit global enables them.
2. `POST /api/v1/application-auth/federation/microsoft/start` accepts only the
   exact surface and return-target enums, exact allowlisted `Origin`, the
   existing matching `__Host-emr4-application-csrf`/`X-EMR4-CSRF` pair and one
   bounded `Idempotency-Key`.
3. Start idempotency stores only HMAC references and a bounded response until
   the attempt expires. Same-key shape mismatch denies; capacity and dependency
   failure are generic unavailable results.
4. The server-owned adapter selects tenant, callback and authorization URI. No
   request field can supply tenant, authority, redirect, origin or arbitrary
   return URL.
5. `POST /api/v1/application-auth/federation/microsoft/callback` accepts only
   `application/x-www-form-urlencoded`, at most 12 KiB, four unique allowlisted
   fields and the adapter's existing strict state/error/code bounds. JSON,
   multipart, duplicate keys and extra keys deny before protocol completion.
6. The callback passes the normalized form exactly once to the accepted
   adapter. Authored-synthetic protocol and verifier ports may be injected;
   live network/provider clients remain absent.
7. Successful completion discards verified external identifiers at the
   transport edge and renders only a fixed `authentication_verified` message
   containing surface and return-target enums. It issues no admission grant,
   no application session, no cookie, no product response and no provider detail.
8. The bridge uses one validated nonce-bound inline script, exact target
   origin, no third-party resource and restrictive CSP, frame-ancestor,
   no-store, no-referrer, nosniff and permissions-policy headers. No credential
   appears in URL, storage or HTML.
9. Protocol, validation and identity failures collapse to
   `authentication_failed`; required dependency/audit failure collapses to
   `authentication_temporarily_unavailable`. Supplied values and provider
   descriptions never appear in responses or logs.

## Acceptance

- Default dependencies return 404 with no-store headers.
- A real loopback HTTP server, disposable PostgreSQL attempt table, finite
  LOGIN/capability pool and authored-synthetic protocol/verifier complete one
  start/callback lifecycle.
- Exact origin/CSRF and idempotent replay pass; mismatched replay, malformed or
  oversized form, duplicate/extra fields, wrong content type, replay and
  provider denial fail generically.
- Callback headers and HTML match the restrictive contract, post only to the
  exact stored origin and contain no state, nonce, PKCE, code, token, external
  identifier, database target, password, key/reference or session/grant value.
- No `Set-Cookie`, binding, grant, session, product read, provider call or
  external side effect occurs; disposable database and roles are removed.
- Focused and inherited API/auth/security/continuity checks pass, with the
  unchanged repository-wide collection barrier reported exactly.

## Handoff

The first preauthorised logical descendant is the provider-free HMAC-only
binding resolver and short-lived admission-grant persistence boundary. The
second is the provider-free atomic admission-grant redemption bridge into the
accepted application-session runtime. Each requires fresh five-source
rehydration and stops if its predecessor exposes a material fork.
