# Threat-model delta: durability behavior RLS lock visibility

Date: 2026-08-09

Parent: provider-free disposable PostgreSQL durability behavior/transaction
rehearsal

| Threat | Recovery control | Residual boundary |
|---|---|---|
| Removing the row lock avoids RLS filtering but permits concurrent registration races | Preserve exact `SELECT ... FOR UPDATE`; change only the applicable `UPDATE USING` policy visibility | Concurrency beyond the frozen single-session rehearsal remains a later finite gate |
| Lifecycle lock visibility becomes lifecycle write authority | `pol_cf_01_update USING` admits producer or lifecycle only for row eligibility; `WITH CHECK` remains producer-only; lifecycle retains zero direct table DML/SELECT and only closed security-definer execution | Any future lifecycle grant or owner change requires a separate authority review |
| Broad lifecycle addition reaches frames, watermarks or unrelated relations | Only `pol_cf_01_update` changes; `pol_cf_10_update` and `pol_cf_11_update` remain producer/coordinator-only | Other lifecycle initialization effects retain their accepted insert/select policies |
| Policy drift is hidden by regenerated hashes | Structural semantics and hostile tests independently reject missing lock visibility and lifecycle write-check widening before reseal | PostgreSQL-version changes remain separate gates |
| Diagnosis leaks raw database values | Persist only row count, binding boolean, zero/multiple lock class, hashes and exact cleanup; raw error is digest-only and not retained | The diagnosis proves this one lock path only |

No protected, patient, clinical or product data, provider, operational
database, application runtime, watcher/listener, command/write, deployment,
production, release, Pages or protected-ref boundary changes.
