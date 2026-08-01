# Raisa shared application-authentication PostgreSQL persistence closeout

Date: 2026-08-01

Result: `raisa_shared_application_auth_postgresql_persistence_pass`

## Outcome

The separately authorised PostgreSQL persistence and migration tranche passes.
The accepted shared-auth policy engine now has one route-free durable adapter
whose authored-synthetic parent/surface sessions, principal generation,
single-use exchange and required metadata audit share one PostgreSQL
transaction.

This is not live authentication. No login or exchange route, cookie, external
identity, Microsoft or Office authority, runtime database role or product-data
read was added.

## Durable boundary

- Alembic revision `o4p5q6r7s8t9`, descending from the previous single head
  `n3o4p5q6r7s8`, adds five normalized tables for principal generation, parent
  sessions, surface sessions, exchange grants and typed metadata audit.
- The schema accepts only `authored_synthetic` rows and `synthetic-` identity
  references. It has no foreign key or query to EMR4 users, practices,
  practitioners, patients, appointments, consultations or clinical records.
- Opaque parent, surface, exchange, state and nonce values reach PostgreSQL
  only as `sha256:` references. PKCE retains the S256 challenge and never the
  verifier.
- Every operation inserts-if-absent and locks the exact composite
  `(practice_ref, user_ref)` principal-generation row before hydrating state.
  The accepted `ApplicationAuthRuntime` remains the only policy engine.
- Required audit rows flush before state persistence, and audit plus state
  commit or roll back together. Known denials may commit only their required
  typed denial audit.
- Forced row-level security applies to all five tables. State policies require
  an exact practice context; audit permits only exact-practice select and
  insert. No durable privilege grant or runtime role was created.
- Database triggers reject audit update/delete, generation rollback or skips,
  and clearing or rewriting a consumed exchange.

## Acceptance evidence

One uniquely named loopback database passed full `upgrade head`, downgrade to
`n3o4p5q6r7s8`, re-upgrade, exact-current-head inspection and `alembic check`
with no new upgrade operations. ORM and migrated columns match for all five
tables; five forced-RLS tables, six policies, four trigger events, 61
constraints and 20 indexes were observed.

The `live_local_backend_postgres` exercise then proved:

- a Word desktop session validates after the creating SQLAlchemy session and
  coordinator have been discarded;
- one issued Word-to-Diary exchange was redeemed concurrently through two
  independent SQLAlchemy sessions, producing exactly one target session and
  one terminal `exchange_already_consumed` denial;
- the target Diary binding validates after restart, while a later principal
  generation advance remains fail closed after restart;
- a forced audit-insert outage returns `required_audit_unavailable` and leaves
  every state and audit count unchanged;
- audit mutation, generation rollback/skip and exchange-consumption
  reset/rewrite each fail at PostgreSQL with SQLSTATE `55000`;
- a transactional `NOLOGIN`, `NOSUPERUSER`, `NOBYPASSRLS` role sees zero rows
  without context, sees all five own-practice table families with exact
  context, sees and updates zero foreign-practice rows, cannot insert a foreign
  row, and is absent after rollback;
- seven issued raw values match none of the 20 persisted rows scanned across
  all five tables; and
- the exact acceptance database was terminated, dropped and proved absent.

All 60 focused shared-auth cases pass. The corrected expanded 156-case
no-`conftest` auth, API Spine, dual-host, Clinician One, Word companion,
Continuity and Compass suite passes. The 12 legacy database-fixture auth cases
also pass serially. Python compilation, Ruff, JSON validation, Alembic drift
checking and whitespace verification pass.

Every recorded external/product side-effect count is zero: no provider or
external-identity call, Microsoft/Office identity access, cloud/IAM mutation,
product or clinical read, appointment/arrival command, microphone capture,
document mutation, deployment or production change occurred.

## Security disposition

The principal row lock supplies the cross-process serialization that the
in-memory parent could not prove. Database single-use, same-transaction audit
and guard triggers close the accepted replay, crash-consistency and rollback
risks for this bounded local adapter. Forced RLS and composite practice keys
add defense in depth without claiming a live runtime-role design.

The route-free coordinator currently performs privileged hash lookup before it
knows a practice. A later live design must solve that bootstrap using a
dedicated least-privilege runtime role or a separate lookup boundary; this pass
does not treat table-owner or superuser access as acceptable production
posture. Retention, backup/restore, purge, statement/lock timeouts, pooling and
external audit delivery also remain unresolved operational decisions.

## Preserved closed boundaries

The accepted in-memory runtime source remained byte-stable; its historical
evidence was not regenerated or rewritten. Protected holdouts and raw
historical Diary material were not inspected.

The frozen Sydney development service remains unchanged at revision
`raisa-office-web-dev-00006-xf9` and digest
`sha256:8e06f07e4efd393f38275348d8bd7b136e664c2797c399a89207b66116839324`.
Its zero-authority posture and resource limits were not broadened.

Provider calls, external identity, Microsoft/Office authority, product-derived
or patient/health/clinical/historical data, live login, routes, cookies,
application product reads, appointment or arrival commands, microphone
capture, document mutation, organisational Office deployment, cloud/IAM
changes, production and release remain closed.

## Claim limit and next gate

This result proves reversible local schema creation, normalized hash-only
authored-synthetic persistence, principal-row serialization, database-level
single-use exchange, same-transaction metadata audit, practice-RLS controls and
complete disposable cleanup. It does not prove live identity establishment,
secure browser transport, a least-privilege runtime database role, current
product-role reload, retention/backup, multi-region behavior, product-data
safety, deployment, production fitness or release readiness.

The next safe candidate is a separately authorised, repository-local and
provider-free runtime database-role plus secure session-transport architecture
tranche. It should resolve token-to-practice bootstrap, least privilege,
non-enumerating route errors, CSRF, opaque Secure HttpOnly cookie or same-origin
BFF handling, rotation and logout while continuing to use only
authored-synthetic identities and keeping every product read closed.

The required non-PHI Pushover closeout notification was attempted with the
sprint engine paused for that fresh authority and failed with
`no active devices to send to`; nothing was delivered.
