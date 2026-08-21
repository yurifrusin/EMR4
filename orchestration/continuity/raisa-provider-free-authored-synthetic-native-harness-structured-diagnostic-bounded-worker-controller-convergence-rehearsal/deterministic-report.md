# Provider-free bounded-worker controller convergence report

Date: 2026-08-21

Result: **pass**

- Claim: `provider_free_descendant_controller_adapter_converged`
- Valid exact-identity selection: `ariadne.native_harness_pre_hmr_startup_terminal.v2`
- Missing-sidecar fallback / reason: `ariadne.native_harness_pre_hmr_startup_terminal.v1` / `structured_diagnostic_absent`
- Invalid fixture coordinates: `structured_diagnostic_invalid`
- Consumed immutable artifacts: `7`
- Disposable fixture root absent: `true`
- Harness / broker / worker / model / provider activity: `0 / 0 / 0 / 0 / 0`

This proves provider-free controller composition only. A separately authorised
fresh occupied attempt is still required to exercise the adapter against the
native runtime.
