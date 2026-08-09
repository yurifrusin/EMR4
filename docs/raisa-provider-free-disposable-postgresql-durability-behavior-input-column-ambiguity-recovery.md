# Provider-free durability behavior input-column ambiguity recovery

Date: 2026-08-10

Status: bounded renderer recovery candidate; behavior runtime remains closed

Behavior attempt 032 stopped at `BTR-E03` with PostgreSQL `42702` in
`admit_proofread_observation_v1` line 35, observed zero of the frozen twenty
scenarios and removed its exact owned container with absence verified. The
immutable failure is
`provider-free-behavior-transaction-failure-evidence-032.json`.

No diagnostic PostgreSQL run was needed. Exact source mapping proves that the
first three `SELECT_SET` nodes compare a fully qualified relation column named
`source_position` with an unqualified function input carrying the same name.
The collision occurs in the primary-admission, conflict-admission and
classified-receipt predicates. PostgreSQL correctly refused to infer which
namespace the bare identifier represented.

The bounded repair gives every body-program input a deterministic `cf_arg_`
physical prefix in its generated program-function signature and all `INPUT`
references. Logical input names, types, expressions, body programs, support
function, PostgreSQL identities, RLS, scenarios and authority remain
unchanged. The new lowering is generic so a future body-program input cannot
silently collide with a same-named relation column.

Before another behavior attempt, the renderer and inert artifact must be
resealed, a fresh PostgreSQL parse/catalogue characterization and distinct exact
reproduction must pass, all six behavior parents must be rebound with the
twenty scenarios unchanged, the complete deterministic packet must pass, and a
fresh Gemini 3.6 Flash/high exact-HEAD veto must pass.

This recovery grants no migration, operational database, source,
watcher/listener/feed, patient/product data, provider, command, application/API/
Diary wiring, deployment, production, release, Pages or protected-ref
authority.
