# Raisa provider-free OIDC binding and admission-grant boundary closeout

Date: 2026-08-02

Result: `provider_free_oidc_binding_admission_grant_boundary_pass`

## Outcome

The second of Yuri's three authorised logical descendants passes. An explicitly
injected callback transport can now turn one accepted, already-verified
authored-synthetic Microsoft principal into one exact-origin bearer admission
grant lasting exactly 60 seconds. The application router remains default 404,
and the grant is not an application session or product authorization.

## Implemented boundary

- a forced-RLS PostgreSQL admission-grant table containing only versioned
  HMAC/digest references, internal authored-synthetic binding/user/practice
  references, exact surface/origin/target, policy, timing and state;
- an exact `SECURITY DEFINER` resolver with an empty search path which compares
  issuer, tenant, object and subject HMACs and appends a required resolved or
  rejected audit row before returning;
- one finite `NOINHERIT` login, separate resolver-call and grant-issuer
  capabilities, and an ungranted `NOLOGIN` resolver owner;
- a database after-insert trigger owned by that no-login owner, making the
  `federation.admission_grant_issued` audit inseparable from grant insertion
  while leaving the grant issuer with no direct audit privilege;
- a separately keyed 256-bit bearer digest, exact 60-second lifetime,
  transactional capacity bound and release only after known database commit;
  and
- an exact-origin no-store callback message containing
  `admission_grant_issued` and the raw bearer once, with no URL, cookie, storage
  or log field.

## Evidence

One unique disposable loopback PostgreSQL database was migrated to head
`s8t9u0v1w2x3`. The proof provisioned two accepted attempt-store roles and four
new binding/grant roles, seeded one HMAC-only authored-synthetic binding, and
served the ordinary FastAPI router on a real Uvicorn loopback socket.

One start/callback lifecycle consumed the encrypted attempt, resolved the exact
four-component binding, appended resolved and issued audit, committed one
active version-one grant with exact 60-second expiry, and returned the raw
256-bit bearer once in the exact-origin message. The database contained only
its separately keyed HMAC and zero raw-bearer matches.

Missing-subject resolution appended a rejected audit and released no grant.
Capacity and required-audit failure rolled back. Direct login, resolver-call,
grant-issuer and resolver-owner probes all returned PostgreSQL `42501` on
out-of-scope table/role edges. The grant issuer saw one own-practice grant and
zero foreign-practice grants. The server stopped and the database plus all six
task roles were proved absent.

## Verification

- disposable live-local HTTP/backend/PostgreSQL acceptance: pass;
- focused binding/grant and current continuity tests: 12 passed;
- inherited OIDC/federation/shared-auth/API Spine suite: 323 passed after exact
  descendant-aware harness reconciliation;
- current continuity/Compass/handover suite: 35 passed;
- targeted Ruff and compilation: pass;
- targeted application Bandit: no findings;
- `pip check`: no broken requirements;
- `pip-audit -r requirements.txt --desc --progress-spinner off`: no known
  vulnerabilities;
- one Alembic head remains `s8t9u0v1w2x3`; disposable upgrade and
  `alembic check` pass; and
- `git diff --check`: pass.

The ordinary development database remains intentionally unmodified. The known
repository-wide collection barrier at the unchanged parent import of removed
uppercase `_BERNIE_SESSION_STORE` remains outside this tranche.

## Side effects

External/provider calls, real identities, application sessions, session
cookies, product/patient/clinical reads, cloud/IAM mutations, deployments,
production changes, releases, protected-ref movements, Pages rebuilds and
Dependabot dispositions are all zero. The user-owned `docs/branding/` directory
was not modified, staged, tested, read into evidence, committed or removed.

## Residual gates

The next preauthorised descendant is atomic one-use admission-grant redemption
into the accepted application-session runtime. It requires a fresh five-source
rehydration and must re-resolve the exact binding/version plus fresh internal
user/practice/role truth before committing grant consumption and any session.

Live Microsoft, real identity, product reads, production secret custody,
hosted database/network policy, distributed abuse resistance, monitoring/SIEM,
cloud/IAM, deployment, protected integration, production and release remain
separately closed.
