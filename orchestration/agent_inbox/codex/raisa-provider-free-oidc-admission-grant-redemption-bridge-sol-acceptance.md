# Sol acceptance: provider-free OIDC admission-grant redemption bridge

Date: 2026-08-02

Decision: `accepted`

Result: `provider_free_oidc_admission_grant_redemption_bridge_pass`

## Acceptance judgment

The implementation satisfies the frozen final descendant. The raw 256-bit
grant is HMACed before SQL; one exact security-definer function locks it under
forced RLS, verifies its original surface/origin/audience/policy, reselects the
same active immutable binding/version, and locks one current authored-synthetic
user/practice/role/practitioner-link truth row.

The authority split is fail closed. The finite login enters one no-login call
capability; that capability has no direct federation binding, grant, audit or
truth access. The ungranted no-login function owner cannot access application
session tables. Row-lock-enabling column privileges have exact owner-only RLS
lock policies with `WITH CHECK (false)`, so they permit `FOR KEY SHARE` but no
mutation.

Grant consumption, federation audit, accepted runtime policy, application-auth
audit and hash-only parent/surface state share one SQLAlchemy transaction. The
route receives values only after commit and then sets the accepted session and
CSRF cookies. Replay/concurrency, current binding/principal failures, required-
audit rollback, raw-value residue and complete cleanup all pass over real
loopback HTTP and disposable PostgreSQL.

## Evidence reviewed

- frozen plan, design and threat-model delta;
- reversible migration, ORM model, role split, operational pool, redemption
  service, accepted persistence transaction step, router and API Spine;
- successful sanitized live-local HTTP/backend/PostgreSQL evidence;
- focused and inherited security/auth/Office/API/continuity regressions; and
- lint, compilation, dependency, migration, security and diff checks.

## Limits

This accepts only provider-free authored-synthetic redemption and session
creation. It establishes no live Microsoft/provider call, real identity or
product truth, real binding administration, product authorization/read,
production credential/key lifecycle, cloud/IAM, deployment, protected
integration, production, release, Pages or Dependabot disposition authority.

Reasoning level: High. The architecture and security meaning were frozen before
implementation; PostgreSQL's row-lock privilege requirement was reconciled
with a non-writable RLS capability, and no failed gate was overridden.
