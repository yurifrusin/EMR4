# Disposable PostgreSQL behavior rehearsal system-`xmin` parent rebind

Date: 2026-08-08

Status: deterministic candidate; occupied behavior remains closed

Attempt 019 stopped safely before any scenario when PostgreSQL proved that a
named table-composite local does not contain the system `xmin` column. The
typed body contract now requires an explicit `xmin` projection into a `record`
local before every `SYSTEM_XMIN` consumption. The corrected body source is
commit `73322f3d86d44f997c054331e06c3017831b345f`; the regenerated inert artifact
source is `3949a61d60e2a704635b922755670f071569d4f3`.

The parse/catalogue proof at accepted evidence source commit
`bfb20a43a30c8f46a65f2383a127a4257e2473c6` passed with exact catalogue
digests, intentional rollback and exact-ID cleanup. This rebind changes only
the six canonical parent bindings. All exactly twenty ordered behavior
scenarios, their SQL and expected outcomes remain byte-for-byte unchanged, as
does category coverage `6/4/3/4/3`.

The deterministic packet and a fresh exact-HEAD Gemini 3.6 Flash/high veto must
pass before one new occupied attempt is eligible. Attempts 001-019 and their
immutable evidence remain preserved. `docs/branding/` and every unrelated
untracked file remain excluded through explicit-path staging only.

This descendant grants no applied migration, provider, application, API,
Diary or operational runtime, patient, product or protected data, live watcher,
tool or command authority, deployment, production, release, Pages or
protected-ref movement.
