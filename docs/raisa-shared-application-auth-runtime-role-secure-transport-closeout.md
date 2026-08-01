# Raisa shared application-auth runtime-role and secure transport closeout

Date: 2026-08-01

Result: `raisa_shared_application_auth_runtime_role_secure_transport_pass`

## Outcome

The separately authorised repository-local runtime-role and secure
authored-synthetic transport tranche passes. The accepted shared-auth policy
engine and PostgreSQL unit of work now sit behind one default-off FastAPI
surface and one exact least-privilege capability-role contract.

This is not live EMR4 authentication. The only identities and practices used
were task-created authored-synthetic fixtures in a uniquely named disposable
local database. No external identity, Microsoft or Office identity authority,
product-derived data or production path was added.

## Durable boundary

- Alembic revision `p5q6r7s8t9u0`, descending from accepted revision
  `o4p5q6r7s8t9`, adds one bounded `SECURITY DEFINER` resolver. It accepts only
  a `parent`, `surface` or `exchange` SHA-256 reference, has an empty
  `search_path`, returns at most one authored-synthetic principal and grants no
  authorization by itself. Public execution is revoked.
- The parameterised runtime capability role is `NOLOGIN`, `NOSUPERUSER`,
  `NOCREATEDB`, `NOCREATEROLE`, `NOINHERIT`, `NOREPLICATION` and
  `NOBYPASSRLS`. It receives only schema usage, the frozen operation matrix on
  five auth tables, audit-sequence use and exact resolver execution. It has no
  privilege on any of the 50 observed product tables.
- Every role-scoped transaction sets bounded statement, lock and
  idle-in-transaction timeouts. It resolves an already hashed reference,
  establishes the transaction-local practice context and then delegates to
  the accepted single policy engine and persistence coordinator.
- The router is mounted at `/api/v1/application-auth` but closed by default.
  With no explicitly injected authored-synthetic transport, all seven routes
  return the same no-store unavailable response before a database session can
  open. No environment variable enables it.
- The session and CSRF cookies are `__Host-` scoped, `Secure`, `HttpOnly`,
  `Path=/`, omit `Domain`, use `SameSite=None` and carry `Partitioned` on set
  and deletion. Parent and surface bearer values never appear in JSON; the
  short-lived exchange code is the only response bearer.
- Exact HTTPS origins and independent cookie/header CSRF equality guard the
  protocol. Malformed and authentication failures collapse to generic 401,
  origin/CSRF failures to generic 403, default-off to generic 404, and
  persistence or required-audit unavailability to generic 503.

## Acceptance evidence

One uniquely named loopback database and one uniquely named cluster capability
role passed full migration and transport acceptance:

- upgrade from accepted parent to `p5q6r7s8t9u0`, exact current head,
  downgrade, re-upgrade and Alembic drift checking all passed;
- the resolver was security-definer, stable, empty-search-path, fixed-kind,
  SHA-256 bounded, limit-one and unavailable to `PUBLIC`;
- every required auth-table, audit, sequence, schema and resolver privilege was
  true, every forbidden privilege was false, and product privilege hits were
  zero across 50 product tables;
- absent practice context exposed zero auth rows, own context exposed the
  expected five table families, and foreign context exposed no own-practice
  rows;
- exact-origin and CSRF denial matrices passed without runtime entry;
- one-use synthetic login, fresh validation, atomic surface/CSRF rotation,
  Word-to-native-Diary issue/redeem and logout passed through the real FastAPI
  router and role-scoped PostgreSQL coordinator;
- replayed bootstrap and exchange values, the old rotated/logged-out bearer,
  and wrong origin/state/nonce/verifier bindings all returned the same generic
  external denial;
- a forced audit insert outage returned generic 503, released no new cookie and
  left all state and audit counts unchanged;
- 31 raw bootstrap, parent, surface, exchange, CSRF, state, nonce and verifier
  values matched no persisted row or evidence field; and
- the exact database and capability role were dropped and proved absent.

All focused shared-auth cases, the expanded no-`conftest` auth/API Spine/host/
Continuity/Compass matrix and the serial legacy database-fixture auth suite
pass. Python compilation, Ruff, JSON/YAML validation, Alembic head/current/
drift checking and whitespace verification pass.

Every recorded external and product side-effect count is zero: no provider,
external-identity or Microsoft/Office identity call; cloud/IAM mutation;
product, patient or clinical read; appointment/arrival command; microphone
capture; document mutation; deployment; or production change occurred.

## Security disposition

The accepted runtime role removes table-owner operation from the application
transport proof. The narrow hash resolver solves the pre-context bootstrap
without granting broad table visibility; forced RLS continues after the exact
practice is established. Generic errors do not expose the detailed typed
runtime denial retained in required metadata audit.

Cookie mutation occurs only after the database coordinator succeeds. Rotation
revokes the old surface reference and creates its replacement atomically;
logout durably revokes before cookie expiry. The one-use bootstrap registry and
accepted exchange semantics close replay in this bounded local transport.

The proof does not make PostgreSQL custom settings a security boundary against
arbitrary SQL. Deployment login credential isolation, connection-pool and
proxy behavior, rate limiting, retained unauthenticated-denial audit, CSP and
supply-chain controls remain unresolved operational work.

## Preserved closed boundaries

Protected holdouts and raw historical Diary material were not inspected. The
frozen Sydney development service remains unchanged at revision
`raisa-office-web-dev-00006-xf9` and digest
`sha256:8e06f07e4efd393f38275348d8bd7b136e664c2797c399a89207b66116839324`;
its zero-authority posture and resource limits were not broadened.

Real EMR4 identities or practices, external identity providers,
Microsoft/Office federation, product-derived or patient/health/clinical/
historical data, GraphQL and application product reads, appointment or arrival
commands, microphone capture, document mutation, providers, cloud/IAM changes,
organisational Office deployment, production and release remain closed.

No commit, push, pull request, staging operation or protected-ref movement was
performed.

## Claim limit and next gate

This result proves one exact local capability-role contract, narrow hash
bootstrap, default-off non-enumerating synthetic routes, exact-origin and CSRF
enforcement, partitioned Secure HttpOnly cookie carriage, atomic rotation and
logout, continued database single-use and complete disposable cleanup. It does
not prove real identity verification, live user/practice mapping, real Word or
Word Online third-party-cookie compatibility, production login isolation,
internet-scale abuse resistance, product-data safety, deployment, production
fitness or release readiness.

The next safe candidate is a separately authorised repository-local,
provider-free operational-hardening architecture for deployment-role
isolation, proxy trust, rate limiting, retained denial audit and bounded pool
behavior, still using only authored-synthetic identity state and keeping real
identity, Office federation and every product read closed.

The required non-PHI Pushover closeout notification was attempted with the
sprint engine paused for that fresh authority and failed with
`no active devices to send to`; nothing was delivered.
