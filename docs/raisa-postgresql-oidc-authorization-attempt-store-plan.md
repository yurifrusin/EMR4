# Raisa PostgreSQL OIDC authorization-attempt store plan

Date: 2026-08-02

Status: authorised provider-free PostgreSQL implementation tranche

Parent: `raisa-two-component-oidc-runtime-adapter`

## Outcome sought

Replace the accepted adapter's process-local limitation with one dormant,
route-free PostgreSQL implementation of its authorization-attempt-store port.
The store must preserve the five-minute encrypted MSAL-flow boundary, survive
process replacement, and make callback consumption exactly one-use across
concurrent database sessions.

## Authority

Yuri authorised this next tranche as described. It may add the attempt-store
port, an authored-synthetic-only PostgreSQL table and migration, versioned
authenticated-encryption and digest-key abstractions, an exact NOLOGIN
capability-role contract, forced RLS, deterministic tests, disposable
live-local PostgreSQL evidence, documentation, continuity artifacts and
necessary task-branch publication.

It may not mount a start or callback route, call Microsoft or any provider, use
a real tenant or identity, create or resolve a binding, role or application
session, read product data, change cloud/IAM, deploy, release, move a protected
ref, rebuild Pages, or include the concurrent `docs/branding/` work.

## Frozen implementation contract

1. `TwoComponentOIDCAdapter` depends on a structural attempt-store port, while
   its accepted in-memory implementation continues to pass unchanged.
2. PostgreSQL stores only versioned HMAC-SHA256 state/nonce references,
   ciphertext, cipher-key identifier, exact creation/expiry times and the
   authored-synthetic data-class marker.
3. The encrypted envelope contains the complete bounded MSAL flow, surface,
   exact origin and return target; raw state, nonce, PKCE verifier and
   authorization URI never appear in plaintext database residue.
4. Encryption and digest keyrings have one active key and a bounded retained
   decrypt/lookup set, so rotation can consume already-open attempts without
   permitting fallback to an unknown key.
5. Store uses one short transaction-scoped advisory lock to purge expiry,
   enforce the maximum-128 global capacity and reject state collisions.
6. Consume uses one database `DELETE ... RETURNING` transaction and commits
   removal before decrypting or returning the flow. Expiry, unreadable
   ciphertext, replay and concurrent completion therefore cannot restore or
   reuse an attempt.
7. The exact NOLOGIN capability role receives only schema usage and table
   `SELECT`, `INSERT` and `DELETE`; `PUBLIC` is revoked, `UPDATE` is absent, and
   forced RLS admits only the allowlisted capability-role family.
8. The module has no router, network, identity-binding, session, product-model
   or application-runtime import.

## Acceptance

The tranche passes only when:

- migration upgrade/downgrade/re-upgrade and ORM drift checks pass in a uniquely
  named disposable loopback PostgreSQL database;
- two concurrent callback completions cause exactly one deletion, exchange and
  principal release;
- capacity, expiry purge, replay, discard, collision, ciphertext tamper,
  cipher/digest rotation and missing-key cases fail closed as specified;
- the capability role has the exact privilege set and a granted outsider is
  still denied by forced RLS;
- raw flow, secret and key material is absent from database/evidence residue;
- the disposable database and cluster roles are removed; and
- focused, inherited API/auth, migration, lint, security and dependency checks
  pass, with any parent-HEAD full-suite barrier reported exactly.

## Handoff

A pass proves only provider-free durable attempt semantics in disposable local
PostgreSQL. A finite deployment LOGIN/pool, mounted route and CSRF/origin edge,
callback bridge, live Microsoft interoperability, real identity, binding,
application session, product access, operations, protected integration,
production and release remain later gates.
