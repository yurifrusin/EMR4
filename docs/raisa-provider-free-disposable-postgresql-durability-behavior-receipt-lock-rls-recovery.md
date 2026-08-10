# Context Fabric receipt-lock RLS recovery

Date: 2026-08-08

Status: deterministic diagnosis complete; bounded repository repair authorised by
the standing closed-plan authority.

Disposable behavior attempt 042 failed safely in authored-synthetic scenario
`BTR-I03`. PostgreSQL returned the contract-owned `CF004` at function line 210,
which maps exactly to the missing-row exception following the
`context_classified_observation_receipt ... FOR UPDATE` lock at inert SQL line
1168. The preceding ordinary receipt read found exactly one row. PostgreSQL's
row-lock policy check then hid it because the forced-RLS receipt relation has
SELECT and INSERT policies but no lock-only UPDATE policy.

The bounded repair adds `pol_cf_09_update_lock` for the existing COORDINATOR
capability. Its `USING` predicate permits row-lock visibility only; its
identical `WITH CHECK` predicate ends in `AND FALSE`, preserving immutable
receipts and denying mutation. The coordinator keeps empty direct-table DML,
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
