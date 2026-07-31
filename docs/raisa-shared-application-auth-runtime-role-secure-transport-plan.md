# Raisa shared application-auth runtime-role and secure transport plan

Date: 2026-08-01

Owner: Yuri / GPT Sol

Status: `authorised_repository_local_provider_free_authored_synthetic_implementation`

Reasoning level: Extra High for the database-role, bootstrap, cookie, CSRF and
route-security choices; High is sufficient for mechanical implementation and
verification inside this frozen plan.

## 1. Authority

This is the separately authorised descendant of
`raisa_shared_application_auth_postgresql_persistence_pass`. Yuri authorised
the exact Compass 164 candidate `shared-application-auth-runtime-role-secure-transport`:
a repository-local, provider-free least-privilege PostgreSQL runtime role and
secure authored-synthetic session transport covering token-to-practice
bootstrap, non-enumerating login/exchange failures, CSRF, opaque Secure
HttpOnly cookie handling, rotation and logout while every product read remains
closed.

The authority permits one database-scoped resolver migration, an exact
parameterised runtime-role grant contract, default-off FastAPI route and schema
code, authored-synthetic bootstrap credentials, cookie/CSRF behavior,
disposable local PostgreSQL role/database writes, deterministic route and
browser-protocol tests, security evidence and continuity closeout. It does not
permit live EMR4 users or practices, external identity, Microsoft or Office
identity authority, product-derived data, patient/health/clinical/historical
data, providers, cloud/IAM changes, deployment, organisational Office rollout,
production, release, commit, push or pull request.

## 2. Objective

Prove one bounded transport above the accepted backend-owned policy engine and
PostgreSQL unit of work:

1. a runtime capability role can use only the five authored-synthetic auth
   tables, the audit identity sequence and one exact token-reference resolver;
2. token-to-practice bootstrap works without broad pre-context table `SELECT`;
3. all post-bootstrap table access remains forced-RLS and transaction-scoped;
4. one-use synthetic bootstrap credentials establish a surface session without
   returning parent or surface bearer values in a response body;
5. browser authority is carried only in `__Host-` Secure HttpOnly partitioned
   cookies, with exact-origin checks and an independent CSRF cookie/header pair;
6. validate, explicit surface-bearer rotation, cross-surface issue/redeem and
   logout converge on the accepted backend runtime and database transaction;
7. externally visible failures use bounded generic status/body classes while
   detailed reason codes remain required metadata audit only; and
8. a uniquely named disposable database and every task-created role disappear
   completely after acceptance.

## 3. Frozen material choices

### 3.1 One policy engine and a child transport extension

`ApplicationAuthRuntime` remains the single implementation of identity-session
binding, expiry, generation revocation, role/practice scope, Word-to-Diary
exchange and required audit rules. `PostgresApplicationAuthRuntime` remains the
accepted same-transaction persistence coordinator.

The new role-scoped coordinator may add only two database hooks: transaction
timeouts before bootstrap and transaction-local practice context after an
exact principal key is established. An `ApplicationAuthTransportRuntime`
subclass may add one atomic same-surface rotation operation. Rotation must
revoke the old surface reference, create one replacement under the same parent
and generation, and record the existing typed `session_refreshed` and
`surface_bound` audit event families before state mutation. It must not add a
second authorization engine.

### 3.2 Database-scoped token bootstrap

Alembic adds one `SECURITY DEFINER` function with an empty `search_path` and an
exact allowlist of `parent`, `surface` and `exchange` reference kinds. It accepts
only a `sha256:` reference and returns at most the matching synthetic
`(user_ref, practice_ref)` pair. It performs no expiry, role or authorization
decision and grants no product-table access. Public execution is revoked.

The role-scoped coordinator calls the function only for an already hashed
opaque value, sets `app.current_practice_ref` transaction-locally from the
returned row, locks the exact principal-generation row and then delegates to
the accepted runtime. A missing reference becomes the same generic transport
failure as any invalid, expired, revoked or mismatched session.

