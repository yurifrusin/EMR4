# Raisa PostgreSQL OIDC operational connection boundary closeout

Date: 2026-08-02

Result: `postgresql_oidc_operational_connection_boundary_pass`

## Outcome

The separately authorised provider-free operational descendant passes. The
accepted PostgreSQL attempt store can now be assembled behind a finite
deployment-LOGIN boundary and a credential-free key-provider seam while
remaining dormant, route-free and detached from identity, session and product
authority.

## Implemented boundary

- one exact `emr4_oidc_attempt_login_*` statement contract using `LOGIN`,
  `PASSWORD NULL`, `NOINHERIT`, `NOBYPASSRLS` and a finite connection limit;
- membership only in the accepted NOLOGIN capability role, with no direct
  schema/table/product grant and no repository-supplied deployment password;
- a bounded QueuePool policy with finite size, overflow, checkout timeout and
  recycle settings, explicit pre-ping/LIFO and pool maximum no greater than the
  LOGIN connection limit;
- verified checkout that starts from the LOGIN, enters the exact capability,
  restores RLS and statement/lock/idle-transaction timeouts and commits only
  setup;
- a custom return-time reset that rolls back application work, resets role and
  all session settings, verifies LOGIN identity and commits only cleanup;
- typed versioned key-reference configuration and one structural secret
  provider with no key bytes in configuration;
- exact once-per-reference startup resolution, duplicate/cross-use rejection
  and construction of the accepted Fernet and digest keyrings; and
- one dormant runtime bundle containing the engine, session factory and
  accepted PostgreSQL store, with no router/main import.

## Evidence

One uniquely named disposable loopback PostgreSQL database, one generated
unrecorded LOGIN password and one exact NOLOGIN capability role were exercised.
The LOGIN attributes and membership-only posture matched exactly; direct LOGIN
table access returned SQLSTATE `42501`.

On a one-connection pool, acceptance observed the exact separate
`session_user`/`current_user` pair and all timeout/RLS settings, then deliberately
committed `RESET ROLE` plus an unlimited statement timeout. Return-time cleanup
restored the LOGIN. The next checkout reused the same physical backend and
restored the exact capability and settings. A second checkout timed out inside
the configured bound.

An initial key configuration stored one encrypted attempt. A fresh runtime with
rotated active cipher/digest keys and retained old references consumed it, then
persisted one active rotated attempt. Database scanning found zero matches for
22 raw flow, key, password, target and secret-reference values. Sanitized
evidence contained zero such matches.

Cleanup proved the disposable database, LOGIN and capability role all absent.

## Verification

- disposable PostgreSQL operational acceptance: pass;
- new focused tests: 14 passed;
- OIDC/API-spine/federation focused suite: 149 passed;
- expanded shared-auth/identity suite: 144 passed;
- continuity/handover reconciliation suite: 64 passed;
- targeted Ruff: pass;
- targeted application Bandit: no findings;
- `pip check`: no broken requirements;
- `pip-audit -r requirements.txt --desc --progress-spinner off`: no known
  vulnerabilities;
- single Alembic head remains `r7s8t9u0v1w2`; and
- `git diff --check`: pass.

Full repository pytest still stops during collection at the unchanged
parent-HEAD import of removed uppercase `_BERNIE_SESSION_STORE` in
`tests/test_api_spine_confirmation_family_idempotency_integration.py`. This
tranche did not alter that test or the appointments router.

## Side effects

External/provider calls, hosted database connections, real identities,
bindings, application sessions, product/patient/clinical reads, mounted routes,
cloud/IAM changes, deployments, production changes, releases, protected-ref
movements, Pages rebuilds and Dependabot dispositions are all zero. The
user-owned `docs/branding/` directory was not modified, staged, tested, read
into evidence, committed or removed.

## Residual gates

The next safe candidate is a default-off provider-free mounted OIDC
start/callback transport boundary: exact origin and pre-authentication CSRF,
bounded `form_post`, generic errors and a restrictive no-store exact-origin
bridge page, still using authored-synthetic protocol/verifier inputs and
releasing no application session or product authority. It requires fresh
authority.

Live Microsoft, real identity, binding resolution, admission-grant/session
redeem, product reads, production key/password custody and rotation, managed
pooler/TLS policy, distributed abuse resistance, monitoring/SIEM, cloud/IAM,
deployment, protected integration, production and release remain separately
closed.
