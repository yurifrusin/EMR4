# Raisa shared application-authentication PostgreSQL persistence plan

Date: 2026-08-01

Owner: Yuri / GPT Sol

Status: `authorised_repository_local_postgresql_authored_synthetic_implementation`

Reasoning level: Extra High for the frozen migration, durable-session and
security choices; High is sufficient for mechanical implementation and
verification inside this plan.

## 1. Authority

This is the separately authorised persistence descendant of
`raisa_shared_application_auth_runtime_foundation_pass`. Yuri authorised the
exact Compass 163 candidate for a PostgreSQL schema/migration and transaction
boundary covering parent and surface sessions, principal generation,
single-use exchange and metadata-only audit using disposable authored-synthetic
fixtures.

The authority permits repository schema/model/service changes, a reversible
Alembic migration, disposable local PostgreSQL databases, authored-synthetic
test writes, deterministic tests, security controls and provider-free evidence.
It does not permit a FastAPI or GraphQL route, cookie, external identity,
Microsoft or Office authority, product-derived read, patient or clinical data,
cloud/IAM change, deployment, production, release, commit, push or pull request.

## 2. Objective

Re-establish the accepted runtime foundation durably by proving that:

1. only SHA-256 references for opaque parent, surface, exchange, state and
   nonce material reach PostgreSQL;
2. parent/surface session state, principal generation and exchange state
   survive a fresh database session;
3. one PostgreSQL transaction contains each admitted state mutation and its
   required metadata audit batch;
4. all operations for one principal serialize on one principal-generation row;
5. concurrent exchange redemption across independent database sessions admits
   exactly one consumer;
6. an audit insert failure rolls back every state mutation in the operation;
7. practice-scoped row-level security fails closed without exact context and
   hides another practice; and
8. migration upgrade, downgrade and re-upgrade pass on a disposable database
   that is removed completely after acceptance.

## 3. Frozen material choices

### 3.1 One policy engine, PostgreSQL unit of work

`ApplicationAuthRuntime` remains the single implementation of the frozen
session, expiry, binding, revocation, exchange and audit-decision rules. The
new PostgreSQL coordinator must not reproduce those rules in a second policy
engine.

For each operation the persistence coordinator will:

1. derive the bounded principal key from an explicit synthetic principal or a
   hash-only stored record;
2. insert-if-absent and lock that principal's generation row;
3. hydrate only that principal's persisted parent, surface, exchange and
   generation records into the accepted in-memory store;
4. execute exactly one accepted runtime operation with an in-transaction audit
   buffer;
5. insert the typed audit batch and flush it before persisted state changes;
6. upsert the resulting hash-only state; and
7. commit audit and state together or roll both back.

Known denials may commit only their required metadata audit. A required-audit
failure overrides the operation result and rolls back the transaction.

### 3.2 Principal serialization boundary

The composite `(practice_ref, user_ref)` principal-generation row is the first
and only mutable row lock for operations on that principal. All subsequent
rows are read and written in deterministic table/key order. This short
transaction contains no network, provider, browser, Office, file, subprocess
or human interaction.

The lock establishes cross-process serialization for this tranche. Direct
database writers outside the coordinator remain forbidden and are not made
safe by this evidence.

### 3.3 Authored-synthetic schema boundary

The initial schema is deliberately incapable of accepting live application
identifiers. It stores bounded text references with exact `synthetic-`
constraints and the fixed data class `authored_synthetic`. It has no foreign
key or query to product `users`, `practices`, `practitioners`, patients,
appointments or clinical tables.

This preserves the accepted evidence boundary. Replacing synthetic references
with live EMR4 identity keys is a later migration and authority decision, not a
silent configuration switch.

### 3.4 Normalized tables and constraints

The migration adds five lower-case tables:

- `application_auth_principal_generations`;
- `application_auth_parent_sessions`;
- `application_auth_surface_sessions`;
- `application_auth_exchange_grants`; and
- `application_auth_audit_events`.

State tables use exact composite practice-scoped foreign keys, timezone-aware
timestamps, positive generations, allowlisted roles/surfaces/statuses,
canonical HTTPS origins, exact audiences, ordered expiry checks and exact hash
formats. Every foreign-key access path is indexed. Active/expiry and
unconsumed-grant queries use small composite or partial indexes.

Audit uses a sequential `bigint` identity primary key and fixed typed columns,
not an arbitrary payload. Reason codes are a bounded array. Audit rows contain
no bearer, raw token, verifier, state, nonce, Office identity, document,
patient, clinical, appointment or free-text column.

