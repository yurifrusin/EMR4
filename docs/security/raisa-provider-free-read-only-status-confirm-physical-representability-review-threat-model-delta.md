# Threat-model delta — status-confirm physical representability review

Date: 2026-08-12

Source HEAD: `3af1af85cc3e6ee646f856a1ce6f306495741894`

## Scope

This delta covers a provider-free, exact-file, read-only review of whether the
accepted status-confirm state version, private receipt and ordered lock
boundary can be physically represented. It selects no implementation.

## Threats and controls

| Threat | Deterministic control |
|---|---|
| Protected paths are enumerated during candidate discovery | AER-0292 discards the failed metadata output; all future commands name exact already-known non-protected files. |
| Review silently treats timestamps as monotonic state versions | Require an explicit positive monotonic identity tied to committed appointment state changes; timestamp substitution fails closed. |
| Public response leaks private session/audit correlation | Separate public response fields from private completed-receipt bindings. |
| Existing idempotency storage is overstated as the full receipt | Inventory every required private field and record additive gaps individually. |
| Receipt/conflict leaks before current checks | Require target validity and current authority before idempotency classification or disclosure. |
| ORM capability is mistaken for mounted behavior | Label capability only as representability; no route, transaction or database is executed. |
| Review chooses a migration or backfill | Freeze design selection outside this tranche and keep `implementation_not_admitted`. |
| Source scope expands by import or migration traversal | Stop, revise the plan with the exact path/hash, then rehydrate before opening it. |

## Residual risks

The review cannot prove a selected column/default/backfill, migration ordering,
ORM/service composition, PostgreSQL lock acquisition, transaction isolation,
concurrency, rollback, restart/unknown-commit behavior, mounted-route parity or
operational safety.

## Authority boundary

No application or migration edit/import, database, SQL, real lock, route,
provider, credential/browser action, product/patient data, watcher/event,
product command, deployment, production, release, Pages or protected ref is
opened. `docs/branding/` and all unrelated untracked paths remain excluded.
