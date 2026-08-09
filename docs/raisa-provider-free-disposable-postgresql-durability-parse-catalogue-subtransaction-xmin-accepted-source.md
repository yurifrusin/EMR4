# Accepted source — subtransaction-xmin parse/catalogue proof

Date: 2026-08-10

Accepted evidence source commit:
`426fd229a96b7a34787dd0d0610a926808fd9961`

Result:
`raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_pass`

The source commit contains the exact accepted PostgreSQL 16 pass evidence at
SHA-256
`sha256:cb439eefe9eb243eb4eccda144ac51218d9e26ba71c0dd14402ee066b7c1fb14`.
It binds the 413-statement, 1,416,483-LF-byte inert artifact SHA-256
`sha256:03150dfec61944df8f26ca2473200afa49e88ddcf9d9fce950320a2a98bd96e0`,
render-manifest file SHA-256
`sha256:bb91292d98fb34f576fa7bf6b5a196eccdcd42f087624b70b450933e36638597`
and exact parse contract SHA-256
`sha256:3dc318e64b9c30817c0e2cdca650fc284ae3d2f35e93e697d0cac5368fecbd03`.

All fifteen artifact-dependent catalogue query digests matched the separately
characterized set and the preceding accepted renderer 2.0.14 set. No catalogue
digest changed because renderer 2.0.15 changes only PL/pgSQL typed UPDATE
lowering inside function bodies. Exact-pass container
`f784718297efd8d11250a2a34bbf7a25627036d2fcb9c745fb6c56e954f6e517`
and preceding characterization container
`8e351be5609f7d01eb18919321eb42ff02736ef64c68c8affa422356ed1eb9d9`
were each removed and independently verified absent by exact ID.

This ledger is eligible to become the behavior contract's accepted-runtime-
source parent. It proves parse, fixed rollback, atomic installation,
catalogue/privilege shape and cleanup only. It does not prove function,
trigger, RLS or transaction behavior and opens no applied migration,
operational runtime, source access, watcher/listener/feed, application/API/
Diary wiring, product or patient data, provider/model call, command/write,
deployment, production, release, Pages or protected ref.
