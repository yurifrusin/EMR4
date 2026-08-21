# Plugin-Tree Source Diagnosis Historical-Latch Test Selection

Date: 2026-08-21
Timestamp: 2026-08-21T13:21:16.5459490+10:00 (Australia/Brisbane)
Status: `frozen_exact_deselection`

The first widened focused run included
`test_attempt_four_provider_free_check_reports_zero_processes_and_requests`
from
`tests/test_raisa_authored_synthetic_check_in_native_harness_bounded_worker_attempt_004.py`.
That historical readiness test calls the attempt-004 provider-free checker,
which deliberately requires the live active-operation latch still to identify
the occupied attempt-004 operation. The repository has correctly advanced to
the source-diagnosis successor latch, so the test returned the expected
`active_operation_latch_mismatch`.

Passing that single test now would require rolling the live latch backwards or
weakening the historical check, neither of which this diagnosis authorises.
The exact test is therefore deselected from the successor's widened regression
run. Every other test in that module remains selected, together with the
attempt-004 postterminal, controller-convergence and structured-diagnostic
suites. The failure is procedure evidence about test selection only; it does
not change the immutable attempt-004 terminal or this tranche's source
diagnosis.
