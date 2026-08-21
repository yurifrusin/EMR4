# Authored-synthetic native Harness worker attempt 005 diagnosis

Date: 2026-08-21

Timestamp: 2026-08-21T19:35:59.5541506+10:00 (Australia/Brisbane)

## Exact terminal

Attempt `deepseek-native-synthetic-window-worker-005` is consumed and cannot be
retried or resumed. Exactly one native Harness process started and exited `1`
after 10,929 ms. The exact terminal source is
`0b2aebd104f4c9dcfd4603af5dd51a687bace555`.

Unlike attempt 004, the process passed both retained HMR coordinates:
`sentinel_activated` and `stock_headless_hmr_ready`. The custom runner also
wrote its closed terminal. It then caught an exception before any model request
and recorded `CUSTOM_RUNNER_FAILURE`, request count `0`, no tool calls, no tool
results, no completed turn and no conclusion marker.

The broker recorded zero started, completed, failed or rejected provider
requests. The synthetic file remained at its baseline digest with no changed
path. Retry, fallback and auxiliary-model counts are zero. Both raw Harness
streams and broker stderr were empty. Harness, broker and the literal
disposable root are absent after cleanup.

## What became more traceable

The result rules out the attempt-004 pre-HMR plugin-tree failure: native
startup, sentinel activation, stock headless HMR readiness and custom-runner
activation all occurred. The remaining failure is inside the runner's
pre-request sequence, which includes service acquisition, exact preset-root
roster admission, agent creation and setup, the initial idle boundary and the
first follow-up boundary.

The runner's catch intentionally discarded the exception and retained one
generic code. Therefore the evidence cannot honestly select which of those
sub-stages failed. This is a real localization improvement over attempt 004,
but it is not yet the stage-level traceability expected from the harness gear.

## Honest conclusion

The native Harness remains unsuitable for EMR4 worker work: it has still never
reached DeepSeek in these bounded occupied attempts. Attempt 005 nevertheless
shows that the preceding source repairs moved execution past the full pre-HMR
startup barrier and into the custom runner. The control plane again behaved
correctly: one consumed launch, zero provider spend, zero retry, immutable
bounded evidence and complete cleanup.

The correct next tranche is provider-free. It should map the exact runner
pre-request operations to a closed stage vocabulary and produce a sanitized,
schema-admitted post-HMR diagnostic sidecar. No new native process or provider
request is justified until that diagnostic gear is independently validated.
