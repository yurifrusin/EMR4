# Sol acceptance: provider-free OIDC binding and admission-grant boundary

Date: 2026-08-02

Decision: `accepted`

Result: `provider_free_oidc_binding_admission_grant_boundary_pass`

## Acceptance judgment

The implementation satisfies the frozen second descendant. It accepts only the
typed output of the maintained-verifier port, converts every external identity
component to a keyed HMAC before SQL, resolves issuer/tenant/object/subject
exactly under forced RLS, and returns only internal authored-synthetic
references after required audit.

The PostgreSQL authority split is decisive: the deployment login is finite and
`NOINHERIT`; the resolver caller can execute only one security-definer function;
the grant issuer cannot read bindings or write audit directly; and the
resolver/audit owner is no-login and not granted to the deployment login. A
database trigger makes issued audit inseparable from grant insertion.

The live proof used the ordinary FastAPI router, accepted durable attempt
runtime, real loopback HTTP and disposable PostgreSQL. It proved one exact
60-second grant, separately keyed bearer HMAC, exact-origin release, generic
failure, capacity rollback, rejected-binding audit, direct privilege denial,
practice isolation, zero raw database residue and complete server/database/
role cleanup.

## Evidence reviewed

- frozen plan, design and threat-model delta;
- model, migration, role split, operational pool, HMAC resolver/grant service,
  transport integration and versioned API Spine;
- successful provider-free live-local HTTP/backend/PostgreSQL evidence;
- focused and inherited security/auth/API/continuity tests; and
- targeted lint, compilation, dependency, migration, security and diff checks.

## Limits

This accepts only provider-free authored-synthetic binding resolution and a
non-session 60-second admission artifact. It grants no live Microsoft/provider
call, real identity, internal-principal freshness claim, grant redemption,
application session, cookie, product read, production credential, cloud/IAM,
deployment, protected integration, production, release, Pages or Dependabot
disposition authority. The final user-preauthorised descendant still requires
its own five-source rehydration and acceptance.

Reasoning level: High. Architecture and security meaning were frozen before
implementation; the database audit invariant was strengthened during review,
and no failure was overridden or authority broadened.
