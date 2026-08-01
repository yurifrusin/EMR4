# Raisa Shared Application Authentication Operational Hardening Plan

Status: frozen implementation and acceptance contract
Authority: Yuri, 2026-08-01
Parent result: `raisa_shared_application_auth_runtime_role_secure_transport_pass`
Parent coordinates: Continuity 184 / Compass 165

## Decision and boundary

This descendant is authorised only for repository-local, provider-free,
authored-synthetic operational hardening of the accepted default-off shared
application-auth transport. It may implement and prove:

1. separation of a deployment login principal from the existing NOLOGIN
   PostgreSQL capability role;
2. an explicit trusted-proxy contract for the client identity used by abuse
   controls;
3. bounded, deterministic per-client transport rate limiting;
4. retained, metadata-only audit of unauthenticated transport denials; and
5. an explicitly bounded SQLAlchemy connection pool and database timeouts.

The accepted runtime policy engine, PostgreSQL transaction boundary, seven
default-off routes, exact-origin checks, CSRF checks, cookies, rotation,
logout and one-use exchange remain the only application-auth behavior. This
plan adds no identity source and grants no product read or command.

## Closed boundaries

The following remain closed and must not be inferred from a passing result:

- real EMR4 identity or identity-to-practice mapping;
- Microsoft, Office or any other external identity federation;
- product-derived, patient, health, clinical or historical data;
- appointment, arrival, document, microphone or external-system commands;
- provider/model calls or network egress beyond disposable local PostgreSQL;
- browser/Office third-party-cookie compatibility;
- cloud or IAM mutation, deployment, production, release, commit, push, pull
  request or protected-ref movement.

## Frozen architecture

### Deployment role isolation

The existing `emr4_application_auth_runtime_*` role remains a NOLOGIN
capability role holding the exact table, sequence and resolver grants. A
separate `emr4_application_auth_login_*` role may authenticate, has
`NOINHERIT`, receives no direct application-table grants and is limited to the
bounded connection count. The pool must execute exact `SET ROLE` to the
allowlisted capability role for every new physical connection. Disposable
acceptance must prove `session_user` is the login role, `current_user` is the
capability role, the login role alone cannot read auth state, and neither role
can bypass RLS or mutate audit evidence.

Repository SQL is credential-free. The structural login-role contract creates
an inert `PASSWORD NULL` role; supplying or rotating a deployment secret is a
future deployment control and is not authorised here. Acceptance may assign
one generated disposable password without recording it and must drop both
roles and the database.

### Proxy trust

Forwarded client identity is accepted only when the direct peer belongs to an
explicit allowlist of IP networks. This tranche supports one exact trusted
proxy hop: one canonical `X-Forwarded-For` address and
`X-Forwarded-Proto: https`. Standard `Forwarded`, multiple-hop/comma chains,
malformed values, forwarded headers from an untrusted peer and non-HTTPS
forwarding fail closed. With no forwarded headers, a non-proxy direct peer is
used; a configured trusted proxy missing the complete pair fails closed. The
resolver affects only abuse-control identity; it grants no auth or origin
authority.

### Rate limiting

One thread-safe fixed-window limiter protects the seven auth routes before
body or credential processing. Keys are HMAC-derived from the canonical client
address and are never persisted or returned. Configuration is bounded by
validated request/window limits and a maximum live-key count; expired entries
are pruned and least-recent entries are evicted at capacity. The first blocked
request per key/window requires a retained audit event, while subsequent
blocked requests remain 429 without unbounded audit amplification.

This local limiter is per process. Passing it proves the repository contract,
not distributed or production abuse resistance. Any multi-instance deployment
requires a separately reviewed shared/edge limiter.

### Retained unauthenticated-denial audit

The operational guard writes a generic `auth.authorization_denied` event to
the accepted append-only application-auth audit table for malformed request,
origin/CSRF, authentication and first-per-window rate-limit denials. The row
contains only fixed action/surface/category metadata, a generated bounded
correlation ID and a process-keyed HMAC reference. It contains no IP address,
forwarded header, origin, cookie, CSRF value, bootstrap value, exchange value,
state, nonce, PKCE value, request body or exception text.

The audit uses one fixed authored-synthetic transport-audit practice context.
If a required denial audit cannot commit, the request remains denied and is
collapsed to the existing generic 503 response. No successful auth state is
created. Retention duration, archival and production monitoring remain closed.

### Bounded pool

The auth pool factory must set explicit `pool_size`, `max_overflow`,
`pool_timeout`, `pool_recycle`, pre-ping, LIFO and rollback-on-return behavior.
The configured pool maximum must not exceed the login role's connection limit.
Every auth transaction retains the accepted statement, lock,
idle-in-transaction and RLS settings. Pool exhaustion must be bounded in time
and surface only the generic unavailable error.

## HTTP contract delta

- Rate-limit denial is HTTP 429 with `request_rate_limited`, `Retry-After` and
  the existing no-store headers.
- A required denial-audit failure is HTTP 503 with
  `authentication_temporarily_unavailable`.
- Existing 401, 403, 404 and 503 bodies remain generic.
- No response or log may echo submitted authentication material or proxy
  headers.

## Acceptance gates

Acceptance requires all of the following:

- deterministic unit tests for strict role names, proxy parsing, spoof/chain
  rejection, limiter bounds, first-block audit coalescing and HMAC-only data;
- route tests for 429, retained 401/403 denial events, required-audit outage,
  no-store/error consistency and unchanged happy-path cookies/exchange;
- disposable PostgreSQL proof using independent owner and deployment-login
  sessions, exact `session_user`/`current_user`, role grant isolation, bounded
  pool checkout timeout, append-only/RLS behavior and retained denial rows;
- raw-value absence across database rows, emitted evidence and error bodies;
- exact database and role absence after cleanup, with zero provider, product,
  cloud, identity, deployment and external side effects;
- focused tests, expanded no-`conftest` regressions, serial legacy database
  tests, API Spine artifact tests and repository boundary tests all pass;
- a preacceptance five-source Ariadne receipt and an independent evidence
  review before any result is described as accepted.

## Evidence and closeout artifacts

- `docs/security/raisa-shared-application-auth-operational-hardening-threat-model-delta.md`
- `app/services/application_auth_operational_hardening.py`
- `app/services/application_auth_operational_database.py`
- `scripts/raisa_shared_application_auth_operational_hardening_acceptance.py`
- `tests/test_raisa_shared_application_auth_operational_hardening.py`
- `orchestration/continuity/raisa-shared-application-auth-operational-hardening/live-local-backend-postgres-operational-evidence.json`
- `docs/raisa-shared-application-auth-operational-hardening-closeout.md`

Until every gate passes, the only truthful result is
`raisa_shared_application_auth_operational_hardening_in_progress`.