### 3.5 Database defense in depth

All five tables enable and force practice-reference row-level security. State
tables receive exact-practice `SELECT`, `INSERT`, `UPDATE` and `DELETE`
policies; the audit table receives only exact-practice `SELECT` and `INSERT`
policies. Missing context sees no scoped rows.

An append-only trigger rejects audit update/delete. A generation trigger
rejects rollback or multi-generation jumps. An exchange trigger makes
consumption monotonic and forbids clearing or rewriting a consumed timestamp.
The service still owns semantic checks; triggers are a final persistence
guard, not another authorization engine.

No durable database role or privilege grant is created in this tranche. The
RLS acceptance role is unique, non-login, non-superuser and non-bypass-RLS,
exists only inside a transaction, and disappears on rollback.

### 3.6 Retention and transport

No session purge, audit retention, backup policy, login route, exchange route,
cookie or BFF transport is added. Expired/revoked rows remain inert. Retention,
runtime database roles and secure transport require later explicit decisions.

## 4. Acceptance gates

### Gate A — five-source receipt and protected Git state

- The receipt names all five mandatory rehydration sources and passes with
  worker dispatch disabled.
- The required branch, HEAD, upstream, worktrees and protected refs remain
  unchanged.
- All accepted uncommitted architecture/runtime work and unrelated user
  changes are preserved.

### Gate B — model and reversible migration contract

- ORM metadata and Alembic define the same five tables, columns, constraints,
  foreign keys and indexes.
- The migration revises the single current head `n3o4p5q6r7s8`.
- A fresh disposable database passes full `upgrade head`, downgrade to
  `n3o4p5q6r7s8`, re-upgrade to head and exact current-head inspection.
- No existing development, test, cloud or production database is migrated.

### Gate C — durable exact behavior

- A session created through the PostgreSQL coordinator validates after all
  original SQLAlchemy sessions are closed.
- All three surface bindings retain exact origin/audience and time bounds.
- Explicit and generation revocation remain fail closed after restart.
- Raw parent/surface/exchange/state/nonce/verifier values are absent from all
  persisted text/array fields and audit rows.

### Gate D — single-use and transaction atomicity

- Two independent SQLAlchemy sessions redeem one grant concurrently; exactly
  one creates a native-Diary binding and the other receives
  `exchange_already_consumed`.
- The grant has one terminal `consumed_at` and cannot be reset or rewritten.
- A forced audit insert outage leaves generation, parent, surface, grant and
  audit counts and state unchanged.
- Audit update/delete and generation rollback fail at PostgreSQL.

### Gate E — practice isolation and cleanup

- A non-login, non-superuser, non-bypass-RLS probe sees zero rows without
  context, exactly its own fixture rows with context and zero foreign-practice
  rows.
- Foreign-practice insert/update attempts fail or affect zero rows.
- The ephemeral role and every fixture disappear on rollback.
- The uniquely named disposable acceptance database is verified, terminated,
  dropped and proved absent after all checks.

### Gate F — non-wiring and regression verification

- Static checks prove the coordinator is not imported by FastAPI/GraphQL
  routers and contains no cookie, Office, Microsoft Graph, provider, HTTP,
  socket or subprocess client.
- Focused persistence tests run serially.
- Runtime-foundation, shared-auth architecture, legacy auth, API Spine,
  Continuity and Compass regressions pass in their appropriate database or
  no-`conftest` modes.
- Python compilation, Ruff, JSON validation and `git diff --check` pass.

## 5. Evidence label

Direct, non-browser operation against a uniquely created local PostgreSQL
database is labelled `live_local_backend_postgres`. It is not browser evidence,
production evidence or proof of a deployed runtime.

## 6. Closed boundaries

Provider calls, external identity, Microsoft/Office authority, product-derived
or patient/health/clinical/historical data, live login, routes, cookies,
application product reads, appointment/arrival commands, microphone capture,
document mutation, organisational Office deployment, cloud/IAM changes,
production and release remain closed.

## 7. Candid claim limit

A pass can prove reversible local schema creation, normalized hash-only
authored-synthetic persistence, principal-row serialization, database-level
single-use exchange, same-transaction metadata audit, practice RLS controls and
complete disposable cleanup. It cannot prove live identity establishment,
product-role freshness, secure cookies, a runtime database role, retained audit
operations, backup/restore, multi-region behavior, external federation,
product-data safety, deployment, production fitness or release readiness.
