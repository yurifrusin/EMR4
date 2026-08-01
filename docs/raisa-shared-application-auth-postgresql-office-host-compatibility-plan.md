# Raisa shared application-auth PostgreSQL Office-host compatibility plan

Date: 2026-08-01

Owner: Yuri / GPT Sol

Status: frozen implementation and acceptance contract

Reasoning level: Extra High for the combined database-role, browser-cookie and
real-Office security boundary; High is sufficient for mechanical implementation
and verification inside this contract.

Parent results:

- `raisa_shared_application_auth_office_cookie_compatibility_pass` at PR 70
  head `0b3fe1f965c1171a436676762d6101818b437bae`;
- `raisa_shared_application_auth_operational_hardening_pass` on protected
  `master` at `1af54ae31895e863b447479aeb3b2bbcf0e684b8`.

## 1. Authority and transition boundary

Yuri authorised the smallest application-auth descendant identified by Compass
168: one provider-free, authored-synthetic Office-host exercise through the
already accepted local PostgreSQL persistence, separate deployment LOGIN role,
exact capability-role activation and operationally hardened secure-cookie
transport.

The work may add a task-scoped harness, two fresh development manifests,
deterministic tests, sanitized evidence, ordinary task-branch commits and a
draft pull request. It may create and remove one uniquely named disposable
loopback PostgreSQL database, one task-owned LOGIN role with a runtime-only
generated password and one task-owned NOLOGIN capability role. It may start and
stop the already configured development relay only for the supervised Office
runs.

PR 70 protected integration is not a prerequisite for task-branch development.
It remains paused because a `docs/**` push to `master` automatically invokes the
public GitHub Pages deployment workflow. Protected integration and that
deployment require a separate explicit Yuri decision. This tranche must not
move `master` or `handoff/current`.

## 2. API Spine classification

Application session lifecycle remains an explicit REST command boundary. The
existing seven routes under `/api/v1/application-auth` are the only backend
surface:

- issue CSRF;
- establish one authored-synthetic session;
- validate, rotate and log out that session; and
- issue or redeem the already accepted one-use Word-to-Diary exchange, which
  remains present but is not exercised by this Office-host proof.

The harness must explicitly inject the accepted transport and operational
guard. The product application remains default-off. No GraphQL operation, new
route, OpenAPI behavior change, product read model, appointment, arrival or
document command, migration or second authorization engine is authorised.

## 3. Frozen infrastructure

### 3.1 Disposable database and migrations

The harness creates a uniquely named loopback-only PostgreSQL database from the
accepted local maintenance connection and upgrades it to the existing single
Alembic head. It must not migrate or write the source development database.

The database contains only the accepted five authored-synthetic application-
auth tables, constraints, triggers, RLS policies and exact hash resolver. No
product model or router is mounted or queried.

### 3.2 Login and capability roles

The harness creates one generated task-owned LOGIN role and one generated
NOLOGIN capability role using the accepted contracts. The LOGIN role has no
direct auth-table grant, uses `NOINHERIT`, and has a connection limit equal to
the finite auth pool maximum. Its random password exists only in process
memory.

Every checked-out physical auth connection executes exact `SET ROLE` to the
allowlisted capability role. Acceptance must read back distinct
`session_user`/`current_user`, prove the capability identity, and retain forced
RLS plus the accepted transaction timeouts. Owner access is permitted only for
bounded setup, sanitized aggregate acceptance readback and cleanup.

### 3.3 Existing policy and transport

`ApplicationAuthRuntime` remains the one policy engine;
`RoleScopedPostgresApplicationAuthRuntime` remains its PostgreSQL coordinator;
and `ApplicationAuthTransport` remains the cookie/CSRF boundary. The harness
uses the existing Secure, HttpOnly, SameSite=None, Partitioned `__Host-`
cookies, exact-origin checks, one-use bootstrap registry, atomic rotation,
logout, generic failures, strict one-hop proxy policy, finite rate limiter and
PostgreSQL denial-audit sink without behavior changes.

## 4. Frozen real-host exercise

Installed Word (`word_desktop`) and Word Online (`word_online`) receive
independent authored-synthetic principals, bootstraps, evidence nonces and
browser cookie partitions. Each fresh task-specific Restricted manifest uses
the exact reserved HTTPS development origin.

In each host, one visible user gesture performs ordinary same-origin
`fetch(..., {credentials: "include"})` requests:

1. issue CSRF;
2. create the one-use synthetic session;
3. validate it;
4. rotate the surface bearer and CSRF value atomically;
5. validate the replacement;
6. log out; and
7. issue fresh pre-auth CSRF and prove post-logout validation is HTTP 401.

