# Threat-model delta: durability admission-row-shape recovery

Date: 2026-08-10

Status: candidate parent-recovery control; runtime remains closed

## Changed surface

Only the typed body entry-program generator, its generated repository-local
artifacts and their deterministic tests change. The structural row-shape
constraint, principals, RLS, SQLSTATE registry, command authority and frozen
behavior scenario population remain unchanged.

## Threats and controls

| Threat | Control |
|---|---|
| PRIMARY and CONFLICT share an invalid superset of fields | Generate disjoint kind-specific projections and test every required and forbidden field against `ck_cf_04_02` |
| SQL `NULL = NULL` prevents a valid insert-or-reload winner match | Lower typed-null expected bindings only as `IS NULL`; reject ordinary equality to typed null anywhere in the program population |
| A narrow fix weakens the structural database guard | Keep `ck_cf_04_02` and its exact PRIMARY/CONFLICT requirements unchanged |
| Generated body and rendered DDL silently diverge | Regenerate the canonical body, schema, inert DDL, manifest and lowering contract from the repaired source and rerun all parent checks |
| Stale parse evidence authorises behavior against a changed body | Require a fresh single-use parse/catalogue rehearsal in a newly owned networkless disposable PostgreSQL 16 container |
| Scenario edits hide a behavioral regression | Preserve and prove the exact twenty-scenario objects, order and `6/4/3/4/3` category population SHA-256 |
| Changed runtime candidate proceeds without independent challenge | Require the full deterministic packet and one fresh exact-HEAD Gemini 3.6 Flash/high veto before the next behavior attempt |

## Residual boundary

This remains authored-synthetic, provider-free repository work followed only by
explicitly gated disposable rehearsals. Concurrency, crash recovery, retention,
key rotation under load, long-lived persistence, operational feeds/watchers,
product data and application wiring remain closed.
