# Sol acceptance — PostgreSQL-backed Office-host compatibility

Date: 2026-08-01

Decision: `accepted`

Terminal result:
`raisa_shared_application_auth_postgresql_office_host_compatibility_pass`

## Acceptance basis

The frozen boundary is satisfied. Installed Word and Word Online independently
completed the exact existing CSRF, create, validate, rotate, revalidate, logout
and post-logout denial sequence through the reserved HTTPS development origin.
Both paths used the accepted disposable local PostgreSQL coordinator, separate
finite LOGIN role, exact NOLOGIN capability role, forced-RLS context and
PostgreSQL denial-audit sink.

Fresh readback proved two principal generations, two parents, four revoked
surface rows, zero exchange grants, fourteen lifecycle audits, two retained
post-logout denial audits, exact per-practice RLS shapes and zero raw-value or
durable-target matches. The database, LOGIN role, capability role, harness,
relay, listeners, Word process and desktop developer registration are absent.

Five focused tests, the serial 176-test expanded shared-auth, Office, API Spine
and security-governance regression, and 29 Continuity/Compass/handover tests
pass. Python compilation, Ruff, both Microsoft Office manifest validations,
JSON parsing and diff checks pass.

PR 71's initial CodeQL wrapper found correctness/quality alert 545 with no
security-severity level. Yuri approved a structural repair: both concrete
harnesses now call one runtime-independent lifecycle initializer, while the
PostgreSQL harness constructs no in-memory authority. Fresh analysis at
`d005a152` passes all five PR checks, the native alert reports `fixed`, zero PR
CodeQL alerts remain open, and no dismissal or suppression occurred.

## Authority review

No new REST route, OpenAPI behavior, GraphQL operation, migration, product
router, identity adapter, product/document/patient/clinical read, command,
provider, cloud/IAM mutation, deployment, production, release or protected-ref
movement occurred. The API Spine remained the existing seven-route explicit
REST command boundary. The user-owned `docs/branding/raisa/` directory remained
untouched and excluded.

PR 70 protected integration remains deliberately paused because its master
`docs/**` push would invoke the public GitHub Pages deployment workflow. That
requires a separate explicit Yuri decision and does not affect this task-branch
acceptance.

## Claim limit

Acceptance proves only one provider-free authored-synthetic lifecycle in each
tested Office host through one exact local PostgreSQL LOGIN-to-capability-role
path with complete owned cleanup. It establishes no real identity, Microsoft
federation, product-data safety, distributed abuse resistance, organisational
deployment, production fitness or release readiness.

Reasoning level: Extra High for the combined real-host, database-role, RLS,
cookie, audit, cleanup and authority decision; High for final mechanical
verification.
