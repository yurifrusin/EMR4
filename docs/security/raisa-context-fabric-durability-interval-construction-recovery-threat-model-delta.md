# Threat-model delta: durability interval-construction recovery

Date: 2026-08-09

Status: bounded provider-free recovery control; behavior runtime remains closed

## Scope change

Behavior attempt 024 proved that the accepted inert renderer and the closed
authored-synthetic fixture shared one invalid PostgreSQL numeric-times-interval
expression. This recovery changes only those two deterministic construction
surfaces and the recognizer that rejects the invalid predecessor.

No database is contacted while the candidate is edited or tested. Later
parse/catalogue and behavior executions retain the accepted one-container,
`--pull=never`, `--network=none`, no-port, no-mount, tmpfs and exact-ID cleanup
profile.

## Threats and controls

| Threat | Control | Required evidence |
|---|---|---|
| A narrow fixture-only patch leaves invalid generated function bodies | Correct both typed renderer opcodes and the independent fixture builder | Fresh render contains no numeric-times-`make_interval`; fixture has the same absence |
| A renderer-only patch leaves BTR-E02 failing before entry-point invocation | Explicit fixture unit test plus next exact BTR-E02 behavior execution | Valid named `mins` construction in the closed payload |
| Broad raw-SQL repair changes body meaning | Immutable structural/body contract hashes and existing typed opcode population remain exact | Parent binding and full deterministic packet pass |
| Seconds silently use an unresolved overload | Explicit `pg_catalog.float8` cast into documented `secs double precision` argument | Static lowering assertion and fresh PostgreSQL installation |
| Minutes or seconds change units | Named `mins`/`secs` arguments; unchanged typed opcode and current operands | Exact generated fragments and unchanged body parents |
| Invalid expression re-enters through later edits | Independent recognizer rejects `* pg_catalog.make_interval(` and hostile mutation proves rejection | `numeric_times_interval` finding on resealed hostile SQL |
| Failure evidence is overwritten by the next attempt | Byte-identical immutable attempt-024 copy; mutable evidence stays unstaged until a pass replaces it | Exact SHA-256 equality and immutable-failure test |
| A fresh Windows worktree changes canonical SQL bytes to CRLF | Exact artifact path has `text eol=lf` and a Git-attribute/byte test | `git check-attr eol` returns `lf`; artifact contains no CRLF |
| Diagnostic leaks raw PostgreSQL text | Persist only fixed resolution booleans, missing identifier, raw digest and cleanup | Diagnosis receipt records `raw_error_persisted: false` |
| Recovery broadens authority | API Steward boundary remains internal durability evidence only | No API, app, migration, provider, product-data or protected-ref change |

## Residual risks

The selected behavior tranche still does not prove concurrent execution,
retention behavior, crash/unknown-commit recovery, applied migration,
operational credentials/storage, performance, watcher/listener/feed wiring or
product integration. Passing parse/catalogue evidence proves installation and
catalogue shape, not execution of every stored function branch. The frozen
twenty behavior scenarios remain the required next execution proof.
