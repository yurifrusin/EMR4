# Sol acceptance: provider-free session practitioner-directory read bridge

Date: 2026-08-02

Decision: `accepted`

Result: `provider_free_session_practitioner_directory_read_bridge_pass`

## Acceptance judgment

The implementation satisfies the frozen selected direction. It preserves the
existing GraphQL practitioner-directory ownership and adds one explicit,
unmounted application-session context factory. Surface, origin, audience,
session generation, CSRF, current synthetic mapping, fresh product role/
practice/practitioner link, active-only policy and required audit all fail
closed before the shared product query.

The database authority is split correctly. The application-auth runtime role
cannot read product tables. A separate finite login enters one `NOINHERIT`
product capability with exact-column reads only; it has no provider/contact
identifier, auth-state or write privilege. The shared query itself no longer
loads prohibited full ORM entities.

Real loopback HTTP and disposable PostgreSQL prove the exact allowed
projection, generic denial behavior, durable allowed/denied audit, forced-audit
failure, cross-practice no-leak behavior, six direct privilege denials, raw
secret absence and complete server/database/four-role cleanup.

## Evidence reviewed

- frozen plan, design and threat-model delta;
- reversible audit-contract migration and exact runtime authorization;
- synthetic mapping, product role/pool, unmounted GraphQL adapter and hardened
  shared read service;
- successful sanitized live-local HTTP/backend/PostgreSQL evidence;
- focused and inherited shared-auth, identity, Office, API Spine, dependency,
  security and collection results; and
- closeout, preacceptance receipt and continuity revision.

## Limits

This accepts only a default-off provider-free authored-synthetic active
practitioner-directory read. It establishes no real identity mapping, patient
or clinical read, other product resource, command/write, general GraphQL
mounting, Office UI integration, product-table RLS claim, production key or
session custody, cloud/IAM, deployment, protected integration, production,
release, Pages or Dependabot disposition authority.

Reasoning level: High. API Spine ownership was preserved, least-sensitive
product truth and exact columns were chosen, an unattributed forced-RLS audit
edge was reconciled without fabricated practice scope, and no failed gate was
overridden.
