# Provider-free durability behavior DML name-ambiguity recovery

Date: 2026-08-09

Status: bounded renderer recovery candidate; behavior runtime remains closed

Behavior attempt 028 stopped at `BTR-E02` with PostgreSQL `42702` in
`project_update_confirm_reschedule_v1` line 124, admitted zero of the frozen
twenty scenarios and removed its exact owned container with absence verified.
The immutable failure is
`provider-free-behavior-transaction-failure-evidence-028.json`.

No diagnostic PostgreSQL run was needed. Exact source mapping binds line 124
to outbox insert node `p19`. Its typed contract deliberately uses local values
named `aggregate_revision` and `source_contract_digest` for identically named
target columns, and returns those columns into the typed outbox row. The
renderer emitted both local references and DML `RETURNING` columns without a
qualifier, leaving PostgreSQL unable to distinguish PL/pgSQL variables from
relation columns.

The bounded repair labels each generated function's outer PL/pgSQL block
`cf_body`, renders every scalar `LOCAL` reference through that label, and
renders `INSERT` and `UPDATE` return projections through their exact target
relation. Symbols, types, values, predicates, returning populations, body
programs, scenarios and authority remain unchanged. Hostile tests must reject
removal of the label, unqualified local values, or unqualified DML returns.

Before another behavior attempt, the renderer and inert artifact must be
resealed, a fresh PostgreSQL parse/catalogue characterization and distinct exact
reproduction must pass, all six behavior parents must be rebound with the
twenty scenarios unchanged, the complete deterministic packet must pass, and a
fresh Gemini 3.6 Flash/high exact-HEAD veto must pass.

This recovery grants no migration, operational database, source,
watcher/listener/feed, patient/product data, provider, command, application/API/
Diary wiring, deployment, production, release, Pages or protected-ref
authority.
