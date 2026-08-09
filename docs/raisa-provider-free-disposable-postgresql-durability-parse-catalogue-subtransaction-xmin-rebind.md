# Durability parse/catalogue subtransaction-xmin rebind

Date: 2026-08-10

Status: exact reproduction passed; accepted-source binding remains required

The disposable PostgreSQL parse/catalogue rehearsal is rebound to renderer
2.0.15 source commit `561f5c896c16f31dcf6057da37d6ece7134c0da6` and its
regenerated 413-statement inert artifact with 1,416,483 canonical LF bytes at
SHA-256
`sha256:03150dfec61944df8f26ca2473200afa49e88ddcf9d9fce950320a2a98bd96e0`.
The render manifest is SHA-256
`sha256:bb91292d98fb34f576fa7bf6b5a196eccdcd42f087624b70b450933e36638597`.

The repair changes only typed UPDATE lowering: each declared update key is
proved against exactly one primary or unique constraint, the UPDATE executes
in the function's top-level transaction rather than an exception
subtransaction, and an immediate `FOUND` guard preserves the stable CF004
zero-row result. The typed body-program population, statement count, phases,
catalogue assertions and behavior scenarios remain unchanged.

The deliberately non-accepting characterization produced all seventeen
predecessor catalogue digests unchanged, including all fifteen
artifact-dependent digests, in attempt `25b98f1da5c8de4d06188a70`. Exact owned
container `8e351be5609f7d01eb18919321eb42ff02736ef64c68c8affa422356ed1eb9d9`
was removed and exact-ID absence was separately verified. Immutable evidence
is
`provider-free-disposable-postgresql-evidence-subtransaction-xmin-characterization.json`
at SHA-256
`4d140704d33624e90737022e5f9d095559152bd56554514ccebc73222d845750`.
The predecessor mutable parse evidence was restored byte-for-byte at SHA-256
`3bf66870cf80edc507b191d6022a5e3d22f3b7f3073c9ae4e696fed2fc54155c`.

The contract is now rebound to those fifteen exact digests at canonical
SHA-256
`3dc318e64b9c30817c0e2cdca650fc284ae3d2f35e93e697d0cac5368fecbd03`.
This characterization cannot accept itself. Distinct exact reproduction
attempt `4ec417dfc5e16ad6e462e66d` matched all seventeen catalogue digests and
completed the required lifecycle. Its separately owned container
`f784718297efd8d11250a2a34bbf7a25627036d2fcb9c745fb6c56e954f6e517`
was removed and exact-ID absence was verified. Immutable exact-pass evidence
is
`provider-free-disposable-postgresql-evidence-subtransaction-xmin-exact-pass.json`
at SHA-256
`cb439eefe9eb243eb4eccda144ac51218d9e26ba71c0dd14402ee066b7c1fb14`.
The generic accepted evidence path was restored byte-for-byte at SHA-256
`97d1385c6b617890cb0f155122e30eb283d49e42af1d44db385a2b9f4a9c2bec`.

The pass proves exact PostgreSQL 16 parse, atomic installation and catalogue
shape for this artifact. A separate accepted-source ledger must bind the
committed exact-pass source before the behavior contract can inherit it.

This rebind opens no behavior proof, application migration, operational
database, source, watcher/listener/feed, patient/product/protected data,
provider/model call, command/write authority, application/API/Diary wiring,
deployment, production, release, Pages or protected-ref authority. It does not
permit listing or touching any unrelated container. `docs/branding/`, mutable
behavior evidence, mutable parse evidence and all unrelated untracked files
remain preserved and unstaged.
