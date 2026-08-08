# Inert DDL registration-RLS rebind

Date: 2026-08-08

Status: deterministic corrected artifact; PostgreSQL behavior runtime closed

Renderer 2.0.7 binds structural source
`9fb107ab598fba418b42be6d233c4960a6f29840`, body source
`6ae8f2c7bf3df1fe9f89b760e9d3641384848545`, structural contract
`sha256:d481b991fa2d6835babe8372722d00775b31432802bdf9ec40e007369b0d34c6`
and body contract
`sha256:422b7cd5203893ecd2269c9b2dbf4018ed359661d5ebe962de55afffb03c340c`.

The regenerated inert PostgreSQL artifact has exactly 412 statements and
1,402,659 canonical LF bytes with SHA-256
`sha256:34d321adce220a94473e3cd74173f7b0ffc37441b2e4dd24699ca18b86c7e760`.
The render-manifest file SHA-256 is
`sha256:4ac9b851796f6460fd55844d4d3634eba62f4302bd68ce80b62b63f69cd541ea`.

Only the six corrected lifecycle `SELECT`/`INSERT` policy predicates, exact
parent bindings and renderer version change. Function and trigger bodies,
relation/column shapes, grants, update policies, statement population and
frozen behavior scenarios remain unchanged. The renderer test packet now
binds lifecycle access to the required initial stream-head, frame and watermark
effects and proves that the corresponding update policies remain closed.

The next dependency is a fresh exact PostgreSQL 16 parse/catalogue rehearsal
for this artifact, followed by behavior-contract rebinding and independent
review. This artifact is still inert and opens no migration, operational
database, product or patient data, provider call, command/write, deployment,
production, release, Pages or protected-ref authority.
