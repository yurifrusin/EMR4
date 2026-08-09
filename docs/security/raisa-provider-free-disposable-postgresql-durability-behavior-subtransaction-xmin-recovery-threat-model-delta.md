# Threat-model delta — durability behavior subtransaction xmin

Date: 2026-08-09

The observed `CF603` is a fail-closed availability defect in inert generated
PL/pgSQL. It released no partial durability membership, crossed no tenant
boundary and widened no command authority. The repair removes an unintended
write subtransaction so the accepted top-level transaction-provenance fence
can distinguish a coherent write set from foreign or earlier row versions.

Security invariants:

- every rendered `UPDATE` key must match exactly one primary-key or unique
  constraint before SQL can be emitted;
- update DML must remain outside PL/pgSQL exception subtransactions;
- zero affected rows still map to stable `CF004` and multi-row mutation remains
  structurally impossible;
- types, predicates, lock order, RLS, grants, failure identities and the outer
  transaction boundary remain unchanged; and
- all runtime, patient/product, provider, application, command, deployment,
  release, Pages and protected-ref surfaces remain closed.
