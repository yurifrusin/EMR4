# Disposable PostgreSQL parse/catalogue interval-construction rebind

Date: 2026-08-09

Status: exact PostgreSQL 16 parse/catalogue reproduction passed; behavior
runtime remains closed

The deterministic parent at exact source
`8c307d28323c68744338e2290879994e4980b2dd` is renderer 2.0.11's
412-statement artifact with 1,391,614 canonical LF bytes and SHA-256
`sha256:c113b2480106441043562412ee3135d2a79bd56c76bb5bc2705734d9e5f8cf51`
and render-manifest file SHA-256
`sha256:7a0c5d15e65a4631cf9b590f7c7af67f2103f69ebe05fb2dd9ad5f002e1d1b2d`.

The sole SQL-semantic correction replaces invalid numeric-times-interval
expressions with typed `pg_catalog.make_interval` construction in the
generated function bodies. The immutable structural and body contracts,
function and trigger populations, roles, policies, privileges, authored-
synthetic prerequisite shapes and statement population remain unchanged. The
prior accepted RLS lock-visibility exact pass is preserved byte-for-byte in
`provider-free-disposable-postgresql-evidence-rls-lock-visibility-pass.json`
at SHA-256
`sha256:e417fc377e6b8e9ff723e21e88b40e41b9cfb2424d2fd6122e404c54bf068611`.

Because PostgreSQL owns canonical function-body and catalogue rendering, the
fixed-path parse harness first binds this exact parent in
`characterization_only` mode. One newly owned `postgres:16-bookworm`
container may install the exact artifact under `--pull=never` and
`--network=none`, reproduce the fixed rollback and complete catalogue
population checks, emit only the closed query digests and then be removed by
exact verified ID. A characterization result cannot pass this gate.

Only after that container is absent may the contract bind the complete
observed digest set. A separate newly owned container must then reproduce the
exact digest-bound result and exact-ID cleanup. Neither attempt may reuse a
container, alter the inert parent or claim behavior of any stored function,
trigger or RLS policy.

This rebind proves parse, atomic installation, catalogue/privilege shape and
cleanup only. It opens no applied migration, operational database, product or
patient data, provider, application/API/Diary wiring, watcher/listener/feed,
command/write, deployment, production, release, Pages or protected-ref
authority.

## Characterization result

The separate characterization completed with the required nonpassing result
`catalogue_characterization_required`. Evidence SHA-256 is
`sha256:257daa83f9d45c9397a3666fa54ee906016fd3fa4924d58af2269f3316b65139`.
All seventeen catalogue query digests remained byte-identical to the preceding
accepted pass. Exact container
`6b0f34cb1bdd7faa3c6482bbe300e2ecb5f7ed9109890a90f18e846625ce7c8d`
was removed and exact-ID absence was verified. The complete digest set is now
eligible for one separate exact-bound rerun.

## Exact-bound result

The separate exact-bound run passed as
`raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_pass`.
Evidence SHA-256 is
`sha256:3bb1c5dd63f6b12566869a95abdd1beeaf7a317b045845d5ee4cdcef0eeee4d9`.
It reproduced the exact artifact, fixed rollback proof, complete catalogue
population, all seventeen frozen query digests and unchanged application-owner
and empty-prerequisite boundary. Exact container
`338fbb6a1a2294d5370879e226adf10ff83214523b7afc3a093bc74f701beb07`
was removed and exact-ID absence was independently re-observed.
