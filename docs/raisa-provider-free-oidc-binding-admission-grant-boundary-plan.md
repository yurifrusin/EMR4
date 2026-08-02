# Raisa provider-free OIDC binding and admission-grant boundary plan

Date: 2026-08-02

Status: authorised implementation tranche

Parent: `raisa-provider-free-oidc-start-callback-transport-boundary`

## Outcome sought

Resolve one already-verified, authored-synthetic Microsoft principal through an
exact HMAC-only PostgreSQL binding boundary and issue one origin- and
surface-bound bearer admission grant lasting exactly 60 seconds. Return the
raw grant only through the accepted exact-origin callback bridge, while
creating no application session and reading no product truth.

## Authority

Yuri authorised this fresh gate and the following logical redemption tranche
unless a material directional choice arises. This tranche may add one migration,
an exact `SECURITY DEFINER` resolver, least-authority PostgreSQL role contracts,
an admission-grant model/service, default-off transport composition, API Spine
changes, disposable local PostgreSQL/HTTP evidence, tests, documentation,
continuity and task-branch publication.

It may not call Microsoft or another provider, use a real tenant or identity,
create or redeem an application session, set an authentication cookie, read
product/patient/clinical data, persist deployment credentials, change cloud or
IAM, deploy, release, move a protected ref, rebuild Pages, decide Dependabot
alert 17 or include `docs/branding/`.

## Frozen contract

1. The accepted start/callback routes remain default-off. Binding/grant work is
   reachable only when a task-scoped admission service is explicitly injected.
2. The service accepts only the typed `CompletedAuthorization` emitted by the
   accepted maintained-verifier port. It rejects any result claiming existing
   authorization, session or product release.
3. Raw issuer, tenant, object, subject, audience and correlation values are
   converted to versioned keyed-HMAC references before database resolution.
   None is stored in clear text or emitted to the browser.
4. A `SECURITY DEFINER` function validates every argument, sets transaction-
   local HMAC policy values, resolves exactly one active binding using issuer,
   tenant, object and subject HMACs, and appends a resolved or rejected audit
   row before returning. Audit failure aborts the transaction.
5. The finite `NOINHERIT` deployment login has membership in exactly two
   no-login capabilities: resolver execution and admission-grant issuance. A
   separate no-login owner owns the resolver function and alone receives the
   binding-select/audit-insert privileges needed inside it.
6. The resolver caller receives no direct binding or audit-table privilege.
   The grant issuer receives no binding-table privilege; forced RLS permits
   only exact-practice grant metadata needed for capacity and one practice-
   scoped grant insert. A database trigger owned by the ungranted resolver
   owner makes the required issued-audit row inseparable from that insert.
7. A grant contains only HMAC/digest references, internal authored-synthetic
   binding/user/practice references and version, exact origin/surface/return
   target, audience HMAC, policy, correlation HMAC, issue/expiry/status/version
   and data class. It contains no token, raw external identity or product data.
8. The raw grant is 256 bits from the operating-system CSPRNG, stored only as a
   versioned keyed SHA-256 HMAC, returned exactly once, and expires exactly 60
   seconds after issue. Capacity is bounded and no expiry extension exists.
9. Binding resolution, grant insertion and both required audit rows occur in
   one database transaction. Any role, RLS, capacity, validation, uniqueness or
   audit failure rolls back all effects and becomes a generic temporary failure.
10. Success changes the callback bridge status to `admission_grant_issued` and
    adds the raw grant. The value appears only in the exact-origin message body,
    never in a URL, cookie, header, storage API, log or database field.
11. No redemption, internal-principal freshness read, application session,
    authentication cookie or product authority is present in this tranche.

## Acceptance

- A disposable PostgreSQL database migrates to the single head and provisions
  uniquely named finite login, resolver-call, resolver-owner and grant-issuer
  roles with no superuser/create/replication/bypass-RLS attributes.
- Direct login and resolver-call access to binding/audit/grant tables is denied;
  grant issuer cannot read bindings; resolver owner cannot insert grants.
- One real loopback HTTP start/callback lifecycle resolves an exact authored-
  synthetic binding and returns one raw grant only in the exact-origin bridge.
- PostgreSQL holds only HMAC/digest references, exact 60-second expiry and the
  required resolved and issued audit rows; no raw UUID, bearer, key or token is
  present in table, evidence, server log or URL residue.
- Subject/tenant/object/issuer mismatch, inactive/missing binding, duplicate
  operation, grant capacity, audit denial and role misuse fail closed with no
  partial grant or success bridge.
- No provider call, session row, cookie, product read or external side effect
  occurs; the disposable database and every task role are removed.
- Focused and inherited API/auth/security/continuity checks pass, with any
  unchanged repository-wide collection barrier reported exactly.

## Handoff

The preauthorised descendant is the provider-free atomic admission-grant
redemption bridge into the accepted application-session runtime. It requires a
fresh five-source rehydration and must re-resolve the binding plus fresh
internal principal truth before atomically consuming the grant and committing
any session.
