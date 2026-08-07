# Sol acceptance: disposable PostgreSQL parse/catalogue rehearsal plan

Date: 2026-08-07

Accepted source HEAD: `009395ac28eb7ac05017fe5fbd1ae1439ecf948d`

Result: `raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan_pass`

## Acceptance

The recovered plan is accepted for implementation. The first reviewer pass at
`d202b310318496fb7a414d97916bbac54e6ec349` remains rejected because it missed
cluster-scoped roles and psql's `-c`/`-f` precondition for
`--single-transaction`. The exact corrected commit passed 9/9 focused tests,
Ruff and diff checks. A genuinely fresh Gemini 3.6 Flash/high Antigravity veto
at the unchanged clean exact HEAD returned `pass` with no P0-P3 finding.

The accepted order is rollback database first, proof of database-local fabric
absence plus cluster-wide role absence, then success database. Every artifact
stream is exact `--file=-`, `ON_ERROR_STOP=1`, `--single-transaction`. The
container must be already-local-image, no-pull, network-none, no-port,
no-mount, tmpfs-backed, exactly owned and exactly removed.

## Boundary

Implementation may create only the closed contracts, fixed-path standard-
library harness, static/hostile tests and, after deterministic admission, one
owned disposable local PostgreSQL 16 rehearsal and bounded evidence. It may not
open behavior execution, application migration/runtime/source/data/provider-
product, operational credential/persistence, deployment, Pages or protected
refs.

The long descriptive replacement-review worktree failed locally before
dispatch because of Windows path length. Its destination is absent and
unregistered; the same commit passed clean preflight and review at `r41`.
