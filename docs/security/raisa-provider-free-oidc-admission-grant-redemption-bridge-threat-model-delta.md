# Threat-model delta: provider-free OIDC admission-grant redemption bridge

Date: 2026-08-02

Parent: `docs/security/raisa-provider-free-oidc-binding-admission-grant-boundary-threat-model-delta.md`

## New trust boundaries

1. A raw 256-bit admission grant crosses from the original cookie partition
   into a CSRF- and exact-origin-gated REST command.
2. One execution-only capability crosses an exact security-definer function
   into grant lock/consume, current binding, synthetic principal truth and
   required federation audit authority.
3. The function result crosses into the accepted application-auth policy
   engine inside the same database transaction.
4. One committed surface bearer and CSRF pair cross to exact `__Host-` cookies.

No live identity or product boundary opens.

## Threats and controls

| Threat | Control | Failure |
|---|---|---|
| Grant theft from URL/log/storage | Bounded JSON body, pre-SQL HMAC, no URL/header/storage/log/audit field | Generic denial; residue gate fails |
| Cross-partition redemption | Exact stored surface, server-derived exact origin, configured audience HMAC, pre-auth CSRF pair | Required rejection audit; no consume/session |
| Replay or concurrent double mint | `FOR UPDATE` exact grant lock and monotonic active-v1 to consumed-v2 transition | At most one commit; later request gets generic conflict/no cookie |
| Stale binding remains authoritative | Active binding reselected by immutable binding ref and exact version/user/practice/provider | Rejected audit; grant unconsumed |
| Stale internal role/membership | Same-transaction locked authored-synthetic current-truth row and active/link checks | Rejected audit; no session |
| Synthetic proof is mistaken for product truth | Synthetic-only checks, no product foreign key/import/privilege, fixed data class | Migration/static/evidence failure |
| Call role reads federation identity state | Execution-only function; direct table privileges denied | Privilege acceptance fails |
| Function owner creates sessions | Owner receives no application-auth table privilege and is ungranted/no-login | Direct-access acceptance fails |
| Security-definer hijack | Empty search path, fully qualified objects, fixed signature, no dynamic SQL, PUBLIC execute revoked | Migration/static gate fails |
| Grant consumed but session/audit absent | Same SQLAlchemy session/transaction for function and accepted runtime | Rollback; no cookie |
| Session written but commit uncertain | Service returns only after transaction context commits; route sets cookies afterward | Generic unavailable; no response authority |
| Second session policy engine diverges | Reuse accepted `ApplicationAuthRuntime.create_session` via the persistence transaction step | Regression/static gate fails |
| Parent bearer escapes | Discard raw parent after hash-only persistence; return only surface value to cookie boundary | Residue/response gate fails |
| Cookie downgrade | Reuse exact accepted Secure/HttpOnly/Path=/no-Domain/SameSite=None/Partitioned helpers | Header acceptance fails |
| Failure becomes an identity oracle | Fixed 401/409/503 classes and generic bodies; detailed reasons metadata-only | Response-shape gate fails |
| Rejection audit amplifies | Accepted pre-route bounded limiter; unknown/replay denial uses retained generic transport audit | Rate/audit regression fails |

## Residual gates

This does not establish live Microsoft interoperability, real identity or
principal truth, product authorization/read safety, binding administration,
production HMAC/session key custody, hosted database/network policy,
distributed abuse resistance, paging/SIEM, deployment, protected integration,
production or release.
