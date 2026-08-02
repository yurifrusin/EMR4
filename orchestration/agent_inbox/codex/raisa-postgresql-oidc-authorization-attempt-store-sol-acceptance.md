# Sol acceptance: PostgreSQL OIDC authorization-attempt store

Date: 2026-08-02

Decision: `accepted`

Result: `postgresql_oidc_authorization_attempt_store_pass`

## Acceptance judgment

The implemented descendant satisfies the authorised plan. PostgreSQL durability
does not weaken the accepted adapter seam: state and nonce remain keyed
references, the complete MSAL flow remains authenticated ciphertext, consume is
an exact database deletion committed before any exchange, and the released
principal still has no EMR4 authorization, binding, role, session or product
authority.

The role and RLS design is proportionate to this dormant tranche. The
capability role is NOLOGIN/NOBYPASSRLS, has only select/insert/delete on the one
attempt table, and cannot update. Forced RLS rejects a separately granted role
outside the exact allowlist. A finite LOGIN and runtime pool are explicitly not
claimed.

## Evidence reviewed

- plan, design and threat-model delta;
- adapter port, model, migration, role contract and PostgreSQL store source;
- successful disposable live-local PostgreSQL evidence with complete database
  and cluster-role cleanup;
- concurrency, rotation, expiry/capacity, tamper, RLS and plaintext-residue
  cases;
- 11 new focused tests, 113 OIDC/API/federation tests and 222 inherited
  shared-auth/identity tests;
- Ruff, targeted Bandit, `pip check` and `pip-audit`; and
- exact disposition of the unchanged parent full-suite collection barrier.

## Limits

This acceptance establishes provider-free authored-synthetic durable attempt
semantics only. It grants no route, live provider, real identity, binding,
session, product read, operational credential/pool, deployment, production,
release, protected integration or Pages authority.

Reasoning level: High. The plan froze the security and migration choices before
implementation; acceptance did not override a failed gate or broaden the user
authority.
