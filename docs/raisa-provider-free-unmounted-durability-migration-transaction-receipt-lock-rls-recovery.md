# Durability structural receipt-lock RLS recovery

Date: 2026-08-08

Status: bounded structural parent repaired; descendants remain closed.

The structural contract now adds exactly one PUBLIC permissive UPDATE policy,
`pol_cf_09_update_lock`, to
`context_classified_observation_receipt`. Its exact COORDINATOR session-binding
predicate supplies the row visibility PostgreSQL requires for the typed
`FOR UPDATE` replay lock in `apply_durability_transition_v1`. The identical
`WITH CHECK` predicate ends in `AND FALSE`, so it cannot authorize receipt
mutation.

The coordinator retains empty direct-table DML. The immutable-receipt
invariant, function entry points, execute grants, forced RLS, typed body and
twenty-scenario behavior population are unchanged. Removal, predicate widening,
capability substitution and role reassignment are all mutation-tested.

The repaired structural contract is sealed at
`sha256:18fb00ff02820c31b4fcab4de096393cbea49e0a37ebb28d65c5eb2d6f154cfd`.
This parent must be committed before the unchanged typed body can be rebound
and the inert SQL can be regenerated. Nothing in this change is executable or
mounted, and no runtime, operational database, product data or external
authority is opened.
