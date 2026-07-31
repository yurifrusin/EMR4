# Threat-model delta — Raisa shared application-auth PostgreSQL persistence

Date: 2026-08-01

Status: `repository_local_postgresql_authored_synthetic_persistence`

## Overview

This delta narrows the accepted shared-auth runtime threat model to its first
durable adapter and reversible migration. It covers normalized PostgreSQL
state, one SQLAlchemy transaction per operation, required metadata audit, a
principal-generation row lock and disposable authored-synthetic acceptance
databases only.

The parent architecture and runtime threat models remain authoritative. No
route, cookie, external identity, Microsoft/Office authority, product-derived
read, patient or clinical data, provider call, command, deployment, production
or release is opened.

## Threat Model, Trust Boundaries, and Assumptions

### Assets and privileges

- hash-only parent, surface and exchange references;
- principal generation and terminal revocation state;
- exact origin, audience, surface, state-hash, nonce-hash and PKCE bindings;
- single-use exchange consumption and target-surface creation;
- practice isolation;
- metadata-audit completeness and immutability; and
- migration integrity and disposable-database cleanup.

### Trust boundaries

1. An untrusted future caller to the still-unmounted coordinator.
2. Raw opaque method inputs to SHA-256 references before persistence.
3. The coordinator to its principal-generation row lock.
4. Hydrated PostgreSQL records to the accepted runtime policy engine.
5. Buffered required audit and state mutation to one database transaction.
6. A practice-scoped database role to forced RLS policies.
7. Alembic upgrade/downgrade code to an exact disposable local database.

Method inputs, opaque tokens, exchange values and database rows are untrusted.
The frozen surface-origin map, runtime policy code, migration source,
SQLAlchemy session factory and PostgreSQL transactional/locking semantics are
trusted within this tranche.

Assumptions are PostgreSQL `READ COMMITTED` row locks, transactional DDL,
timezone-aware UTC values, no direct state writer outside the coordinator, no
reuse of the synthetic-only schema for live identities, and a database account
that cannot silently defeat the intended production RLS design. The last item
is not established here because durable runtime roles remain closed.

## Attack Surface, Mitigations, and Attacker Stories

### Concurrent redemption creates two Diary bindings

Two application processes read the same unconsumed grant and each creates a
target surface.

Controls:

- all operations for the principal lock the same generation row;
- the second transaction hydrates state only after acquiring that lock;
- the accepted runtime treats `consumed_at` as terminal;
- grant consumption, target binding and both audit rows commit together; and
- a database trigger forbids clearing or rewriting consumption.

Acceptance requires independent database sessions to admit exactly one caller.

### Audit and authority diverge during failure

The database accepts session/grant state but rejects or loses its required
audit, or it retains audit for state that rolled back.

Controls:

- audit rows and resulting state share one SQLAlchemy transaction;
- the audit batch is flushed before state persistence;
- any audit failure raises `required_audit_unavailable` and rolls back; and
- append-only triggers reject later audit update/delete.

Residual risk: backup/restore, replication and external audit delivery are not
tested. No outbox is needed until an external audit consumer is authorised.

### Cross-practice token or row access

A caller or compromised query reads or changes another practice's auth state.

Controls:

- every state relationship includes the same `practice_ref` in a composite
  foreign key;
- all foreign-key paths are indexed;
- all tables enable and force exact-practice RLS;
- missing context exposes no scoped rows; and
- an ephemeral non-bypass-RLS role proves own/foreign visibility behavior.

Residual risk: the route-free coordinator must initially locate a token hash
before it knows the practice. A future runtime-role design must explicitly
solve that bootstrap lookup without a broad table-owner or superuser account.

### Synthetic storage is mistaken for live authentication

A developer wires the adapter to a route or puts real EMR4 identifiers into
the tables.

Controls:

- all identity references have database `synthetic-` checks;
- every row has the fixed `authored_synthetic` data class;
- the coordinator accepts only `SyntheticPrincipal`;
- no router, cookie or dependency binding is added; and
- static tests reject route/cookie/provider/Office wiring.

Live identity mapping necessarily requires a reviewed schema migration rather
than a configuration-only change.

### Database or log disclosure yields reusable credentials

An attacker reads the five tables, SQL logs, audit events or evidence JSON.

Controls:

- only `sha256:` references are stored for parent, surface, grant, state and
  nonce values;
- the PKCE verifier is never stored and its challenge is not a bearer;
- audit uses fixed columns and bounded reason-code arrays, not free metadata;
- evidence excludes database URLs and raw values; and
- tests scan persisted text/array values for every issued raw value.

Residual risk: low-entropy secrets would be vulnerable to offline guessing;
the production token source remains the accepted cryptographically random
default, while deterministic tokens are acceptance-only.

### Generation rollback resurrects revoked sessions

A stale writer lowers the generation or skips directly to an unrelated value.

Controls:

- the principal row is locked first;
- generation advances by exactly one in the accepted runtime; and
- a trigger permits only unchanged or one-step-forward updates.

Parent, surface and exchange generation mismatches still fail closed after
restart.

### Lock inversion or long transaction causes denial of service

Two operations lock rows in different order, or hold a lock while performing
external work.

Controls:

- the principal-generation row is always the first mutable lock;
- records are persisted in a deterministic table/key order;
- transactions contain only local validation, audit inserts and state upserts;
- no network, provider, browser, Office, subprocess or human action occurs
  while locked; and
- acceptance uses bounded concurrent operations.

Residual risk: production statement/lock timeouts, connection pooling and load
capacity are later operational decisions.

### Migration or cleanup targets the wrong database

An acceptance run upgrades or drops a development/product database.

Controls:

- the runner creates a unique allowlisted database name itself;
- destructive cleanup accepts only that exact created name and local host/port;
- the existing development and shared test databases are never migration
  targets;
- all connections are terminated only for the exact task-created database; and
- absence is verified after drop.

## Severity Calibration (Critical, High, Medium, Low)

### Critical

- raw stored bearer material permits reusable application-session takeover;
- concurrent redemption commits two valid native-Diary bindings; or
- a practice can read/change another practice's live-equivalent auth state.

### High

- audit failure still commits a session, revocation or exchange mutation;
- generation rollback reactivates revoked state;
- state/nonce/PKCE/origin/audience substitution redeems a grant; or
- the synthetic adapter is silently connected to product-derived clinical
  reads or commands.

### Medium

- lock ordering enables a bounded denial of service without authority gain;
- an expired row remains queryable to a privileged database operator while
  validation still denies it;
- detailed internal denial audit becomes an enumeration aid after future route
  wiring; or
- missing operational retention causes unnecessary metadata accumulation.

### Low

- a malformed synthetic reference is rejected by a database check;
- a duplicate deterministic test token rolls back on a primary-key collision;
  or
- disposable evidence omits a non-security timing measurement while all
  authority and cleanup claims remain intact.

Repository: EMR4
Version: 8fa732592fbee4f57c322b13d9d8ff89fcc7fa33
