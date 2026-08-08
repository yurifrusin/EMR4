# Sol acceptance: disposable PostgreSQL parse/catalogue rehearsal plan

Date: 2026-08-07

Accepted source HEAD: `c5f0960a240b7f162b1b34e1b09fb166d12fd42e`

Result: `raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan_pass`

## Acceptance

The corrected plan is accepted for bounded implementation. The first reviewer
pass at
`d202b310318496fb7a414d97916bbac54e6ec349` remains rejected because it missed
cluster-scoped roles and psql's `-c`/`-f` precondition for
`--single-transaction`. The next replacement pass at
`009395ac28eb7ac05017fe5fbd1ae1439ecf948d` also remains rejected for acceptance
because it reported only the aggregate 32 owned types/domains and missed the
plan's incorrect 4/17/11 subdivision.

The exact correction at
`c5f0960a240b7f162b1b34e1b09fb166d12fd42e` passed 89 focused/register/index
checks, acceptance-index integrity, Ruff and diff checks. A genuinely fresh
Gemini 3.6 Flash/high Antigravity veto mechanically reproduced all 388 ordered
nodes, every exact identifier and `4 DOMAIN / 19 ENUM / 9 COMPOSITE /
32 TYPE_OWNER`; it returned `pass` with no P0-P3 finding after 9/9 focused tests
and left its exact-HEAD worktree clean. Sol independently reproduced the same
kind counts and exact one-to-one 32-member type-owner set.

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

Implementation is now admitted only inside the closed plan. Docker preflight
remains ineligible until the closed contracts, harness and hostile/static tests
pass deterministic implementation admission. The later one-container runtime
cannot broaden the plan or its parse/catalogue-only claim.

The long descriptive replacement-review worktree failed locally before
dispatch because of Windows path length. Its destination is absent and
unregistered; the same commit passed clean preflight and review at `r41`.
