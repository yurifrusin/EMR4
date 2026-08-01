# Raisa shared application-auth PostgreSQL Office-host compatibility — closeout

Date: 2026-08-01

## Result

Accepted terminal result:
`raisa_shared_application_auth_postgresql_office_host_compatibility_pass`.

One installed-Word taskpane and one signed-in Word Online taskpane independently
completed the existing authored-synthetic session-cookie lifecycle through the
exact reserved HTTPS development origin and the accepted local PostgreSQL
runtime-role path. Each host created, validated, rotated, revalidated and logged
out its session, then proved post-logout validation returned the ordinary HTTP
401 authentication denial.

No application session remains usable.

## API Spine and authority boundary

The task harness mounted only the accepted seven REST application-auth routes
and its closed taskpane/result/evidence resources. It explicitly injected the
accepted `ApplicationAuthTransport`,
`RoleScopedPostgresApplicationAuthRuntime` and operational guard. It added no
route, OpenAPI behavior, GraphQL operation, migration, product router, product
read model, appointment/arrival/document command or second authorization
engine.

The API Spine guidance therefore influenced the implementation directly: the
session lifecycle remained one explicit, typed, auditable REST command boundary
and the database remained subordinate persistence rather than an alternate
authority surface.

## PostgreSQL and capability-role result

The task created one uniquely named disposable loopback database, one separate
finite LOGIN role and one NOLOGIN capability role. A fresh pooled connection
reported the LOGIN role as `session_user` and the exact capability role as
`current_user`; the identities were distinct, the LOGIN role had `NOINHERIT`
and no direct audit-table grant, and neither role could bypass RLS.

After both Office runs, fresh database readback found exactly:

- two principal-generation rows;
- two parent sessions;
- four surface sessions, all revoked after rotation and logout;
- zero exchange grants;
- fourteen lifecycle audit events; and
- two retained generic post-logout denial events, for sixteen audit rows total.

Each synthetic practice saw exactly one principal, one parent, two surface rows,
zero exchange grants and seven lifecycle audits under a fresh capability-scoped
RLS context. Every persisted opaque reference retained the exact SHA-256 shape.
No raw bootstrap, parent, surface, CSRF, nonce or generated secret matched any
persisted field, and no database name, role name or password entered durable
evidence.

## Real Office results

Installed Word used the fresh task-specific Restricted manifest and the same
direct developer-debugging admission that repaired the parent tranche:
`--debug-method direct --no-live-reload`. The user observed the exact
passed-and-logged-out terminal message. The matching stop operation removed the
developer registration before Word Online began.

Word Online used its independent fresh manifest through **My Add-ins → Upload
My Add-in** in a blank authored-synthetic document. The user observed the same
passed-and-logged-out terminal message. No cookie store, account, tenant,
document identifier or unrelated browser state was inspected.

## Verification

- Five focused plan, manifest, source-boundary, durable-evidence and full disposable-PostgreSQL
  lifecycle tests pass.
- The expanded shared-auth, Office-cookie, API Spine and security-governance
  regression passes 176 tests serially.
- The Continuity, Compass and compact-handover regression passes 29 tests.
- Python compilation and Ruff pass.
- Both fresh Restricted manifests pass Microsoft's Office manifest validator.
- The deterministic local rehearsal and both real-host runs produce the same
  exact database/audit outcome.
- JSON parsing and `git diff --check` pass.

## Cleanup and residue

The harness exited gracefully and wrote its terminal evidence after disposing
the finite pool. The exact disposable LOGIN role, database and capability role
were then independently queried and found absent. Ports 8001 and 4040 have no
listeners; the harness, ngrok and Word processes are absent; and the desktop
developer registration is removed. Both one-use bootstraps are consumed, none
is available or reserved, and the stopped relay makes the online taskpane
unavailable.

The user-owned untracked `docs/branding/raisa/` directory was preserved exactly
and never staged, tested, committed, pushed or included in evidence.

## Protected integration boundary

PR 70 was not merged. Repository inspection established that any `docs/**`
change pushed to `master` automatically triggers the public GitHub Pages
deployment workflow. Yuri authorised protected integration but did not broaden
the still-closed deployment boundary. This task therefore started from PR 70's
exact green head on
`codex/shared-auth-postgresql-office-host-compatibility`; local and origin
`master` and `handoff/current` remain unchanged.

That is a deliberate authority stop, not a compatibility failure. Review and
task-branch publication may continue. Protected integration requires Yuri's
explicit decision to permit the resulting one GitHub Pages rebuild.

## Claim limit and next gate

This proves one supervised provider-free authored-synthetic session-cookie
lifecycle in installed Word and one in Word Online through the accepted local
PostgreSQL, separate LOGIN role, exact capability role, forced-RLS and retained-
audit path with complete owned cleanup.

It does not prove real EMR4 identity, live user/practice mapping, Microsoft or
Office federation, every Office/WebView/browser/tenant policy, product-data
safety, distributed abuse resistance, organisational deployment, production
fitness or release readiness.

After review and any separately authorised protected integration, the smallest
architecture-only application-auth candidate is the real-identity and
Microsoft-federation boundary design and threat review, still without product
reads or live wiring. That remains a fresh Yuri decision. Dependabot alert 17
also remains native-open/`needs_review` pending its separate explicit
disposition decision.
