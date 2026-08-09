# Accepted source — RLS lock-visibility parse/catalogue proof

Date: 2026-08-09

Accepted evidence source commit:
`a7a780f9735d3c41095703d464611752f89685d9`

Result:
`raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_pass`

The source commit contains the exact accepted PostgreSQL 16 pass evidence at
SHA-256
`sha256:e417fc377e6b8e9ff723e21e88b40e41b9cfb2424d2fd6122e404c54bf068611`.
It binds renderer 2.0.10's 412-statement, 1,391,506-LF-byte inert artifact
SHA-256
`sha256:28dc21611c937cfa9d6db5bb58d571b1a267af02377294b16cef029a7e1e4800`,
render-manifest file SHA-256
`sha256:8ced08cb218b4a19cb1abbf41930db3dcec0ac1e60fa132d38e9fba8c813c49e`
and exact parse contract SHA-256
`sha256:2834249d755d83764abf974d524424b958a261f6d8c94808403d4d8bf3a5a1f1`.
All fifteen exact catalogue digests matched; only the expected policy digest
differs from the predecessor. Terminal container
`3156fb7876f366dd36bbd52645706aa3d4158526e5e1bcfdaa72ff4c56c3c22f`
was removed and exact-ID absence was independently verified.

This ledger is the behavior contract's accepted-runtime-source parent. It
proves parse, fixed rollback, atomic installation, catalogue/privilege shape
and cleanup only. It does not prove function, trigger, RLS or transaction
behavior and opens no applied migration, operational runtime, product or
patient data, provider, tool, command, deployment, production, release, Pages
or protected-ref authority.
