# Authored-synthetic native Harness worker attempt 004 diagnosis

Date: 2026-08-21

Timestamp: 2026-08-21T12:45:22.5790561+10:00 (Australia/Brisbane)

## Exact terminal

Attempt `deepseek-native-synthetic-window-worker-004` is consumed and cannot be
retried, resumed or reclassified. Exactly one native Harness process started
and exited `1` after 11,150 ms. The outer coordinate is
`native_harness_terminal_failure` at exact terminal source
`26c95db309c2bfb12e640b6fd504b7399f87d73d`.

The converged pre-HMR controller produced the validated v2 terminal
`structured_entrypoint_import_rejected`. It places the failure after native
process creation and before the first HMR event, with controller coordinate
`native_process_exited_nonzero`. Its sanitized diagnostic records phase
`entrypoint_import_rejected` and four cause nodes. The top node is an `error`
with message coordinate `plugin_tree_failed_to_load`; two intermediate error
nodes have no admitted message or code coordinate; the deepest error node has
code coordinate `unrecognized`. The chain is neither cyclic nor truncated.

The process emitted zero stdout bytes and 7,314 stderr bytes. The stderr
SHA-256 is
`0db1536f1e7cca299d0fb2f96fb7c8d2fefce34aa01e706bd28499b6571db934`.
Raw messages, stacks, paths and streams are not retained.

The broker recorded zero started, completed, failed or rejected provider
requests. The runner produced no request, model step, tool call or tool result.
The synthetic source remained at its exact baseline with no changed path.
Retry, fallback and auxiliary-model counts are zero. Harness, broker and the
literal disposable root are absent after cleanup.

## What became more traceable

Attempt 003 could prove only an unclassified nonzero exit before HMR. Attempt
004 safely identifies the failing launcher phase, the plugin-tree-load message
coordinate, the finite cause-chain shape and the existence of one deeper code
outside the current closed vocabulary. The equal 7,314-byte stderr lengths do
not imply equal content: the attempt-003 and attempt-004 digests differ.

This is a material traceability improvement. It is not a startup repair and it
is not DeepSeek performance evidence. The closed diagnostic intentionally does
not retain the raw code or message, so it cannot yet identify which pinned
rc.7 plugin-tree branch rejected the profile.

## Honest conclusion

The native Harness remains unsuitable for EMR4 worker work under this exact
profile because it still fails before any DeepSeek request. The controller and
broker regime did, however, behave as intended: one consumed launch, zero
provider spend, zero retry, a digest-bound structured terminal and complete
cleanup.

The next narrow tranche is provider-free and read-only. It should inspect the
pinned rc.7 plugin-tree construction and error-wrapping source against this
immutable cause-chain shape, map the deepest unrecognized code only if source
evidence supports a closed coordinate, and authorise no Harness process,
provider request or occupied retry.
