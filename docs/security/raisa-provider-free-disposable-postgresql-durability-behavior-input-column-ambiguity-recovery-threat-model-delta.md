# Threat-model delta — durability behavior input-column ambiguity

Date: 2026-08-10

The observed `42702` is a fail-closed availability defect in inert generated
PL/pgSQL, not evidence of tenant crossover, data release or command-authority
widening. Bare input names that collide with relation columns could otherwise
make future behavior depend on PostgreSQL's variable-conflict setting, so the
repair assigns body-program inputs a separate physical namespace.

Security invariants:

- every body-program input has one deterministic `cf_arg_` physical spelling;
- every `INPUT` reference uses that same physical parameter;
- the SQL support function keeps its accepted parameter names and behavior;
- no `#variable_conflict` override or search-path reliance is permitted;
- typed expressions, body contracts, RLS, grants, scenarios, failure
  identities and transaction boundaries remain unchanged; and
- all runtime, patient/product, provider, application, command, deployment,
  release, Pages and protected-ref surfaces remain closed.
