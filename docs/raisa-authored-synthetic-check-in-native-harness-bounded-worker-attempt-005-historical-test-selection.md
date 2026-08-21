# Attempt 005 historical test selection

## Purpose

This record freezes the exact applicability boundary used by the provider-free widened packet for `raisa-authored-synthetic-check-in-native-harness-bounded-worker-attempt-005`.

The packet retains every immutable predecessor test except these three selectors:

1. `tests/test_raisa_provider_free_authored_synthetic_native_harness_structured_diagnostic_bounded_worker_controller_convergence_rehearsal.py::test_deterministic_evidence_launches_no_subprocess`
2. `tests/test_raisa_provider_free_authored_synthetic_native_harness_structured_diagnostic_bounded_worker_controller_convergence_rehearsal.py::test_contract_evidence_and_report_are_current`
3. `tests/test_raisa_authored_synthetic_check_in_native_harness_bounded_worker_attempt_004.py::test_attempt_four_provider_free_check_reports_zero_processes_and_requests`

## Why these selectors are not current acceptance tests

The first two selectors assert the byte identity of a historical controller evidence publication. They remain valid for that immutable predecessor source but cannot establish the current descendant's controller identity.

The third selector deliberately requires the live operation latch to name attempt 004. The latch correctly names attempt 005, so applying this historical live-latch assertion to the current attempt must fail closed.

Attempt 005 supplies its own current-latch, provider-free zero-activity check. The widened packet passed after applying only these three exact deselections. No harness process, model turn or provider request was used by either packet run.

This selection changes no product, patient, clinical, runtime, deployment, protected-ref or prior-evidence surface.
