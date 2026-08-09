# Disposable PostgreSQL parse/catalogue system-`xmin` record-access rebind

Date: 2026-08-09

Status: exact parse/catalogue reproduction passed; behavior remains closed

The parse/catalogue rehearsal is rebound to renderer-repair commit
`cd305e6b4dd160f8ebbc8b7487ec042b1278b9f2`, whose canonical inert SQL is
1,403,578 LF bytes at SHA-256
`sha256:42e7230a98447201400129ecba06fbc5e0cb4fddff2aab263133c21f5635f112`.
It contains exactly 412 statements.

Renderer 2.0.9 changes only anonymous-record `SYSTEM_XMIN` lowering from
`(record).xmin` to direct `record.xmin`. It retains all 62 explicit
`relation.xmin AS xmin` projections, binds 118 total `.xmin` tokens, and leaves
the typed body semantic and structural contracts unchanged.

Because PostgreSQL catalogue query digests are runtime evidence, the first
newly owned networkless container is characterization-only with an empty
expected-digest map. It may release only bounded catalogue digests, rollback
facts, artifact bindings and exact cleanup. A second newly owned container may
run only after those digests are mechanically rebound and must reproduce them
exactly before parse acceptance.

The characterization completed with file SHA-256
`sha256:ae39e8727abae894914839998f7e2d2a25a2720faa4952d3c7b69b7c822d9f45`.
It reproduced the entire predecessor digest set unchanged, matched the expected
rollback SQLSTATE with zero role/schema residue, and removed exact container
`ebfe9cac39aa53c89307d4ef2ed1cdae4878ec21f5da799a93d454f70503905a`
with absence verified. Those observed digests are now the complete frozen map
for the second newly owned exact run.

This rebind opens neither function/trigger behavior nor an applied migration.
It grants no application, API, Diary, product-data, provider, tool, command,
deployment, release, Pages or protected-ref authority.

The second newly owned exact run passed as
`raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_pass`.
Evidence file SHA-256 is
`sha256:27d7e4ac43bea613c44afea53d20881822e1e9bbfbaec3211bd3b9a442026006`;
it binds exact-mode contract SHA-256
`sha256:06d79bd73122f71548cf85d0ba68b48549d3cdfb42a5a8e69147844e337e39e4`,
the repaired artifact, all fifteen frozen catalogue digests, matched rollback
SQLSTATE `42601`, and exact cleanup. Exact container
`28d0699d81fa257d5421d322342961d523918d853022f0ae9b763951fea6b3ee`
was removed with absence verified.

The current regression packet deliberately excludes
`test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_continuity.py`.
That frozen predecessor-closeout module asserts historical Continuity revision
230, agent-error revision 81 and then-current next-step wording; the live
repository has correctly advanced to Continuity 233, agent-error revision 122
and the accepted behavior/transaction plan. Its four failures were reproduced
without changing the module or its historical artifacts. Current body
semantics, inert DDL, parse/catalogue and agent-error validity remain the
applicable descendant checks.
