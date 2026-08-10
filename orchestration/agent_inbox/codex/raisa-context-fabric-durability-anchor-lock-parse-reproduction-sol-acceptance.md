# Sol acceptance — anchor-lock parse exact reproduction

Date: 2026-08-08

Decision: `accepted_as_behavior_rebind_parse_parent`

Immutable reproduction evidence
`provider-free-disposable-postgresql-evidence-anchor-lock-rls-exact-reproduction.json`
is accepted at SHA-256
`28be342cec5fb011a128027e090ebf206be9af034e82596fa69c8cef4fd2d0c0`.
Attempt `dec52bbdd6905cf0748d1967` reproduced every complete catalogue digest
and object population under exact contract canonical SHA-256
`ce968baca442a3a9c3a3b0a6a13e635115378ec91434bd29baaf58dce07786f3`.
Exact container `ae450ec99726230c87549a49229eb121da936b09e555f4c741da2fd0f2f00203`
was removed and independently absent.

The immutable evidence was preserved at runtime source HEAD
`0dd603bc5508bb99f827365399f830b152ed165e`. The fresh characterization and
exact reproduction together show that only the intended recovery-anchor
lock-only RLS policy changed: policy count is 46 and all other catalogue
digests and kind counts remain unchanged from the preceding generation.

Sol separately reverified that primary mutable parse evidence was restored to
SHA-256 `97d1385c6b617890cb0f155122e30eb283d49e42af1d44db385a2b9f4a9c2bec`,
historical failure remains
`3bf66870cf80edc507b191d6022a5e3d22f3b7f3073c9ae4e696fed2fc54155c`,
generic characterization remains
`78c157c72243036d395c3bcff30f778fa8b1032bb98eec9a32b37110efbcf536`,
and mutable behavior evidence remains
`09907bf6569944f51fe0c13ba2b07f118e9f151173a19c188837e4e2a0deb12b`.

This acceptance permits only a deterministic behavior-contract rebind to this
immutable parse evidence, current inert SQL and manifest, structural and body
parents, followed by focused hostile tests and one fresh exact-HEAD review
before another behavior attempt.

It grants no behavior run by itself, applied migration, operational database
or credentials, watcher/listener/feed, patient/product/clinical data,
application/API/Diary command or write, deployment, production, release,
Pages or protected-ref movement.
