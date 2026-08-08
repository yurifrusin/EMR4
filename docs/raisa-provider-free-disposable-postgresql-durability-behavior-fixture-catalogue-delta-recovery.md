# Provider-free behavior rehearsal fixture/catalogue delta recovery

Date: 2026-08-08

Status: deterministic repair candidate; runtime closed pending fresh veto

The recovered-parent behavior attempt admitted and reconciled the exact SQL,
then failed closed before scenario execution. Its bounded mismatch digest
resolves exactly to `application_relations,relation_acl`.

The fixture intentionally grants the producer four application-table
privilege sets and inserts authored-synthetic application rows. Therefore:

- bootstrap may change exactly `relation_acl` and `application_relations`;
- after the twenty scenarios, only `application_relations` may differ from the
  post-bootstrap catalogue; and
- application-table row counts and contents remain governed by the stricter
  per-scenario snapshots, exact count deltas and row-set digests.

All type, relation, column, constraint, index, policy, function, trigger, role,
schema and privilege catalogue digests remain immutable after bootstrap. Any
additional changed query id fails closed. Failure attempt 008 proves zero
scenarios executed and exact owned-container cleanup.

This repair changes no SQL artifact, fixture, scenario, expected result,
authority, runtime containment or closed surface. Another runtime attempt
remains ineligible until deterministic tests and a fresh exact-HEAD independent
veto pass.
