# Threat-model delta: system-`xmin` explicit projection alias

Date: 2026-08-09

Status: bounded renderer recovery candidate

## New observed failure

An exact `SELECT` can carry PostgreSQL system `xmin` into a PL/pgSQL `record`
without establishing a field name that a later `(record).xmin` expression can
resolve. Merely changing the local from a named table composite to `record`
does not prove the record-field contract.

## Security properties

- Every renderer-owned `SELECT_EXACT` or `LOCK_EXACT` projection of system
  `xmin` must emit an explicit `AS xmin` output name.
- Every local consumer remains subject to the typed body's
  `xmin_not_selected` definitely-assigned projection proof.
- The accepted artifact must contain no unaliased `.xmin INTO STRICT` and must
  contain the exact complete alias population.
- No user-column projection, predicate, relation, role, policy, trigger,
  privilege, scenario or expected outcome may change through this lowering.
- PostgreSQL parse/catalogue proof and the frozen behavior gate remain distinct;
  parse success cannot substitute for live record-field behavior.

## Retained containment

The work remains local, provider-free, unmounted, authored-synthetic and
default-off. Patient/product/protected data, operational sources and
credentials, application or migration runtime, providers, live watchers,
deployment, release, Pages and protected refs remain outside authority.
