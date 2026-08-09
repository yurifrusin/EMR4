# Threat-model delta — durability behavior DML name ambiguity

Date: 2026-08-09

The observed `42702` is a fail-closed availability defect in inert generated
PL/pgSQL, not evidence of tenant crossover, data release or command-authority
widening. Ambiguous local/column names could otherwise make a future renderer
change depend on PostgreSQL's variable-conflict setting, so the repair makes
the intended namespace explicit in emitted SQL.

Security invariants:

- one fixed outer block label qualifies scalar locals;
- DML return projections are qualified by the exact target relation;
- no `#variable_conflict` override or search-path reliance is permitted;
- typed values, predicates, lock order, RLS, grants, failure identities and
  transaction boundaries remain unchanged; and
- all runtime, patient/product, provider, application, command, deployment,
  release, Pages and protected-ref surfaces remain closed.
