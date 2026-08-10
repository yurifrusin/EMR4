# Disposable PostgreSQL parse/catalogue admission-row-shape rebind

Date: 2026-08-10

Status: non-accepting characterization passed; exact reproduction candidate

The independently accepted parent recovery at source commit
`c8ab7602e16e24453dbf909597b4f702a2388416` regenerates the inert durability
artifact as 1,435,142 canonical LF bytes with SHA-256
`sha256:ca22e47e847409f1ae8a81f62dd7f5f8402a43176d9015211f657204460fbdbb`.
Its 421-statement, six-phase, schema-object, role, privilege and RLS populations
remain fixed. Only function bodies change: PRIMARY and CONFLICT admission rows
now have disjoint constraint-correct field shapes, and typed-null
insert-or-reload winner bindings lower to `IS NULL`.

The parse contract was deliberately rebound first in `characterization_only`
mode with canonical SHA-256
`sha256:a34fb46701396f9626a11f94024e233637e381f15e50d10bbec3cba6f1c4a0fa`.
Attempt `2fb9bbacbd4cd172aec49c51` ran once in freshly gated, networkless,
pull-never, tmpfs-only disposable PostgreSQL 16 container
`6515210c07830a7d6df037d12887ecf05961b5c34323e378a3186a9a2f4cd600`.
It returned the required non-pass `catalogue_characterization_required`, and
exact-ID cleanup plus independent absence inspection passed. Its immutable
evidence is
`provider-free-disposable-postgresql-evidence-admission-row-shape-characterization.json`
with SHA-256
`sha256:fc2268693334c03d6aed78efca8f58d1ba654c1cd0f32709a1ef2d24fd1a5c63`.

The current exact-digest contract has canonical SHA-256
`sha256:b81be9b783ba102a663fd3244ee4d1a81c4a2320745aa6f6eac537821b6e1e79`.
It binds the characterization's 15 value-bearing catalogue query digests;
server-version and extension observations remain fixed parent gates rather than
digest-map members. A distinct fresh container must reproduce the exact map
before the parse parent can pass.

The characterization revealed an evidence-routing defect: every non-pass
result previously targeted the immutable historical exact-rerun failure slot.
The characterization was preserved first, the protected failure was restored
byte-exact at SHA-256
`sha256:3bf66870cf80edc507b191d6022a5e3d22f3b7f3073c9ae4e696fed2fc54155c`,
and the accepted mutable evidence remained SHA-256
`sha256:97d1385c6b617890cb0f155122e30eb283d49e42af1d44db385a2b9f4a9c2bec`.
The harness now routes pass, characterization-required and other failure
results to three distinct targets. No second database run occurred before this
repair and exact-digest rebind.

Historical characterization tests bind their own immutable accepted evidence
rather than borrowing the current contract's intentionally empty expectation
map. No applied migration, operational database, source/watcher/listener/feed,
product/patient/clinical data, provider call, application/API/Diary command,
deployment, production, release, Pages or protected-ref authority is opened.