The custom RLS setting remains defense in depth against application defects;
it is not claimed to resist a malicious database principal that can execute
arbitrary SQL. The capability role, parameterized queries, exact resolver and
absence of direct product privileges form the enclosing boundary. Live EMR4
identity mapping remains a later migration and authority decision.

### 3.3 Runtime capability role contract

PostgreSQL roles are cluster-scoped, so Alembic must not create or drop a fixed
cluster role. A repository-local parameterised grant contract defines a
`NOLOGIN`, `NOSUPERUSER`, `NOCREATEDB`, `NOCREATEROLE`, `NOREPLICATION`,
`NOBYPASSRLS` capability role. Acceptance instantiates it under a unique
task-owned name and removes it after the disposable database is dropped.

The role receives only:

- `USAGE` on schema `public`;
- `SELECT`, `INSERT` and `UPDATE` on principal, parent, surface and exchange
  tables;
- `SELECT` and `INSERT` on the append-only audit table;
- `USAGE` and `SELECT` on the audit identity sequence; and
- `EXECUTE` on the exact resolver function.

It receives no `DELETE`, `TRUNCATE`, `REFERENCES`, `TRIGGER`, schema `CREATE`,
product-table privilege, role administration or RLS bypass. A deployment login
role and secret remain external operational work; acceptance uses `SET ROLE`
from the local disposable-database owner and does not claim login credential
isolation.

Each role-scoped transaction sets bounded statement, lock and
idle-in-transaction timeouts before any lookup. It performs no network,
provider, Office, browser, file, subprocess or human work while locked.

### 3.4 Default-off synthetic transport

The router is mounted under `/api/v1/application-auth` but its transport
dependency is closed by default. Without an explicitly injected authored-
synthetic transport, every endpoint returns the same unavailable response and
does not open a database session. No environment variable silently enables it.

The accepted route set is:

- `POST /csrf` — exact-origin pre-authentication CSRF challenge;
- `POST /synthetic/session` — one-use authored-synthetic bootstrap login;
- `POST /session/validate` — fresh backend validation and bounded role context;
- `POST /session/rotate` — atomic surface-bearer and CSRF rotation;
- `POST /session/logout` — revoke the presented surface session and clear both
  cookies;
- `POST /exchange/issue` — authenticated Word-to-native-Diary exchange issue;
  and
- `POST /exchange/redeem` — target-origin, PKCE/state/nonce and CSRF-gated
  single-use redemption that establishes a target cookie.

There is no product read, GraphQL operation, appointment command, document
operation or provider call behind these routes.

### 3.5 Browser cookie and CSRF contract

The browser authority cookie is `__Host-emr4-application-session`. The CSRF
cookie is `__Host-emr4-application-csrf`. Both are `Secure`, `HttpOnly`,
`Path=/`, have no `Domain`, use `SameSite=None` and carry `Partitioned` so Word
Online, desktop WebView and top-level native Diary receive separate browser
partitions. This is a standards-shaped repository proof; real Office cookie
support remains a later supervised compatibility gate.

The raw surface bearer appears only in the session cookie. Parent bearers never
leave the server. The CSRF value appears in its HttpOnly cookie and once in a
`Cache-Control: no-store` response body so the same-origin client can retain it
in memory and send it as `X-EMR4-CSRF`. Every authority-changing request
requires exact constant-time header/cookie equality plus an exact allowlisted
`Origin`. Pre-authentication login and redemption first require `/csrf`.

Login, exchange redemption and explicit rotation replace both cookies. Logout
revokes the database surface record before expiring both cookies. Cookie
deletion retains all security attributes. Responses set `Cache-Control:
no-store`, `Pragma: no-cache` and `Referrer-Policy: no-referrer`.

### 3.6 Non-enumerating failure closure

Pydantic bounds all request fields before runtime calls. Invalid bootstrap
credentials, unknown/revoked/expired sessions, invalid exchanges and binding
mismatches map to one `401 application_authentication_failed` response. Origin
or CSRF failures map to one `403 request_not_admitted` response. Required-audit
or database unavailability maps to one `503 authentication_temporarily_unavailable`
response. Internal runtime reason codes, principal references and supplied
values never appear in response bodies or headers.

