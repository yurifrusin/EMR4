# Disposable PostgreSQL parse/catalogue system-`xmin` explicit-alias rebind

Date: 2026-08-09

Status: exact catalogue reproduction passed; behavior remains closed

The exact parse/catalogue rehearsal is rebound to renderer-repair commit
`1e5e9840dcbf14d2c1766a63149417f6912dc915`, whose canonical inert SQL is
1,403,680 LF bytes with SHA-256
`sha256:45c90b927a6e5a9b5b367ddf6ca76dfde0491ddb04d74214383cbca68419b7f6`.
It contains exactly 412 statements.

Renderer 2.0.8 explicitly aliases all 62 selected system-column expressions as
`xmin` while leaving every user-column projection, predicate, role, policy,
trigger and privilege ceiling unchanged. The typed body semantic contract and
structural contract remain unchanged.

The bounded characterization reproduced the complete frozen digest set and
returned only `catalogue_characterization_required`; its exact container was
removed with absence verified. A second newly owned networkless container then
reproduced all 17 exact catalogue digests, the intentional rollback SQLSTATE
and atomic installation, and again completed exact-ID cleanup. The accepted
pass evidence SHA-256 is
`sha256:67ef8251ed08ed8f17bf86e44c8f4f6ad1e74fad51eeca553adb2b641e0d8915`.

This rebind opens neither behavior nor an applied migration. It grants no
application, API, Diary, product-data, provider, tool, command, deployment,
release, Pages or protected-ref authority.
