# Provider-free durability behavior subtransaction-xmin recovery

Date: 2026-08-09

Status: bounded renderer recovery candidate; behavior runtime remains closed

Behavior attempt 029 stopped safely at `BTR-E02` with PostgreSQL `CF603`,
completed zero of the frozen twenty scenarios and removed its exact owned
container with absence verified. The immutable failure is
`provider-free-behavior-transaction-failure-evidence-029.json`.

No diagnostic PostgreSQL run was needed. Exact source mapping proves that the
renderer wrapped the stream-head `UPDATE ... RETURNING` in a PL/pgSQL block
with an `EXCEPTION` clause. PostgreSQL documents that such a block forms a
subtransaction, that a writing subtransaction receives a subxid, that a row's
`xmin` records the transaction which created that row version, and that
`pg_current_xact_id()` returns the top-level xid even inside a subtransaction.
The deferred temporal fence consequently compared the stream-head row's subxid
with the top-level xid and rejected the otherwise coherent transaction.

The bounded repair emits every typed `UPDATE` directly, outside an exception
subtransaction. Before rendering it proves that the node's exact key columns
match one primary-key or unique constraint. A zero-row result still maps to
stable `CF004` through `FOUND`; the uniqueness proof makes a multiple-row
result structurally impossible. Typed programs, predicates, locks, returned
rows, scenarios and authority remain unchanged.

Before another behavior attempt, the renderer and inert artifact must be
resealed, fresh PostgreSQL parse/catalogue characterization and distinct exact
reproduction must pass, all behavior parents must be rebound with the twenty
scenarios unchanged, the complete deterministic packet must pass, and a fresh
Gemini 3.6 Flash/high exact-HEAD veto must pass.

This recovery grants no migration, operational database, source,
watcher/listener/feed, patient/product data, provider, command, application/API/
Diary wiring, deployment, production, release, Pages or protected-ref
authority.
