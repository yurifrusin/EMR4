# Raisa PostgreSQL OIDC authorization-attempt store closeout

Date: 2026-08-02

Result: `postgresql_oidc_authorization_attempt_store_pass`

## Outcome

The separately authorised provider-free PostgreSQL descendant passes. The
accepted two-component adapter now targets a structural attempt-store port, and
one dormant PostgreSQL implementation durably retains the exact encrypted MSAL
flow while preserving consume-before-exchange and releasing no new identity,
session or product authority.

## Implemented boundary

- one authored-synthetic-only table whose primary key is a versioned
  HMAC-SHA256 state reference;
- a unique versioned nonce HMAC, cipher-key identifier, authenticated-encryption
  ciphertext, exact five-minute timestamps, envelope version and no plaintext
  flow/identity/token/product columns;
- separate bounded active-plus-retained Fernet and digest keyrings, including
  rotation of already-open attempts and fail-closed removal of an old key;
- short transaction-scoped advisory locking for global maximum-128 capacity,
  expiry purge and cross-key state/nonce collision checks;
- one `DELETE ... RETURNING` consume transaction committed before expiry,
  decrypt or adapter exchange, making matched expired/corrupt attempts terminal;
- an exact credential-free NOLOGIN capability role with only schema `USAGE` and
  table `SELECT`, `INSERT`, `DELETE`;
- forced RLS select/insert/delete policies for the allowlisted effective-role
  family, with `PUBLIC` revoked and no `UPDATE`; and
- no route, main/router import, provider transport, binding/session/product
  dependency or deployment configuration.

## Evidence

The uniquely named disposable loopback PostgreSQL database passed upgrade,
downgrade, re-upgrade, exact-head and ORM-drift checks. A separate effective
NOLOGIN role passed the exact privilege contract. A granted outsider saw zero
rows and received SQLSTATE `42501` on insert; the capability role received the
same denial for update.

Two concurrent adapter callbacks over independent database sessions produced
exactly one row deletion, one synthetic exchange, one verification and one
bounded principal release. Replay denied. Fresh store construction consumed a
durable attempt; exact expiry, capacity, discard, collision, retained-key
rotation, missing-key, ciphertext-tamper and audit-cleanup cases all matched the
frozen result. An active encrypted row was scanned and contained zero matches
across 76 raw flow/key values.

Cleanup proved both the exact disposable database and cluster role absent.
Evidence records neither name nor database URL.

## Verification

- disposable PostgreSQL acceptance: pass;
- new focused tests: 11 passed;
- OIDC/API-spine/federation focused suite: 113 passed;
- full shared-auth and real-identity inherited suite: 222 passed;
- targeted Ruff: pass;
- targeted application Bandit: no findings;
- `pip check`: no broken requirements;
- `pip-audit -r requirements.txt --desc --progress-spinner off`: no known
  vulnerabilities.

Full repository pytest still stops during collection at the parent-HEAD import
of removed uppercase `_BERNIE_SESSION_STORE` in
`tests/test_api_spine_confirmation_family_idempotency_integration.py`. This
tranche did not alter that test or router symbol. One historical federation
migration test was reconciled from an obsolete terminal-head assertion to the
durable invariant that its accepted revision remains in the repository's
single Alembic lineage.

## Side effects

External provider/network calls, real identities, bindings, application sessions,
product/patient/clinical reads, mounted routes, cloud/IAM changes, deployments,
production changes, releases, protected-ref movements and Pages rebuilds are
all zero. The user-owned `docs/branding/` directory was not modified, read into
evidence, staged, tested, committed or removed.

## Residual gates

The next safe candidate is a provider-free operational connection boundary for
this store: one finite deployment LOGIN, exact pool-time `SET ROLE`, and a
credential-free runtime key-provider/configuration seam. It requires fresh
authority.

Mounted start/callback routes, CSRF/origin handling, callback HTML/admission
grant bridging, live Microsoft, real identity, binding resolution, application
sessions, product reads, distributed abuse resistance, monitoring/SIEM,
cloud/IAM, deployment, protected integration, production and release remain
separately closed.
