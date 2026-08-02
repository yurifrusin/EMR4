# Sol acceptance: PostgreSQL OIDC operational connection boundary

Date: 2026-08-02

Decision: `accepted`

Result: `postgresql_oidc_operational_connection_boundary_pass`

## Acceptance judgment

The implemented descendant satisfies the authorised plan. The authenticating
LOGIN has no inherited or direct table authority, the reused pool connection is
verified on both checkout and return, and bounded key references become the
accepted cipher/digest objects without storing raw material in configuration.
No application surface imports the runtime bundle.

The decisive negative proof is live rather than syntactic: acceptance committed
a weakened session role/timeout, returned it to the one-connection pool, and
proved both clean LOGIN check-in and exact capability/timeout restoration on the
same physical backend before the next borrower. Direct LOGIN access denied,
pool exhaustion remained finite, old keys survived one fresh-runtime rotation,
and all disposable state was removed.

## Evidence reviewed

- frozen plan, design and threat-model delta;
- LOGIN/capability statement contract, bounded pool/reset implementation and
  credential-free key-provider/runtime builder;
- successful disposable live-local PostgreSQL evidence with zero sensitive
  residue and complete database/two-role cleanup;
- 14 new focused, 149 OIDC/API/federation, 144 expanded shared-auth/identity
  and 64 continuity/handover tests;
- Ruff, Bandit, `pip check`, `pip-audit`, Alembic-head and diff checks; and
- exact reproduction of the unchanged parent full-suite collection barrier.

## Limits

This acceptance establishes only the provider-free dormant operational
connection and key-configuration boundary. It grants no persistent deployment
credential, secret-manager implementation, hosted connection, mounted route,
live Microsoft/provider call, real identity, binding, admission grant,
application session, product read, deployment, production, release, protected
integration, Pages or Dependabot disposition authority.

Reasoning level: High. The security choices were frozen before implementation;
acceptance followed the exact live-local gates and did not override a failure or
broaden the user's authority.
