# Disposable PostgreSQL behavior rehearsal system-`xmin` explicit-alias rebind

Date: 2026-08-09

Status: deterministic candidate; occupied behavior remains closed

Attempt 020 stopped safely at `BTR-E01` with SQLSTATE `42703`, zero admitted
scenarios and exact cleanup. Diagnosis 020a proved that the `record` local had
received the system value but not a stable field named `xmin`. Renderer 2.0.8
now emits `relation.xmin AS xmin` at all 62 accepted exact-read sites.

The regenerated inert source is commit
`1e5e9840dcbf14d2c1766a63149417f6912dc915`; its accepted parse/catalogue
evidence source is `1057b0d6e49384f8b7ab00bd501dcc868fba909b`.
This behavior rebind changes only the accepted parse ledger, inert SQL,
manifest and unchanged prerequisite source rows. The typed body and structural
parents remain unchanged.

All exactly twenty ordered behavior scenarios, their SQL and expected outcomes
remain byte-for-byte unchanged, as does category coverage `6/4/3/4/3`.
The deterministic packet and a fresh exact-HEAD Gemini 3.6 Flash/high veto must
pass before one new occupied attempt is eligible. Attempts 001-020 and their
immutable evidence remain preserved; `docs/branding/` remains excluded.

This descendant grants no applied migration, provider, application/API/Diary
or operational runtime, patient/product/protected data, live watcher, tool or
command authority, deployment, production, release, Pages or protected-ref
movement.
