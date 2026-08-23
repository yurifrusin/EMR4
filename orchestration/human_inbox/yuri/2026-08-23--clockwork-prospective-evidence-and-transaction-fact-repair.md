# Clockwork prospective evidence and transaction-fact repair

Date: 2026-08-23

Timestamp: 2026-08-23T16:46:31.8267653+10:00 (Australia/Brisbane)

Yuri attention required: **no**

## Lay summary

The clock now reads the whole relevant form before it moves and tells us every
detectable problem together. It also reads its own attempt, lease, generation,
publication and rollback state, so these facts no longer depend on memory or
manual counting.

The three rollback shapes from the preceding closeout are now handled at the
clock face: two timestamp omissions are prepublication errors and the
publication count is machine output. No new form field, approval, gate or
document was added.

## Technical summary

Exact implementation source
`86dc6652d154eaa6adc9ca97e7fa2b7e66d7323c` changes four existing governance
implementation/test files. One hostile fixture returns ten errors in one
reading; a two-file build fixture proves four errors with zero canonical,
metadata or pointer mutation. Five CLI dispositions emit command-local typed
transaction facts. The current-Baton test shares the production timestamp
validator. Ruff, byte compilation and all 108 governance tests pass.

The first test run exposed six historical replay-fixture compatibility defects,
which were corrected in test-only paths while preserving the graph's canonical
acceptance rule. One diagnostic command used an unsupported node-selector shape
with the whole-file provider-free runner; direct serial diagnosis and the
canonical full suite passed. No product or provider work reran.

The next tranche will test a typed semantic closeout builder and command
registry inside the existing tick, targeting the remaining free-form command,
label, path and repeated-header burden. Harness/provider use, product and
check-in choices, patient/clinical data, runtime, deployment, Pages and
protected refs remain closed.
