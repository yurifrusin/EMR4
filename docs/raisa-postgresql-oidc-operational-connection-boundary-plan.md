# Raisa PostgreSQL OIDC operational connection boundary plan

Date: 2026-08-02

Status: authorised provider-free operational implementation tranche

Parent: `raisa-postgresql-oidc-authorization-attempt-store`

## Outcome sought

Make the accepted dormant PostgreSQL authorization-attempt store constructible
through one finite, least-privilege operational connection boundary without
mounting it into the application. The boundary must separate the authenticating
LOGIN from the NOLOGIN table capability, restore the exact capability and
timeouts on every pool checkout, remove session contamination on return, and
resolve bounded versioned key material through a credential-free provider port.

## Authority

Yuri authorised this next candidate tranche. It may add a credential-free
finite deployment-LOGIN statement contract, a bounded SQLAlchemy QueuePool
factory, exact checkout/reset hooks, a typed secret-reference/key-provider
port, a dormant runtime builder, deterministic tests, disposable loopback
PostgreSQL evidence, documentation, continuity artifacts and necessary
task-branch publication.

It may not create a persistent deployment credential, connect to a hosted
database, change cloud/IAM or secret-manager state, mount a start/callback
route, call Microsoft or any provider, use a real tenant or identity, create a
binding or application session, read product data, deploy, release, move a
protected ref, rebuild Pages, decide Dependabot alert 17, or include the
concurrent `docs/branding/` work.

## Frozen implementation contract

1. One exact `emr4_oidc_attempt_login_*` role is `LOGIN`, `PASSWORD NULL`,
   `NOINHERIT`, `NOBYPASSRLS`, has a finite connection limit and receives only
   membership in the exact existing `emr4_oidc_attempt_runtime_*` NOLOGIN role.
2. The LOGIN receives no direct schema, table, sequence, function or product
   grant. Repository code neither supplies nor rotates a deployment password.
3. A validated pool policy sets finite size, overflow, checkout timeout and
   recycle bounds. Pool maximum may not exceed the LOGIN connection limit;
   pre-ping and LIFO are explicit.
4. Every checkout starts from the LOGIN, enters the exact capability role,
   applies `row_security=on` plus exact statement/lock/idle-transaction
   timeouts, verifies session/effective identities and settings, and commits
   only that session setup before application work.
5. Every pool reset first rolls back application work, then executes exact
   `RESET ROLE` and `RESET ALL`, verifies `session_user=current_user=LOGIN`,
   and commits only the cleanup. The default pool reset is replaced so a
   poisoned returned session cannot retain role or timeout state.
6. Only PostgreSQL URLs whose username exactly matches the configured LOGIN
   are accepted. Connection-string `options`, service files and role-changing
   parameters are rejected before connection.
7. Runtime key configuration contains only bounded key identifiers and opaque
   secret references. A structural provider resolves exact bytes once during
   startup before an engine/store is released; raw key material never belongs
   to configuration, repr, errors, evidence or repository settings.
8. Encryption and digest keysets remain separate, have one active plus at most
   three retained entries, reject duplicate references/material and construct
   the accepted Fernet cipher and HMAC digest keyring without fallback.
9. The runtime builder returns an engine, session factory and accepted
   `PostgresAuthorizationAttemptStore`, but no router or `app.main` import uses
   it and it performs no provider, identity, session or product action.

## Acceptance

The tranche passes only when disposable authored-synthetic loopback PostgreSQL
proves:

- the exact LOGIN attributes, membership-only privilege posture and absence of
  direct table/product grants;
- LOGIN-only denial, capability-role access, exact session/effective identity
  separation and exact timeout/RLS settings;
- reuse of one physical pooled connection after deliberate role/setting
  contamination, with the next checkout restored to the frozen contract;
- bounded pool exhaustion within the configured checkout deadline;
- provider resolution before runtime release, key separation, rotation and
  fresh-runtime durable store/consume behavior;
- no database URL, password, raw key, secret reference, state, nonce or PKCE
  value in recorded evidence;
- complete database, LOGIN and capability-role removal; and
- focused/inherited API, auth, migration, lint, security, dependency and
  continuity checks pass, with any parent full-suite barrier reported exactly.

## Handoff

A pass proves only the provider-free dormant connection and key-configuration
boundary in disposable local PostgreSQL. Mounted start/callback routes,
CSRF/origin and bridge-page handling, live Microsoft interoperability, real
identity, binding, application sessions, product access, distributed abuse
resistance, production secret custody/rotation, monitoring, cloud/IAM,
deployment, protected integration, production and release remain later gates.
