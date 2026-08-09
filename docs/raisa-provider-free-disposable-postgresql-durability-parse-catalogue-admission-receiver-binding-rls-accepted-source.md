# Accepted source — admission-receiver binding-RLS parse/catalogue proof

Date: 2026-08-10

Accepted evidence source commit:
`f842c023f4db16e8b0ffc381f653fb16e98280cc`

Result:
`raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_pass`

The source commit contains the exact PostgreSQL 16 pass evidence at SHA-256
`sha256:bf842570457b09c78dd4e7685b618af535fea71d6f0093f27d1699c9876471c9`.
It binds the 421-statement, 1,419,573-LF-byte inert artifact SHA-256
`sha256:1d53c7ac1cd9a9fb19faafcca0ebcf8dacadf238f62df873d2d3fc78c657b407`,
render-manifest file SHA-256
`sha256:2042eb8055cc55cd7cb4396093a897b4df5f86c5a1910dbca677a241c2d7325b`
and exact parse contract SHA-256
`sha256:cf746ed8824ef8853677020e90083c2b4bfe1b4096a36ad7735cfeabf0eb4b91`.

All fifteen artifact-dependent catalogue query digests matched the separately
characterized set. Fourteen remain identical to the prior accepted source;
only `policies` changed, to
`sha256:5bd0a6629eaa4a734e01d786781ea62121e887581b38558b33677bd79c752a0f`,
representing the exact two-owner binding predicate with unchanged session and
active-time fences. No other role, relation, type, function, ACL, trigger,
constraint, RLS mode or privilege surface changed.

Exact-pass container
`2cbe41c2589b2abd175f4807d89efcc14e0321738790ce92365fe9af60099ad7`
and characterization container
`a1d64af025b200578f73cb020e357befc8176969534fd8a006eb3dfe137952e4`
were each removed and independently verified absent by exact ID. Mutable
accepted and preserved failure evidence paths were restored byte-for-byte.

This ledger is eligible to become the behavior contract's accepted-runtime-
source parent. It proves parse, fixed rollback, atomic installation,
catalogue/privilege shape and cleanup only. It does not prove function,
trigger, RLS or transaction behavior and opens no applied migration,
operational runtime, source/watcher/listener/feed, application wiring, product
or patient data, provider call, command/write, deployment, production,
release, Pages or protected-ref authority.
