# Disposable PostgreSQL parse/catalogue admission-row-shape rebind

Date: 2026-08-10

Status: non-accepting characterization candidate; no database run completed

The independently accepted parent recovery at source commit
`c8ab760220bc40863a18feaa3fc13a3d6ba04ba6` regenerates the inert durability
artifact as 1,435,142 canonical LF bytes with SHA-256
`sha256:ca22e47e847409f1ae8a81f62dd7f5f8402a43176d9015211f657204460fbdbb`.
Its 421-statement, six-phase, schema-object, role, privilege and RLS populations
remain fixed. Only function bodies change: PRIMARY and CONFLICT admission rows
now have disjoint constraint-correct field shapes, and typed-null
insert-or-reload winner bindings lower to `IS NULL`.

The parse contract is deliberately rebound first in `characterization_only`
mode with canonical SHA-256
`sha256:ce85174653dfbadc0f15124dd9f26a8ab83ba68c4192ced21569fdcb3efe0efc`.
Its expected catalogue digest map is empty, so a run cannot accept itself. One
freshly gated networkless, pull-never, tmpfs-only disposable PostgreSQL 16 run
may record the fixed catalogue values and must return
`catalogue_characterization_required`. A separate exact-digest contract and a
distinct fresh container must reproduce those values before the parse parent
can pass.

Historical characterization tests bind their own immutable accepted evidence
rather than borrowing the current contract's intentionally empty expectation
map. No applied migration, operational database, source/watcher/listener/feed,
product/patient/clinical data, provider call, application/API/Diary command,
deployment, production, release, Pages or protected-ref authority is opened.
