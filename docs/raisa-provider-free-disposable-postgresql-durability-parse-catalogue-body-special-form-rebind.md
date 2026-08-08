# Disposable PostgreSQL parse/catalogue body special-form rebind

Date: 2026-08-08

Status: exact PostgreSQL 16 parse/catalogue rehearsal passed

The exact parse/catalogue rehearsal is rebound to source commit
`cf51e3a8de270869f4f4da3e36f6b5167b0c502a`, whose canonical inert SQL is
1,402,341 LF bytes with SHA-256
`sha256:afe131084e8a433fe87c56b48c21abef941fb04450efb252fbed10a287053b14`.

Only invalid `pg_catalog.coalesce(...)` spellings were replaced by valid
unqualified `COALESCE(...)` special forms. The structural and typed body
contracts, 412-statement population, exact catalogue expectations, authored-
synthetic prerequisites, containment profile and claim boundary are unchanged.

The one fresh pull-never, networkless, disposable PostgreSQL 16 rehearsal
passed and completed exact-ID cleanup. It does not claim function or trigger
behavior and opens no application migration, runtime wiring, product data,
provider call, deployment, release, Pages or protected-ref authority.
