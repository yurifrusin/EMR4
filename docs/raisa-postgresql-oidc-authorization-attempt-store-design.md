# Raisa PostgreSQL OIDC authorization-attempt store design

Date: 2026-08-02

Result class: route-free provider-free PostgreSQL runtime foundation

## API Spine placement

This is persistence behind the existing dormant REST protocol adapter. It adds
no endpoint, GraphQL mutation, event actuator or browser contract. The adapter
still releases only independently verified Microsoft `tid`/`oid`/`sub` with
authorization, session and product flags false.

## Port and key ownership

`AuthorizationAttemptStore` is a structural port with `store`, `consume` and
`discard`. The existing bounded in-memory store and the new PostgreSQL store
both implement it. The adapter owns sequencing; persistence never invokes MSAL,
Authlib, a provider, binding resolver or session service.

`FernetAuthorizationAttemptCipher` is an authenticated-encryption keyring. One
validated key identifier is active for writes and up to four retained keys may
decrypt existing rows. `AuthorizationAttemptDigestKeyring` separately derives
domain-separated state and nonce HMAC references. Its active plus retained
keys produce a bounded lookup set during rotation. Unknown, removed or invalid
keys fail closed; no raw key is persisted or included in evidence.

## Table

`application_identity_oidc_authorization_attempts` has the state HMAC reference
as its primary key and the nonce HMAC reference as a unique constraint. It also
stores the cipher key identifier, encrypted envelope, `created_at`,
`expires_at`, envelope version and the fixed `authored_synthetic` marker.

Database checks enforce reference/key syntax, a bounded nonempty ciphertext,
the exact v1 envelope marker and an expiry exactly five minutes after creation.
An expiry index supports bounded purge. There is no identity, tenant, email,
name, token, authorization code, binding, practice, role, session, patient or
product column.

## Transaction semantics

Store validates and encrypts before opening a transaction. Within one short
transaction it verifies the effective capability role, obtains one
transaction-scoped advisory lock, deletes expired rows, checks every retained
state digest for collision, enforces the configured capacity and inserts one
row. There is no external/provider network or other non-database blocking work
while the lock is held.

Consume derives the bounded candidate state references and issues one
`DELETE ... RETURNING`. The transaction commits before expiry evaluation,
decryption, envelope validation or release. Thus database concurrency selects
one winner and every expired, corrupt or otherwise unreadable matched attempt
is still terminally consumed. Provider exchange remains later in the adapter,
after this commit.

Discard is an idempotent delete over the bounded candidate reference set.
Opportunistic expiry purge plus the maximum-128 capacity bounds storage without
claiming a scheduler or distributed abuse-control system.

## Role and RLS

The cluster-scoped capability role is provisioned outside Alembic from an exact
allowlisted statement generator and is never created by application code. It
is `NOLOGIN`, `NOINHERIT`, `NOBYPASSRLS`, has short statement/lock/idle
timeouts, and receives only schema `USAGE` plus table `SELECT`, `INSERT` and
`DELETE`. It has no `UPDATE`, sequence, function, product-table or schema-create
authority.

The migration revokes `PUBLIC`, enables and forces RLS, and defines exact
select/insert/delete policies whose `current_user` must match the capability
role-name family. A separately authorised finite LOGIN and pool-time `SET ROLE`
contract is still required before a mounted runtime can use this store.

## Closed boundaries

The schema is authored-synthetic only. There is no durable LOGIN credential,
route, callback HTML, CSRF/origin edge, admission grant, binding lookup, cookie,
application session, product read, live Microsoft call, cloud/IAM change,
deployment, protected integration, production or release.
