# Raisa provider-free session practitioner-directory read bridge closeout

Date: 2026-08-02

Result: `provider_free_session_practitioner_directory_read_bridge_pass`

## Outcome

The selected provider-free product-authorization direction passes. One
explicitly constructed, default-off GraphQL router can accept an existing
authored-synthetic application session, reload exact current product-principal
truth, commit an endpoint-owned authorization audit, and reuse the existing
active practitioner-directory read and display-safe projection.

The router is not mounted in `app.main`. No patient, clinical, appointment,
provider, real-identity, command, mutation, production or release authority is
created.

## Implemented boundary

- fixed `practice-practitioner-directory-read.v1` policy, action
  `practice.practitioner-directory.read`, resource `practitioner_directory`,
  and active-only scope;
- exact surface, origin, audience, session-generation and CSRF admission with
  generic 401/403/503 failures;
- process-local injected `synthetic-*` references mapped only to disposable
  product UUIDs, followed by a fresh exact-column user/role/practice/
  practitioner-link reload;
- required append-only `auth.authorization_allowed` or denied audit before
  any practitioner row can be released;
- separate finite `NOINHERIT` product login/capability roles with exact-column
  `SELECT` grants and no application-auth or product-write access;
- an unmounted GraphQL factory which reuses the API Spine resolver and closes
  its product session after each request, while a bounded pre-auth parser
  admits only JSON POST with the exact directory path/fields and rejects GET,
  aliases, fragments, directives, introspection, health, practice-id-only and
  mutations; and
- a shared practitioner query hardened from full ORM entity loads to only the
  five display-safe projection sources.

## Live-local evidence

A uniquely named disposable PostgreSQL database upgraded, downgraded to parent
`t9u0v1w2x3y4`, re-upgraded to head `u0v1w2x3y4z5`, passed `alembic check`, and
served one real loopback HTTP GraphQL path. The allowed request returned exactly
two active same-practice practitioners with only `id`, derived `displayName`,
optional `roleLabel`, `active`, and optional active same-practice
`defaultLocation { id name }`.

Wrong origin, CSRF, unknown session, unmapped principal, stale role, inactive
user, inactive enumeration and forced audit failure released no directory
data. A cross-practice GraphQL id preserved the existing no-leak `null`. The
allow and denial audits contained no cookie, CSRF, product UUID, practitioner
name, email or prohibited provider identifier. Six direct login/capability
probes all failed with PostgreSQL `42501`.

The loopback server stopped and the disposable database plus all four task
roles were proved absent. Provider calls, real identities, patient/clinical
reads, product writes, GraphQL mutations, deployments and production changes
were zero.

## Verification

- live-local HTTP/backend/PostgreSQL acceptance: pass;
- focused bridge and shared directory resolver/REST tests: 69 passed;
- inherited shared-auth, Office, federation and three provider-free OIDC
  descendants: 212 passed with the frozen parent runtime-evidence equality
  node explicitly deselected;
- broad practitioner-directory/API Spine history: 390 passed; two static
  historical gates still reject GraphQL symbols already present at parent HEAD
  and are not regressions from this patch;
- canonical Ruff/lint and reviewed Bandit gates: pass;
- `pip check` and `pip-audit -r requirements.txt --desc`: pass;
- Office manifest validation and production-only `npm audit`: pass with zero
  production vulnerabilities;
- full development-tree npm audit: the governed upstream-only toolchain
  baseline remains 19 findings (13 high, 6 moderate); no lockfile change or
  forced override was made;
- reversible migration and current-head check: pass; and
- fresh repository-wide collection reconfirmed the unchanged parent barrier:
  `tests/test_api_spine_confirmation_family_idempotency_integration.py` imports
  removed `_BERNIE_SESSION_STORE`.

The committed parent runtime-foundation evidence was not regenerated merely
to replace its pre-descendant source hash. Historical OIDC replay harnesses
were reconciled to verify their own exact frozen Alembic revision without
claiming it remains the modern metadata head.

## Side effects and limits

No live provider, Microsoft/Office identity, real principal, patient or
clinical data, product mutation, cloud/IAM action, deployment, production,
release, protected-ref movement, Pages rebuild or Dependabot disposition
occurred. The user-owned `docs/branding/` directory was preserved and excluded
from reading, testing, evidence, staging and commits.

This result proves only a default-off authored-synthetic active-practitioner
directory read. It does not establish real identity mapping, patient or
clinical read safety, a generally mounted product endpoint, Office UI
consumption, product-table RLS, production secret custody, distributed abuse
resistance, monitoring/SIEM, deployment, production or release readiness.
