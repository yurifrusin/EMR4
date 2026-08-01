# GPT Sol acceptance — Raisa shared application-auth PostgreSQL persistence

Date: 2026-08-01

Verdict: **accepted**

Result: `raisa_shared_application_auth_postgresql_persistence_pass`

The authorised repository-local PostgreSQL tranche satisfies its bounded plan
and inherited threat boundary.

Acceptance grounds the following claims:

1. one reversible Alembic migration and matching ORM add exactly five
   normalized authored-synthetic auth tables at head `o4p5q6r7s8t9`;
2. opaque parent, surface, exchange, state and nonce material persists only as
   SHA-256 references, while the PKCE verifier is never stored;
3. one principal-generation row lock serializes each principal's operations
   before the accepted in-memory runtime policy engine executes;
4. state and required typed metadata audit share one transaction, and a forced
   audit outage rolls back every change;
5. two independent database sessions redeem one exchange with exactly one
   consumer and one terminal replay denial;
6. forced practice RLS, append-only audit, monotonic generation and terminal
   exchange-consumption guards pass; and
7. the uniquely named local database and transactional probe role are absent
   after acceptance.

The standalone `live_local_backend_postgres` evidence passes. All 60 focused
cases, the corrected 156-case expanded no-`conftest` suite and 12 serial legacy
database-fixture auth cases pass. Alembic upgrade/downgrade/re-upgrade, exact
head, autogenerate drift, compilation, Ruff, JSON and whitespace gates pass.
Every recorded external and product side-effect count is zero.

No live login, route, cookie, runtime database role, external identity,
Microsoft/Office federation, product-derived read, clinical authority,
appointment command, microphone capture, document mutation, cloud/IAM change,
deployment, production or release authority is created by this acceptance.

A least-privilege runtime database-role and secure synthetic session-transport
architecture is the next safe candidate. It remains a fresh material decision,
and product reads remain closed.
