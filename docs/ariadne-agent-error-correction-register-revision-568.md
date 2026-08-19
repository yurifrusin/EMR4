# Ariadne agent-error and correction register — revision 568

Date: 2026-08-20

Timestamp: 2026-08-20T00:36:00+10:00 (Australia/Brisbane)

## Revision scope

Revision 568 preserves AER-0658. Before the manifest defect recorded by
AER-0657 was exposed, Sol had already included the conftest-dependent A5.1
runtime suite in an initial standard-pytest verification set. That acquired the
repository's shared PostgreSQL test schema, contrary to this repair tranche's
no-database boundary. The candidate remained unchanged, no Docker or provider
call occurred and no product, patient or clinical data was used, but the
tranche-wide zero-database-execution claim was false and is withdrawn.

The accepted verification evidence is now only the corrected 146-test
provider-free `--noconftest` matrix. The accidental database-backed run remains
disclosed as process evidence and cannot contribute acceptance. The register
contains 658 incidents, all corrected or contained and none open.

## Prevention

Every no-database test selection now requires fixture-graph classification and
collection through the provider-free runner before execution. Standard pytest
is inadmissible unless the frozen plan expressly permits its conftest side
effects.
