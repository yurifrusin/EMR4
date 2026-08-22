# Historical test selection: stock-headless-to-custom-runner boot proof

Date: 2026-08-22

Timestamp: 2026-08-22T20:45:11.0000000+10:00 (Australia/Brisbane)

Status: active exact-node selection

Operation: `deepseek-native-harness-provider-free-stock-headless-to-custom-runner-boot-proof`

The inherited file
`tests/test_deepseek_native_harness_provider_free_edit_coordinate_integrated_runner_stock_headless_boot_rehearsal_plan.py`
remains in the deterministic gate except for exactly:

`test_active_latch_is_the_exact_in_progress_operation`

That node freezes the predecessor operation ID as the live in-progress latch.
The predecessor is accepted and the governance clockwork has validly advanced
the latch to this successor, so replaying that equality is expected to fail and
would incorrectly require two operations to own the one active latch.

This selection changes no predecessor evidence, acceptance result or source.
All other predecessor plan, implementation, evidence, package, HMR, containment
and cleanup assertions remain selected. The successor's own focused test and
the generic active-operation latch tests validate the current exact operation.
