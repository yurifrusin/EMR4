# Durability parse/catalogue DML name-ambiguity rebind

Date: 2026-08-09

Status: exact parse/catalogue reproduction passed; behavior remains closed

The disposable PostgreSQL parse/catalogue rehearsal now binds renderer 2.0.14
source commit `9513b1f8a845b29473a2ca402fcee2ac2b11eebe` and its regenerated
413-statement inert artifact with 1,427,373 canonical LF bytes at SHA-256
`sha256:b2e476995848b64d819ae6c545d5b8c9b93707288993a0120d09d19c503230dc`.

The structural/body contracts and all catalogue populations are unchanged.
Only generated PL/pgSQL namespace spelling changed: scalar locals are block
qualified and DML return projections are target qualified. The current
catalogue characterization used a deliberately non-accepting contract. It
produced all seventeen predecessor catalogue digests unchanged, including the
fifteen artifact-bound digests, in attempt
`1dcabd0341a3770703633468`. Exact owned container
`a90453f42aa6c3fe2afd8dd2403f9f85bc60803d087ea2c0849116754897f339`
was removed and exact-ID absence was separately verified. Immutable evidence
is
`provider-free-disposable-postgresql-evidence-dml-name-ambiguity-characterization.json`
at SHA-256
`3bf66870cf80edc507b191d6022a5e3d22f3b7f3073c9ae4e696fed2fc54155c`.

The contract was rebound to those fifteen exact artifact-dependent digests
at canonical SHA-256
`f696bc57c3bbe6e25fc6f817aff337ef85b199bffff66fbf33ffa327c982e673`.
The characterization did not accept itself. Distinct attempt
`26f530dab9ed13ba20500267` then reproduced all seventeen catalogue digests
exactly, passed the fixed rollback and atomic-installation checks and returned
`raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_pass`.
Its immutable evidence is
`provider-free-disposable-postgresql-evidence-dml-name-ambiguity-exact-pass.json`
at SHA-256
`122d2db7ec577875c1477eee6a4fa0c51dc9117ce0c23bc3704aa43f4c791ca0`.
Exact owned container
`a26898ce851b1eab61039023466c2e9802227ae4b223faaa0d1cc48c58e0db76`
was removed and exact-ID absence was separately verified. The parse prerequisite
may now be ledger-bound and used to rebind the frozen behavior contract.

This rebind opens no behavior proof, application migration, operational
database, source, watcher/listener/feed, patient/product data, provider,
command, application/API/Diary wiring, deployment, production, release, Pages
or protected-ref authority.
