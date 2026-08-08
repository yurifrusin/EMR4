# Provider-free behavior rehearsal snapshot special-form recovery

Date: 2026-08-08

Status: deterministic repair candidate; runtime closed pending fresh veto

Bounded attempt 010 identified the failing site as `scenario_snapshot` and the
single safe SQLSTATE as `42883`. The snapshot renderer had emitted
`pg_catalog.coalesce(...)`. PostgreSQL `COALESCE` is a SQL conditional special
form, not a schema-qualified callable function, so the read-only query failed
before the first scenario.

The repair removes only the invalid `pg_catalog.` qualifier. Every aggregate,
row conversion, ordering expression, digest, relation population, read-only
transport and snapshot shape remains unchanged. A deterministic test forbids
the invalid spelling and requires one `COALESCE` per snapshotted relation.

Failure 010 contains no query values or stderr prose, records zero executed
scenarios and proves exact cleanup. Another behavior run remains ineligible
until deterministic checks and a fresh exact-HEAD independent veto pass.
