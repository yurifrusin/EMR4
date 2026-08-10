# Context Fabric recovery-anchor lock RLS recovery

Date: 2026-08-08

Status: deterministic diagnosis complete; bounded repository repair authorised by
the standing closed-plan authority.

Disposable behavior attempt 036 failed safely in authored-synthetic scenario
`BTR-E04`. PostgreSQL returned the contract-owned `CF004` at function line 299,
which maps exactly to the `NO_DATA_FOUND` branch following the
`context_recovery_anchor ... FOR SHARE` lock at inert SQL line 1251. The
immediately preceding plain read found exactly one anchor, so the row was not
lost. PostgreSQL's row-lock policy check could not see it because the forced-RLS
relation had SELECT and INSERT policies but no lock-only UPDATE policy.

The bounded repair adds `pol_cf_08_update_lock` for the existing COORDINATOR and
LIFECYCLE capabilities. Its `USING` predicate permits row-lock visibility only;
its identical `WITH CHECK` predicate ends in `AND FALSE`, preserving the
append-only anchor and denying mutation. Both roles keep empty direct-table DML,
all entry-point grants remain unchanged, and the typed body program and twenty
behavior scenarios remain unchanged.

The repaired structural parent must reseal the unchanged typed body, regenerate
the inert DDL and manifest, pass a fresh parse/catalogue reproduction, rebind the
unchanged behavior contract and pass a fresh exact-HEAD independent veto before
one further disposable behavior attempt.

This is provider-free repository and disposable authored-synthetic evidence
only. It grants no application wiring, operational database, product or patient
data, commands, provider call, deployment, release, Pages or protected-ref
authority.