This proves response-shape non-enumeration, not constant-time database behavior
or internet-scale rate limiting. Rate limits and an external unauthenticated
security-event sink remain operational gates before deployment.

## 4. Acceptance gates

### Gate A — five-source receipt and Git boundary

- A fresh passing receipt names all five mandatory sources and disables worker
  dispatch.
- Required branch, HEAD, upstream, worktrees and protected refs remain exact.
- All accepted uncommitted parent artifacts and unrelated user changes remain
  preserved and unstaged.

### Gate B — migration and role contract

- A fresh disposable database passes upgrade from `o4p5q6r7s8t9` to the new
  single head, downgrade, re-upgrade, exact current and Alembic drift checks.
- The resolver is security-definer, empty-search-path, public-execute revoked,
  fixed-kind and hash-bounded.
- A unique task role has exactly the positive privileges above and every
  forbidden privilege is false.
- With the role active, no context sees zero state; a valid opaque reference
  resolves one principal, binds one practice and cannot expose another
  practice or any product table.

### Gate C — secure route and cookie protocol

- The default application remains closed and opens zero database sessions.
- Exact HTTPS origins for desktop Word, Word Online and native Diary pass;
  missing, `null`, path-bearing, HTTP and foreign origins fail identically.
- Every set and delete cookie has the exact `__Host-`, Secure, HttpOnly,
  Path=/, no-Domain, SameSite=None and Partitioned attributes.
- Parent/surface bearers never enter a JSON body, URL, log, audit free text or
  evidence artifact; the one short-lived exchange code is the only admitted
  response bearer.
- Missing, mismatched and replayed pre-auth or authenticated CSRF probes fail
  without state mutation.

### Gate D — complete lifecycle and failure closure

- A one-use synthetic bootstrap creates a Word session; replay gets the same
  generic failure as an unknown credential.
- Validate returns only bounded synthetic role context and refreshes through
  the accepted policy engine.
- Rotate invalidates the old cookie immediately, admits the replacement and
  rotates CSRF atomically.
- Issue/redeem creates one native-Diary cookie; replay, wrong origin, state,
  nonce or verifier all share the generic external denial.
- Logout revokes the presented surface and expires both cookies; the old
  cookie remains denied after a fresh database session.
- Forced audit failure produces 503 and leaves cookies, state and audit
  unchanged.

### Gate E — cleanup and regressions

- Raw bootstrap, parent, surface, exchange, CSRF, state, nonce and verifier
  values match no persisted field or evidence artifact.
- The unique database and every task-created role are absent after acceptance.
- Focused role/transport, persistence/runtime/architecture, legacy auth, API
  Spine, Continuity and Compass tests pass in their appropriate serial modes.
- Compilation, Ruff, JSON/YAML validation, Alembic head/current/drift and
  `git diff --check` pass.

## 5. Evidence labels

Direct FastAPI/TestClient-to-role-scoped PostgreSQL operation is labelled
`live_local_backend_postgres_transport`. It is not browser-rendering evidence,
deployed evidence or production evidence. Cookie semantics are verified from
the real Starlette response headers and HTTPS client cookie jar without route
interception.

## 6. Closed boundaries

External identity providers, Microsoft/Office identity authority, live EMR4
users or practices, product-derived or patient/health/clinical/historical data,
application product reads, GraphQL, appointment/arrival commands, microphone
capture, document mutation, providers, cloud/IAM changes, organisational Office
deployment, production and release remain closed.

## 7. Candid claim limit

A pass can prove an exact local capability-role contract, narrow hash bootstrap,
default-off non-enumerating synthetic routes, exact-origin and CSRF enforcement,
partitioned Secure HttpOnly cookie carriage, atomic rotation/logout, continued
database single-use and complete disposable cleanup. It cannot prove real
identity verification, live user/practice mapping, Office third-party-cookie
compatibility, production login credential isolation, rate limiting, retained
unauthenticated audit, product-data safety, deployment, production fitness or
release readiness.

