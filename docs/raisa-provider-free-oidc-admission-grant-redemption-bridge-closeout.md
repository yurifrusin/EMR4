# Raisa provider-free OIDC admission-grant redemption bridge closeout

Date: 2026-08-02

Result: `provider_free_oidc_admission_grant_redemption_bridge_pass`

## Outcome

The third and final provider-free descendant passes. One default-off exact-
origin command can redeem an authored-synthetic 60-second admission grant once,
recheck its current binding/version and fresh synthetic security-principal
truth, and create the accepted parent/surface application session in the same
PostgreSQL transaction. The callback still sets no cookie and no product
authority is created.

## Implemented boundary

- one forced-RLS authored-synthetic security-principal truth table with no
  product foreign key or live-identity import;
- one finite `NOINHERIT` login, execution/session capability, and ungranted
  `NOLOGIN` redemption owner;
- one empty-search-path security-definer function which locks the HMAC-selected
  grant, checks exact surface/origin/audience/policy, reselects the active
  binding/version, locks fresh user/practice/role/practitioner-link truth, and
  commits only the active-v1 to consumed-v2 transition with required audit;
- same-session reuse of `ApplicationAuthRuntime.create_session`, preserving the
  accepted single session policy engine and hash-only parent/surface storage;
- one default-off REST redemption route with generic 401/409/503 failures and
  exact no-store `__Host-` Secure, HttpOnly, Path=/, no-Domain, SameSite=None,
  Partitioned session/CSRF cookies emitted only after commit; and
- an API Spine revision which returns the CSRF value once for same-origin
  in-memory use while retaining the callback's no-cookie invariant.

## Evidence

A uniquely named disposable database upgraded, downgraded to the parent and
re-upgraded to head `t9u0v1w2x3y4`. Real loopback HTTP consumed one issued
grant, committed one exact Word Online session and set two frozen cookies.
Replay returned generic conflict with no cookie; unknown and foreign-origin
requests remained generic denials.

Two independent database sessions raced a second grant and produced exactly
one committed session and one conflict. Surface mismatch, inactive membership
and revoked binding each appended bounded rejection evidence and created no
session. Forced federation-audit and application-audit outages rolled back
grant consumption and session state. Direct login/call/owner probes denied all
six out-of-scope table or role edges with PostgreSQL `42501`. Raw grants,
surface values and CSRF values matched no database or evidence field. The
server stopped and the database plus all seven task roles were proved absent.

## Verification

- disposable live-local HTTP/backend/PostgreSQL acceptance: pass;
- focused redemption plus parent binding/continuity tests: 20 passed;
- inherited OIDC/federation/shared-auth/Office/API Spine suite: 324 passed after
  exact descendant-aware API-status, route-inventory and migration-head
  reconciliation;
- continuity, Compass and live-handover suite: 57 passed;
- targeted Ruff and compilation: pass;
- targeted application Bandit: no findings;
- `pip check`: no broken requirements;
- `pip-audit -r requirements.txt --desc --progress-spinner off`: no known
  vulnerabilities;
- one Alembic head remains `t9u0v1w2x3y4`; reversible disposable migration and
  `alembic check` pass; and
- API YAML parse and `git diff --check`: pass.

Fresh repository-wide collection reconfirmed the known unchanged parent barrier:
`tests/test_api_spine_confirmation_family_idempotency_integration.py` imports
removed uppercase `_BERNIE_SESSION_STORE`. It remains outside this tranche.

## Side effects

External/provider calls, real identities, product/patient/clinical reads,
cloud/IAM mutations, deployments, production changes, releases, protected-ref
movements, Pages rebuilds and Dependabot dispositions are all zero. The
user-owned `docs/branding/` directory was not modified, staged, tested, read
into evidence, committed or removed.

## Residual gates

This closes the three authorised provider-free bridge descendants. Live
Microsoft interoperability, real internal principal truth, identity binding
administration/recovery, product authorization and reads, production
credential/HMAC/session-key custody, hosted connectivity, distributed abuse
resistance, monitoring/SIEM, cloud/IAM, deployment, protected integration,
production and release remain separately closed.
