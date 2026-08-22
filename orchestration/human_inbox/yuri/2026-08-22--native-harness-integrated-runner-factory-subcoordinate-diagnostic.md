# Native Harness integrated-runner factory diagnostic

Date: 2026-08-22

Timestamp: 2026-08-22T19:05:50.6495370+10:00 (Australia/Brisbane)

## Lay summary

We found a very plausible exact reason for the previous Harness failure: the
runner and the safety guard were using different versions of the same
connection, one with four plugs and one with three. That would make the guard
reject immediately before DeepSeek was contacted.

The local test intended to prove this dynamically then exposed one of the
workflow costs you were worried about. I selected the package folder one level
too high, so the test could not import its two scoped DeepSeek packages and
stopped before reaching the factory. The clockwork contained it cleanly—one
local process, no retry, no provider cost, no raw error retained—but this was
still avoidable circular work rather than the intended proof.

The next step is deliberately tiny: correct that one folder projection, prove
both import files exist before starting anything, and run one separately named
provider-free test. No new taxonomy or Harness attempt is justified.

## Technical summary

- Source diagnosis: occupied runner call arity 4 versus materialised guard
  parameter arity 3; predicted coordinate
  `EFFECTIVE_TOOL_COMPOSITION_INPUT_INVALID`.
- Consumed fixture: Node exit 1, stdout 0 bytes, stderr 1,327 bytes; raw streams
  not retained.
- Deterministic fixture diagnosis: selected `node_modules`; required
  `node_modules/@deepseek-ai`; two selected targets absent and two corrected
  targets present.
- Factory/setup entered: no.
- Native Harness / broker / worker / model / provider requests: all zero.
- Retry / resume / fallback: all zero.
- Cleanup: process and disposable root absent.
- Verification: 39 relevant tests pass after task-branch origin alignment;
  Ruff, compilation, schemas and whitespace pass.

## Deliberately closed

No occupied retry, native Harness process, model/provider request, product or
patient data, ordinary-practice change, production runtime, deployment,
release, Pages or protected-ref movement. Existing untracked files, especially
`docs/branding/`, remain preserved.

## Next tranche and attention

Next:
`deepseek-native-harness-provider-free-integrated-runner-factory-fixture-import-path-recovery`.

Yuri's attention is not required. The successor is an exact mechanical recovery
inside the standing authority and must stop after one separately identified
provider-free process if the typed coordinate is not reproduced.
