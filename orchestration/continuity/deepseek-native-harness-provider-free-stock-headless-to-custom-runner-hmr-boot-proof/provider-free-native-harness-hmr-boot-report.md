# Provider-free native Harness HMR boot report

Status: `pass`

Exact package: `@deepseek-ai/dsh@0.1.0-rc.7`

Native attempt: `native-attempt-001`

The package-declared `lib/bin.js` launcher ran with Node
`--expose-internals --profile headless`. The initial profile layer disabled
`headless-runner`, `code-runtime` and `session-telemetry-otel`. Its sentinel
recorded the active rc.7 HMR service only after the exact profile and home patch
paths both appeared in the HMR config registry. The controller then atomically
replaced the watched profile patch; the HMR-refreshed composition inserted the
local custom runner, which recorded the terminal and requested exit 0.

The exact retained event order is:

1. `sentinel_activated`
2. `stock_headless_hmr_ready`
3. `custom_runner_reached`
4. `app_exit_requested`

The native boot completed in 10,597 ms with exit 0, empty stdout/stderr, zero
network/model/broker/provider/session counts, process absence and disposable-
root absence. Exact package, source, patch, plugin and guard digests are in
`provider-free-native-harness-hmr-boot-evidence.json`.

One earlier controller invocation rejected before native launch because its
documented-headless source predicate required a quoted marker that the exact
minified rc.7 CLI expresses as help text. The preserved
`prelaunch-source-predicate-rejection.json` records zero native boot processes,
zero lifecycle/provider/network activity and complete cleanup. The corrected
predicate was covered by a synthetic exact-tree test and read back against the
real rc.7 source before native attempt 001.

This proves the pinned local Harness startup/HMR path only. It admits no model
call, occupied worker, development edit, attempt-004, product/runtime/data,
deployment or protected-ref movement.
