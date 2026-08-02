# Raisa provider-free OIDC start/callback transport boundary closeout

Date: 2026-08-02

Result: `provider_free_oidc_start_callback_transport_boundary_pass`

## Outcome

The first of Yuri's three authorised logical descendants passes. EMR4 now has
two default-off mounted Microsoft OIDC transport routes around the accepted
two-component adapter: an exact-origin start command and one strict
provider-shaped callback. The default dependency still returns 404, so the
routes have no runtime authority until an explicit composition root injects
the bounded transport.

## Implemented boundary

- a strict enum-only start request with exact surface origin,
  pre-authentication CSRF cookie/header equality and HMAC-only bounded
  idempotent replay;
- a server-owned adapter call which creates the existing five-minute encrypted
  authorization attempt and returns only the validated Microsoft authorization
  URI and expiry;
- a byte-bounded 12 KiB `application/x-www-form-urlencoded` callback parser
  accepting at most four unique allowlisted keys and rejecting duplicate,
  ambiguous, malformed or alternate-media input;
- exact generic `authentication_failed`/temporary-unavailable JSON errors with
  required normalized denial audit and no supplied-value echo;
- a nonce-bound, third-party-free bridge page with exact-origin `postMessage`,
  fixed enum-only `authentication_verified` content, restrictive CSP,
  no-store/no-cache, no-referrer, nosniff and permissions-policy headers; and
- API Spine versioning which marks start/callback mounted default-off while
  retaining zero admission-grant and application-session authority.

The callback discards the verified provider identifiers at this edge. It
creates no binding, no admission grant, no application session and no cookie.

## Evidence

One unique disposable loopback PostgreSQL database, generated unrecorded LOGIN
credential and exact attempt-table capability role were migrated and wired to
the accepted PostgreSQL authorization-attempt store. A real Uvicorn loopback
socket then served five ordinary HTTP requests through the FastAPI router.

The start returned 201 and exact replay, leaving one encrypted attempt. The
strict callback returned 200, consumed the attempt to zero rows and released
only the fixed enum bridge. Replaying the callback and sending an invalid media
type both returned the same generic 401 body. The response had the exact
no-store, no-referrer, nosniff and restrictive CSP posture, no `Set-Cookie` and
zero matches for state, nonce, verifier, code, token or provider identifiers.

Exactly one synthetic protocol start, one synthetic redemption and one
synthetic verifier call occurred. Provider calls, real identities, bindings,
admission grants, application sessions and product reads were all zero. The
loopback server stopped and the database, LOGIN and capability role were all
proved absent.

## Verification

- disposable live-local HTTP/backend/PostgreSQL acceptance: pass;
- focused transport tests: 17 passed;
- expanded OIDC/federation/shared-auth/API Spine suite: 275 passed;
- current continuity/Compass/handover suite: 36 passed;
- targeted Ruff and compilation: pass;
- targeted application Bandit: no findings;
- `pip check`: no broken requirements;
- `pip-audit -r requirements.txt --desc --progress-spinner off`: no known
  vulnerabilities;
- single Alembic head remains `r7s8t9u0v1w2`; the disposable acceptance
  database upgraded to it and passed `alembic check`; and
- `git diff --check`: pass.

The ordinary development database is behind that head and was deliberately not
mutated. Full repository pytest still stops during collection at the unchanged
parent-HEAD import of removed uppercase `_BERNIE_SESSION_STORE` in
`tests/test_api_spine_confirmation_family_idempotency_integration.py`. This
tranche did not alter that test or the appointments router.

## Side effects

External/provider calls, real identities, identity bindings, admission grants,
application sessions, session cookies, product/patient/clinical reads,
cloud/IAM mutations, deployments, production changes, releases, protected-ref
movements, Pages rebuilds and Dependabot dispositions are all zero. The
user-owned `docs/branding/` directory was not modified, staged, tested, read
into evidence, committed or removed.

## Residual gates

The next preauthorised logical descendant is the provider-free HMAC-only
provider-key binding resolver and short-lived admission-grant boundary. It must
perform a fresh five-source rehydration and freeze its own plan before acting.
It may not create an application session or read product data.

The following preauthorised descendant is atomic one-use grant redemption into
the accepted application-session runtime, also after its own fresh
rehydration. Live Microsoft, real identity, product reads, production secret
custody, hosted database/network policy, distributed abuse resistance,
monitoring/SIEM, cloud/IAM, deployment, protected integration, production and
release remain separately closed.
