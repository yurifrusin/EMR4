# Durability structural admission-lock RLS recovery

Date: 2026-08-08

Status: bounded structural parent repaired; descendants remain closed.

The structural contract now adds exactly one PUBLIC permissive UPDATE policy,
`pol_cf_04_update_lock`, to
`context_proofread_observation_admission`. Its exact COORDINATOR session-binding
predicate supplies the row visibility PostgreSQL requires for the typed
`FOR UPDATE` lock in `apply_durability_transition_v1`. The identical
`WITH CHECK` predicate ends in `AND FALSE`, so it cannot authorize admission
mutation.

The coordinator retains empty direct-table DML. The immutable-admission
invariant, function entry points, execute grants, forced RLS, typed body and
twenty-scenario behavior population are unchanged. Removal, predicate widening,
capability substitution and role reassignment are all mutation-tested.

The repaired structural contract is sealed at
`sha256:80d5b57eadef0e6ede54c48fc842fe5567723c0a9cdebe288efbf63048c4b3ac`.
This parent must be committed before the unchanged typed body can be rebound
and the inert SQL can be regenerated. Nothing in this change is executable or
mounted, and no runtime, operational database, product data or external
authority is opened.
