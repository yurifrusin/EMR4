# DeepSeek native Harness sentinel source escape repair historical test selection

Date: 2026-08-21
Timestamp: 2026-08-21T15:48:00+10:00 (Australia/Brisbane)

## Purpose

The source-only repair intentionally changes the SHA-256 of `scripts/raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal.py` and runs under a successor active-operation latch. Historical tests that require either the consumed pre-repair controller digest or the consumed attempt-004 latch must not be rewritten or regenerated to make the new state appear historical.

The complete pre-repair diagnosis packet passed 8/8 immediately before the one-byte edit. The initial post-repair surrounding packet produced exactly these three expected historical-state failures:

- `tests/test_deepseek_native_harness_provider_free_repaired_sentinel_native_boot_proof.py::test_deterministic_check_never_launches_native_process` — frozen boot-proof lineage requires the consumed pre-repair controller digest.
- `tests/test_deepseek_native_harness_provider_free_repaired_sentinel_native_boot_proof.py::test_direct_script_check_bootstraps_repository_imports` — the same frozen lineage check returns `component_digest_mismatch:repaired_profile_controller` by design.
- `tests/test_raisa_authored_synthetic_check_in_native_harness_bounded_worker_attempt_004.py::test_attempt_four_provider_free_check_reports_zero_processes_and_requests` — the consumed attempt-004 controller requires its historical active-operation latch, while the live latch correctly names the source-escape repair.

These three selectors are excluded from the post-repair surrounding packet. Their committed historical artifacts and assertions remain unchanged. All other tests in the selected files must pass. This selection grants no Node, Harness, broker, worker, model, provider or network activity and makes no boot-success claim.

The separate selector `tests/test_raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal.py::test_controller_environment_and_real_broker_reach_bound_ready` is also excluded because it starts a real Node broker fixture. Its 22 static neighbours pass; executing it would violate this tranche's zero-Node boundary.
