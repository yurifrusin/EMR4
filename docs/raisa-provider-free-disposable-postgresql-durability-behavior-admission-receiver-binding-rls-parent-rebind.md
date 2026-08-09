# Durability behavior admission-receiver binding-RLS parent rebind

Date: 2026-08-10

Status: deterministic six-parent rebind; behavior runtime remains closed

The frozen behavior rehearsal now binds the accepted admission-receiver
binding-RLS parse/catalogue ledger at evidence source
`f842c023f4db16e8b0ffc381f653fb16e98280cc`, the renderer 2.0.17 inert SQL
artifact and render manifest at source
`30ff6b01a54c339e3045977cda909628841fe57e`, the repaired structural
contract at source `a1a4a619222297b36fa6894a5cf5f12a179af48c`, the rebound body contract
at source `c0673fc755457756719959dcfc6aea04531d6627`, and the unchanged
authored-synthetic prerequisite contract at evidence source
`f842c023f4db16e8b0ffc381f653fb16e98280cc`.

The exact accepted-source ledger SHA-256 is
`19d45f59222b1bab0120f4c00d79f7845eec701703d0eaa181e0bfa1f1f26d8f`,
the inert artifact SHA-256 is
`1d53c7ac1cd9a9fb19faafcca0ebcf8dacadf238f62df873d2d3fc78c657b407`,
and the render-manifest file SHA-256 is
`2042eb8055cc55cd7cb4396093a897b4df5f86c5a1910dbca677a241c2d7325b`.
The canonical behavior contract SHA-256 is
`678252f6e5bca28118e041880c675e25ca4a51be999ccddd5c121d91d01c477a`.

All twenty frozen scenarios and category counts remain unchanged at
`6/4/3/4/3`; their canonical population SHA-256 remains
`eec93b0d67bd70a9640b3000bc63d43a08aa6817b438e0c99dbf2595a69c4c19`.
No scenario, fixture identity, SQL action, expected outcome, SQLSTATE,
readback, forbidden effect, Docker boundary or cleanup rule changed. The only
runtime-relevant repair is the already parse-proved extension of
`pol_cf_17_select` to the exact non-login admission receiver while retaining
the database-login equality and both active-time fences. Forced RLS remains,
and no new role, grant or `BYPASSRLS` authority is introduced.

This rebind makes the complete deterministic packet and one fresh exact-HEAD
Gemini 3.6 Flash/high veto eligible. It does not authorize another PostgreSQL
behavior run by itself and opens no applied migration, operational database,
source access, watcher/listener/feed, application/API/Diary wiring, product or
patient data, provider/model call, command/write, deployment, production,
release, Pages or protected-ref surface. `docs/branding/`, mutable behavior
and parse evidence, and all unrelated untracked files stay excluded.
