# Raisa provider-free application-session practitioner-directory read bridge plan

Date: 2026-08-02

Status: authorised implementation tranche

Parent: `raisa-provider-free-oidc-admission-grant-redemption-bridge`

## Outcome sought

Prove one existing display-safe product read behind the accepted opaque
application session without opening patient or clinical data. A default-off
GraphQL context adapter must authenticate the exact surface cookie, reload one
current authored-synthetic product user, admit the endpoint-owned practitioner-
directory policy and required durable audit, and only then reuse the existing
shared practitioner-directory read service.

## Authority

Yuri selected the recommended provider-free product-authorization direction.
This tranche may add one reversible audit-contract migration, a bounded runtime
authorization operation, a task-scoped authored-synthetic principal mapping,
one unmounted GraphQL context/router factory, deterministic disposable local
PostgreSQL/HTTP evidence, tests, documentation, continuity and task-branch
publication.

It may not mount the adapter in `app.main`, read patient or clinical data, add a
GraphQL mutation, change the existing bearer-authenticated GraphQL route, call
Microsoft or another provider, use a real identity, persist a real principal
mapping, write product state, change cloud/IAM, deploy, rebuild Pages, decide
Dependabot alert 17, move a protected ref or include `docs/branding/`.

## Frozen contract

1. The accepted `Query.practice.practitioners` field remains the read surface.
   No second directory query, REST command or mutation is added.
2. The application-session adapter is constructed only by an explicit factory
   and is not imported or mounted by the production composition root. The
   existing bearer-token GraphQL context remains unchanged.
3. The factory binds one server-selected surface. Each request requires the
   exact configured HTTPS origin, accepted `__Host-` application-session
   cookie, and exact pre-authentication CSRF cookie/header pair. Client role,
   practice or surface claims confer no authority.
4. A task-scoped immutable mapping may join bounded `synthetic-*` application
   principal references to disposable authored-synthetic product UUIDs. It is
   injected, process-local, contains no external identifier, and creates no
   production or real-identity mapping contract.
5. Before directory access the adapter reloads one current product `User` and
   requires active state, exact mapped practice, exact current backend role and
   exact practitioner link when the session carries one. Unknown, stale or
   cross-practice mapping fails before product data access.
6. The endpoint-owned policy is
   `practice-practitioner-directory-read.v1`, action
   `practice.practitioner-directory.read`, resource
   `practitioner_directory`. It permits only `activeOnly=true`; inactive staff
   enumeration is closed for every role in this bridge.
7. The accepted application-auth runtime rechecks the current parent/surface
   status, generation, exact surface/origin/audience and fresh mapped principal.
   It appends `auth.authorization_allowed` or the existing bounded denial event
   under the new exact policy. Audit failure releases no directory data.
8. A successful current-request-only decision is not a capability token. The
   GraphQL resolver immediately calls the existing
   `list_practitioner_directory` service with the freshly loaded user and
   existing bounds/order/same-practice filters.
   The product session uses a separate finite `NOINHERIT` login/capability
   pair with exact-column `SELECT` grants only; it has no application-auth
   table access and no product write privilege.
   The task router accepts only bounded JSON POST queries with one exact
   `practice.practitioners` selection, safe projection fields and fixed
   arguments; GET queries, aliases, fragments, directives, introspection,
   health, practice-id-only and mutation shapes are rejected before auth.
9. The projection remains exactly `id`, derived `displayName`, optional
   `roleLabel`, `active`, and optional same-practice active
   `defaultLocation { id name }`. Provider/prescriber/AHPRA/HPI-I identifiers,
   contact data, schedule, appointment, patient and clinical fields remain
   absent.
10. Practice-id mismatch remains the existing no-leak `null`; unknown session
    is generic HTTP 401, authenticated policy denial is generic GraphQL
    `FORBIDDEN`, and required audit/database unavailability releases no data.
11. HTTP and evidence artifacts contain counts, fixed authored-synthetic labels
    and hashes only. Names, emails, product UUIDs, cookie/CSRF values and session
    references are excluded.
12. The acceptance database, task roles, engines, server and authored-synthetic
    product rows are disposable and must be proved absent after cleanup.

## Acceptance

- A reversible migration makes `auth.authorization_allowed` and the exact new
  policy admissible while preserving the append-only forced-RLS audit table and
  the prior policy/event values.
- Unit tests prove fixed policy/action/resource values, fresh user/practice/
  role/link matching, active-only enforcement, current-request-only decisions,
  required audit and absence of generic client-selected authorization.
- Real loopback HTTP through an explicitly constructed GraphQL router reads two
  active authored-synthetic practitioners from the mapped practice with exact
  REST/shared-service projection parity and a committed allowed audit before
  release.
- Wrong origin/CSRF/session, stale role, inactive user, mapping mismatch,
  inactive enumeration, cross-practice practice id and forced audit failure
  release no practitioner rows; denial audit is admitted where the application
  session is identifiable.
- Another practice's practitioners and every prohibited sensitive field remain
  absent. Provider, identity-provider, patient, clinical and product-write
  counts remain zero.
- Focused and inherited GraphQL/API Spine/application-auth/Office/security/
  continuity suites pass. The unchanged repository-wide collection barrier is
  reported exactly if still present.

The parent runtime-foundation evidence-equality node is intentionally
deselected in this descendant. Its committed evidence is immutable and hashes
the pre-descendant `application_auth_runtime.py`; regenerating it would rewrite
historical proof rather than validate this tranche. All other tests in that
file remain required. Historical OIDC live-replay harnesses continue to target
their own frozen Alembic revisions and verify `current`; they do not run
`alembic check` against this descendant's newer metadata.

## Handoff

This proves one provider-free display-safe product read only. Patient or
clinical reads, a real principal mapping, production RLS for product tables,
general session-backed GraphQL mounting, live Microsoft interoperability,
binding administration, product commands, deployment, protected integration,
production and release remain fresh decisions.
