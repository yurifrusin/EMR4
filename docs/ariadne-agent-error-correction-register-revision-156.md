# Ariadne agent error and correction register revision 156

Date: 2026-08-10

Status: corrected; database gate pending

Revision 156 adds AER-0182 and brings the register to 182 bounded incidents
with zero open incidents.

## AER-0182 — exact review-set format drift

Ruff's semantic check passed all 34 exact review files, but its format gate
named four deterministic formatting drifts: the attempt-031 diagnosis script,
the behavior-plan test, the inert-DDL test and the migration-architecture plan
test. No semantic lint, runtime, database or provider failure occurred.

Ruff formatted only those four paths. Because candidate bytes changed, the
exact lint, format and complete 552-test packet must all pass again before an
independent veto is eligible.