JavaScript must not read cookies, Office credentials, profile or storage. The
harness must not call a document API, inspect a document, or use bearer,
storage, query-string, second-origin or exchange fallback.

## 5. Acceptance gates

### Gate A - five-source rehydration and Git isolation

- The fresh receipt names all five mandatory sources and passes with worker
  dispatch disabled.
- The task branch starts exactly at PR 70 green head `0b3fe1f9...` while all
  four protected refs remain at `1af54ae3...`.
- The user-owned untracked `docs/branding/raisa/` directory remains untouched,
  unstaged and excluded from every commit and evidence artifact.

### Gate B - deterministic static and route security

- Tests prove the exact route allowlist, fresh manifest identifiers, exact
  origin and surface binding, no-store/CSP pages, one-use bootstraps and closed
  evidence schema.
- Wrong origin, wrong surface, bootstrap replay, CSRF mismatch, logged-out
  bearer reuse and unbounded result submissions fail closed.
- Static scans prove there is no bearer fallback, browser storage, cookie read,
  Office document API, product router, provider client or product database
  access.
- Existing Office-cookie, runtime-role, persistence, operational-hardening,
  API Spine and security regressions remain green.

### Gate C - live local PostgreSQL and role path

- A unique disposable database upgrades to the accepted current head without
  changing the source database.
- A fresh auth connection reports the generated LOGIN role as `session_user`
  and the exact NOLOGIN capability role as `current_user`.
- Two independent Office lifecycles persist through fresh database sessions,
  with exactly two principal-generation rows, two parent sessions, four
  revoked surface rows, zero exchange grants, fourteen lifecycle audit events
  and two retained generic post-logout denial events.
- Each synthetic practice has one parent and two surface rows; a capability-
  scoped fresh read sees only its exact practice.
- Every persisted opaque reference has the accepted SHA-256 shape, and no raw
  bootstrap, parent, surface, CSRF, nonce or other generated secret matches any
  persisted field or durable evidence value.

### Gate D - installed Word

- A real installed-Word taskpane loads from the exact HTTPS origin, reports
  `word_desktop`, and completes the visible lifecycle through PostgreSQL.
- Direct developer debugging with live reload disabled may be used only to
  admit the task-specific manifest and must be stopped afterward.

### Gate E - Word Online

- A real signed-in Word Online taskpane loads from the same exact HTTPS origin,
  reports `word_online`, and completes its independent lifecycle through the
  same bounded database-role path.
- Interaction is limited to a blank authored-synthetic document and the
  taskpane. Cookie stores, unrelated tabs, account identity, tenant and
  document identifiers remain uninspected.

### Gate F - cleanup and residue

- The harness, relay, listeners and developer registration are removed.
- The finite pool is disposed, both generated roles and the disposable
  database are absent, both bootstraps are consumed, and no application session
  remains usable.
- Durable evidence records only closed booleans, counts, generic status and
  claim limits. It records no database or role name, password, URL credential,
  token, cookie, nonce, header, identity, document or patient/clinical value.
- Manifest validation, focused tests, expanded regressions, Ruff, Bandit,
  dependency gates, JSON validation and `git diff --check` pass.

## 6. Evidence labels and artifacts

The combined proof is labelled
`live_local_office_backend_postgres_capability_role`. It is real Office UI to
the task-owned HTTPS relay and local FastAPI/PostgreSQL path, without route
interception. It is not deployed, organisational, real-identity or production
evidence.

Planned artifacts:

- `scripts/raisa_shared_application_auth_postgresql_office_host_compatibility.py`;
- `tests/test_raisa_shared_application_auth_postgresql_office_host_compatibility.py`;
- two manifests and closed evidence under
  `orchestration/continuity/shared-application-auth-postgresql-office-host-compatibility/`;
- the matching security threat-model delta and closeout after every gate.

## 7. Closed boundaries and claim limit

Real EMR4 identity, live user/practice mapping, Microsoft/Office federation,
Office profile or tenant authority, product-derived/patient/health/clinical
data, document reads or writes, application product reads, GraphQL,
appointment/arrival commands, providers, broader cloud/IAM changes,
organisational Office deployment, GitHub Pages deployment, production, release,
public rename, domain, ASIC and trade-mark action remain closed.

A pass can prove only that two independent authored-synthetic Office cookie
lifecycles worked once through the accepted local PostgreSQL, finite LOGIN pool,
exact capability role, forced-RLS and retained-audit path with complete owned
cleanup. It cannot prove real identity, Microsoft federation, every Office or
browser policy, multi-instance abuse resistance, product-data safety,
deployment, production fitness or release readiness.

Until every gate passes, the only truthful result is
`raisa_shared_application_auth_postgresql_office_host_compatibility_in_progress`.
