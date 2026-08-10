# Threat-model delta: Context Fabric generation-lock RLS recovery

Date: 2026-08-10

## Changed surface

`pol_cf_06_update` now admits an already practice- and source-bound
`COORDINATOR` session in addition to `LIFECYCLE`. This aligns forced-RLS row
visibility with the existing `apply_durability_transition_v1` execute grant and
its typed generation-state updates.

## Preserved controls

- `context_coordinator` retains no direct table SELECT or DML privilege.
- No new role, login, entry point, function owner or `BYPASSRLS` capability is
  introduced.
- Session binding still proves login, logical capability, practice, source and
  validity time for both the old and new row image.
- The entry point remains security-definer, typed, exact-cardinality,
  transaction-bound and fail closed.
- Generation one-way lifecycle invariants and trigger enforcement are
  unchanged.
- No application command path, source truth, product data, patient data,
  provider, runtime wiring or deployment is opened.

## Abuse analysis

A coordinator login cannot exploit the policy for direct mutation because it
has no table privilege. Inside the definer function, it can affect only rows
selected by the existing exact generation locator and only through the existing
typed transition branches. Cross-practice, cross-source and expired bindings
remain denied by `session_binding_allows_v1`.

## Required verification

Deterministic tests must reject removal of `COORDINATOR` from either UPDATE
predicate, retain zero coordinator direct relation grants, reproduce the inert
artifact, re-prove the PostgreSQL catalogue in a disposable owned container and
then rerun the unchanged 20-scenario behavior contract only after a fresh
exact-HEAD independent veto.
