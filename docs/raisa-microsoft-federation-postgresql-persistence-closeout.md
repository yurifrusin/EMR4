# Raisa Microsoft-federation PostgreSQL persistence closeout

Date: 2026-08-01

Result: `raisa_microsoft_federation_postgresql_persistence_pass`

## Outcome

The second authorised architecture descendant passes. EMR4 now has one route-free authored-synthetic PostgreSQL repository for external-identity binding creation, exact active lookup, terminal revocation and required metadata audit.

Alembic revision `q6r7s8t9u0v1`, descending from the previous single head `p5q6r7s8t9u0`, adds exactly two detached tables. The binding table stores synthetic internal references and versioned keyed-HMAC references for issuer, tenant, object and subject. The audit table stores only typed decisions/events, HMAC-only correlation/external references and optional synthetic internal references. Neither table has a raw external identifier/token/email/name column or a foreign key/query to product identity, practitioner, patient, appointment or clinical truth.

## Acceptance evidence

One uniquely named loopback PostgreSQL database passed upgrade to `q6r7s8t9u0v1`, downgrade to `p5q6r7s8t9u0`, re-upgrade, exact-head inspection and `alembic check`. ORM and migrated columns match for both tables. Both tables enable and force RLS; three exact-practice policies and the two expected guard triggers were observed.

The `live_local_backend_postgres` exercise proved:

- an active binding resolves through a freshly constructed repository/database session;
- two independent sessions racing to create the same external key produce exactly one binding and one `binding_conflict`;
- a forced required-audit failure rolls back both binding and audit state;
- exact-version revocation advances version from 1 to 2, persists and makes later lookup deny;
- audit update/delete and binding reactivation each fail with SQLSTATE `55000`;
- a transactional `NOLOGIN`, `NOSUPERUSER`, `NOBYPASSRLS` role sees zero rows without context, sees only its practice with exact context, sees no foreign-practice binding and disappears on rollback; and
- scanning every persisted binding/audit row finds none of the tested raw issuer, tenant, object, subject, email, HMAC key or correlation values.

The exact disposable database was terminated, dropped and proved absent. The evidence records neither its generated name nor a database URL.

## Security disposition

Database uniqueness closes the in-memory ambiguity race for this bounded schema. Immutable external/principal fields plus a terminal transition trigger prevent silent reassignment or reactivation. Required audit shares the mutation/read transaction and an append-only trigger protects recorded events. Forced RLS provides practice defense in depth for identified rows.

This is not a production bootstrap. Rejected lookups with no known practice can be audited only by the table owner in this proof. No durable runtime role or privilege grant exists. A later live design must define a narrowly scoped provider-to-practice resolver/audit-ingress capability without accepting table-owner or superuser access.

## Claim limit and next gate

This result proves reversible local authored-synthetic schema, keyed-reference persistence, database uniqueness, terminal revocation, transaction-bound metadata audit, RLS defense in depth and cleanup. It does not prove Microsoft/OIDC behavior, real identity or key custody, a login/callback or binding-lifecycle route, current internal identity reload, application-session creation, product authorization, retention/SIEM, deployment, production fitness or release readiness.

The three-tranche authority is now consumed. The next safe candidate would be an architecture-only maintained-library verifier and least-privilege federation bootstrap/session-bridge design, still with no live Microsoft wiring or product reads. It requires a new explicit authority decision.

Protected integration remains paused because these documentation changes would trigger public GitHub Pages deployment.
