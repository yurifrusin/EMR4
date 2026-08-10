# Disposable PostgreSQL parse/catalogue generation-lock RLS rebind

Date: 2026-08-10

Status: deterministic characterization candidate; no database run authorised
by this document.

The independently accepted source commit
`e115f6f4cb31df1131c5c67d24f3a475a2ca6127` regenerates the inert durability
artifact as 1,435,252 canonical LF bytes with SHA-256
`sha256:aa26f92671a18d927e423f9d7df80973a19a87f32d49d85cc3f3d55f6808e8e9`.
Its 421 statements and all object populations remain fixed. The only catalogue
delta expected is the existing `pol_cf_06_update` predicate admitting ordered
`COORDINATOR, LIFECYCLE` in USING and WITH CHECK.

The parse contract is deliberately rebound in `characterization_only` mode
with an empty expected digest map. It must first pass deterministic and fresh
independent exact-HEAD review. Only then may one newly owned networkless,
pull-never, tmpfs-only PostgreSQL 16 container characterize the complete
catalogue. The accepted mutable evidence and protected historical failure must
remain byte-exact; characterization has its own non-aliasing evidence path.

No applied migration, operational database, source watcher/listener/feed,
product/patient/clinical data, provider call, application/API/Diary command,
deployment, production, release, Pages or protected-ref authority is opened.
