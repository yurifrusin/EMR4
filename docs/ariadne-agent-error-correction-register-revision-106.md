# Ariadne agent error and correction register revision 106

Date: 2026-08-08

Status: accepted register correction

Revision 106 adds AER-0128 and AER-0129 and brings the register to 129 bounded
incidents.

## AER-0128 - verifier named a nonexistent evidence path

The otherwise passing recovered-parent review named a nonexistent handover-
ledger path instead of the actual reviewed parent-rebind document. The path
claim is preserved but rejected and cannot enter continuity or parent binding.

## AER-0129 - catalogue guard conflated application rows with structure

Behavior attempt 008 installed and reconciled the recovered artifact, then
failed before scenario execution because the fixture catalogue guard expected
only privileges to change. The unique bounded changed set also included
`application_relations`, whose row counts necessarily change when the fixture
inserts authored-synthetic application rows.

The repaired guard admits exactly that data-bearing projection alongside the
fixture privilege projection, then permits only the application-row projection
to differ after behavior. Per-scenario snapshots continue enforcing exact row
count deltas and row-set digests. Another run remains closed pending tests and
a fresh exact-HEAD veto.
