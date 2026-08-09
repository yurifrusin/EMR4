# Durability behavior subtransaction-xmin parent rebind

Date: 2026-08-10

Status: deterministic six-parent rebind; behavior runtime remains closed

The frozen behavior rehearsal now binds the accepted subtransaction-xmin
parse/catalogue ledger at evidence source
`426fd229a96b7a34787dd0d0610a926808fd9961`, the renderer 2.0.15 inert SQL
artifact and render manifest at source
`561f5c896c16f31dcf6057da37d6ece7134c0da6`, the unchanged structural and
body contracts at source `958f8178c872854ab0f8e1c56dbb9fe46afbea22`,
and the unchanged authored-synthetic prerequisite contract at evidence source
`426fd229a96b7a34787dd0d0610a926808fd9961`.

The exact accepted-source ledger SHA-256 is
`8273baa138a8302677ca76244bccdf6b4be511aa41400c12c0e7b625cce0e972`,
the inert artifact SHA-256 is
`03150dfec61944df8f26ca2473200afa49e88ddcf9d9fce950320a2a98bd96e0`,
the render-manifest file SHA-256 is
`bb91292d98fb34f576fa7bf6b5a196eccdcd42f087624b70b450933e36638597`,
and the canonical behavior contract SHA-256 is
`a7278f6d87a69e9c5c9daef0a5b3640bcd22d27a3aac597ee228584dcc06d740`.

All twenty frozen scenarios and category counts remain unchanged at
`6/4/3/4/3`; their canonical population SHA-256 remains
`eec93b0d67bd70a9640b3000bc63d43a08aa6817b438e0c99dbf2595a69c4c19`.
No scenario, fixture identity, SQL action, expected outcome, SQLSTATE,
readback, forbidden effect, Docker boundary or cleanup rule changed. The only
runtime-relevant artifact change is the already parse-proved renderer 2.0.15
typed UPDATE lowering that keeps UPDATE-authored row versions in the
top-level transaction while preserving the stable CF004 zero-row guard.

This rebind makes the complete deterministic packet and one fresh exact-HEAD
Gemini 3.6 Flash/high veto eligible. It does not authorize another PostgreSQL
behavior run by itself and opens no applied migration, operational database,
source access, watcher/listener/feed, application/API/Diary wiring, product or
patient data, provider/model call, command/write, deployment, production,
release, Pages or protected-ref surface. `docs/branding/`, mutable behavior
and parse evidence, and all unrelated untracked files stay excluded.
