# Historical test selection — proof-module relative-specifier repair

Date: 2026-08-21
Timestamp: 2026-08-21T13:48:11.7207157+10:00 (Australia/Brisbane)

The widened repair regression preserves three exact historical checks without
requiring them to pass against successor state:

1. `test_attempt_four_provider_free_check_reports_zero_processes_and_requests`
   requires the live latch still to be attempt 004. The latch has correctly
   advanced twice, so the successor deselects this assertion without changing
   the test.
2. `test_deterministic_evidence_launches_no_subprocess` and
   `test_contract_evidence_and_report_are_current` in the accepted controller-
   convergence rehearsal bind the pre-repair controller source hash. The exact
   two-row repair necessarily changes that component hash. Regenerating its
   accepted historical evidence or weakening the binding would violate the
   immutable-evidence boundary.

All other tests in those modules remain selected. The corrected widened run
passes 56 tests. These deselections prove neither a native boot nor current
controller-convergence acceptance; they preserve historical evidence while the
new repair's own contract, schema and behavioral projections carry the current
claim.

The first widened command also attempted to pass `--deselect` through
`scripts.ariadne_provider_free_pytest`, whose closed CLI accepts only test
paths. That invocation was rejected before collection. The corrected run uses
direct serial pytest, retains the repository lock and names every deselection
explicitly.
