# Raisa Microsoft-federation PostgreSQL persistence plan

Date: 2026-08-01

Owner: Yuri / GPT Sol

Status: `authorised_disposable_postgresql_authored_synthetic_implementation`

Parent result: `raisa_microsoft_federation_admission_runtime_pass`

## 1. Authority

This is the second logical descendant explicitly authorised with the real-identity/Microsoft-federation architecture. It may add a reversible Alembic migration, detached ORM models, a route-free repository and uniquely named disposable local PostgreSQL acceptance using authored-synthetic identity references and an injected synthetic HMAC key.

It may not migrate an existing development/test/cloud database, create a real identity binding, store a real Microsoft identifier, add a route, grant a durable runtime role, create an application session, read product data, mutate cloud/IAM, deploy, enter production or release.

## 2. Objective

Prove a durable boundary for:

- unique external-key-to-one-principal binding;
- keyed-reference lookup without raw external identity persistence;
- active-to-revoked terminal lifecycle with optimistic versioning;
- required append-only metadata audit in the same transaction as binding mutation or resolution;
- forced practice-scoped row-level security for identified rows; and
- reversible migration and complete disposable database cleanup.

## 3. Frozen schema

### 3.1 Binding table

`application_identity_federation_bindings` stores:

- synthetic binding, user and practice references;
- fixed provider `microsoft_entra`;
- versioned HMAC-SHA-256 references for issuer, tenant, object and subject;
- active/revoked status, positive version and bounded timestamps; and
- fixed `authored_synthetic` data class.

The composite provider/issuer/tenant/object reference is unique. Raw issuer, tenant, object, subject, email, name, token, code or role columns do not exist. There is deliberately no foreign key or query to `users`, `practices`, practitioners, patients, appointments or clinical tables.

### 3.2 Audit table

`application_identity_federation_audit_events` stores one synthetic idempotency-style operation reference, HMAC-only correlation/external references, optional synthetic binding/principal references, fixed provider/policy/data class, typed event/decision/reason and time. It has no arbitrary JSON or free-text payload.

A trigger rejects update/delete with SQLSTATE `55000`. A binding trigger permits only one immutable active-to-revoked transition with version `+1`; revoked rows are terminal.

### 3.3 Row-level security

Both tables enable and force RLS. Identified binding and audit rows use exact `emr4.practice_ref` policies. An unidentified rejected lookup audit has no practice and is intentionally insertable only by the table owner in this bounded proof; a later live runtime-role/bootstrap design must replace owner access with a narrowly reviewed security-definer or separate audit-ingress capability.

No durable role, privilege grant or resolver function is created here. The disposable RLS probe creates a non-login, non-superuser, non-bypass role inside a transaction, grants only read capability, and proves the role disappears on rollback.

## 4. Route-free repository

The repository:

- accepts only typed authored-synthetic binding values and exact `.invalid` tenant-specific issuer;
- computes all external/correlation references with an injected minimum-256-bit key;
- creates binding plus required audit in one transaction;
- resolves at most one active binding and records allowed/denied lookup audit before return;
- locks a binding for exact-version revocation and commits revocation plus audit together; and
- maps uniqueness, audit and database failures to bounded reason codes without a connection string or raw identity.

It is not imported by a router or session runtime.

## 5. Acceptance gates

1. Alembic advances the single head `p5q6r7s8t9u0` to `q6r7s8t9u0v1`, downgrades, re-upgrades and reports exact head with no ORM drift.
2. ORM and migrated columns match for exactly the two new tables.
3. Two concurrent attempts to create the same external key admit exactly one row.
4. A fresh repository/session resolves the created binding; revocation persists and later resolution denies.
5. A forced required-audit failure rolls back the associated binding mutation.
6. Audit update/delete and invalid binding mutation fail with SQLSTATE `55000`.
7. The disposable RLS role sees zero rows without context, only its practice with exact context and no foreign-practice rows.
8. Scanning every persisted row finds no raw issuer, tenant, object, subject, email, HMAC key or correlation value.
9. The exact uniquely named database is terminated, dropped and proved absent.

## 6. Closed boundaries and claim limit

No live Microsoft/OIDC verifier, real identity, app registration, route, cookie, session bridge, product/internal user reload, product read, durable runtime role, production key custody, retention/SIEM, deployment, production or release is proven.

A pass proves only reversible local authored-synthetic schema, keyed-reference persistence, database uniqueness, terminal revocation, transaction-bound metadata audit, RLS defense in depth and cleanup.
