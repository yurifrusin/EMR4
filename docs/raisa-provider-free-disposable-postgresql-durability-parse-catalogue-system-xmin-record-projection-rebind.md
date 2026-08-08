# Disposable PostgreSQL parse/catalogue system-`xmin` record-projection rebind

Date: 2026-08-08

Status: exact catalogue reproduction passed; behavior remains closed

The exact parse/catalogue rehearsal is rebound to source commit
`3949a61d60e2a704635b922755670f071569d4f3`, whose canonical inert SQL is
1,403,184 LF bytes with SHA-256
`sha256:0379b35fe34eb5cc7f78a45d55a54b3b429e5f85af591e1c5bdf4080e3a15c7c`.
It contains exactly 412 statements.

The repaired function bodies explicitly project PostgreSQL's system `xmin`
column into `record` locals before any typed `SYSTEM_XMIN` consumption. The
structural contract remains exactly
`sha256:9fb1073a437c291f0953db89f4e1a6851d1977df581a149f3692a49b2fb45ad8`;
relations, policies, triggers, roles and privilege ceilings are unchanged.

The bounded characterization reproduced the complete prior digest set and
returned only `catalogue_characterization_required`; its exact container was
removed with absence verified. A second newly owned networkless container then
reproduced all exact catalogue digests, the intentional rollback SQLSTATE and
atomic installation, and again completed exact-ID cleanup. The accepted pass
evidence SHA-256 is
`sha256:b3eab7e0e79a87493750b5b825d452f826d37377e4a7cf5b747a563f6ec57718`.

This rebind opens neither behavior nor an applied migration. It grants no
application, API, Diary, product-data, provider, tool, command, deployment,
release, Pages or protected-ref authority.
