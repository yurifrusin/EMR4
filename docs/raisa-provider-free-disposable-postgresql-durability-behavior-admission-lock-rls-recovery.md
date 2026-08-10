# Context Fabric admission-lock RLS recovery

Date: 2026-08-08

Status: deterministic diagnosis complete; bounded repository repair authorised by
the standing closed-plan authority.

Disposable behavior attempt 037 failed safely in authored-synthetic scenario
`BTR-E04`. PostgreSQL returned the contract-owned `CF004` at function line 307,
which maps exactly to the `context_proofread_observation_admission ... FOR
UPDATE` lock at inert SQL line 1262. The preceding ordinary admission read
found the primary row. PostgreSQL's row-lock policy check then hid it because
the forced-RLS admission relation has SELECT and INSERT policies but no
lock-only UPDATE policy.

The bounded repair adds `pol_cf_04_update_lock` for the existing COORDINATOR
capability. Its `USING` predicate permits row-lock visibility only; its
identical `WITH CHECK` predicate ends in `AND FALSE`, preserving immutable
admissions and denying mutation. The coordinator keeps empty direct-table DML,
all entry-point grants remain unchanged, and the typed body program and twenty
behavior scenarios remain unchanged.

The repaired structural parent must reseal the unchanged typed body, regenerate
the inert DDL and manifest, pass a fresh parse/catalogue reproduction, rebind
the unchanged behavior contract and pass a fresh exact-HEAD independent veto
before one further disposable behavior attempt.

This is provider-free repository and disposable authored-synthetic evidence
only. It grants no application wiring, operational database, product or patient
data, commands, provider call, deployment, release, Pages or protected-ref
authority.
