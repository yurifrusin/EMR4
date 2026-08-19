# DeepSeek native Harness provider-free stock-headless-to-custom-runner HMR boot proof closeout

Date: 2026-08-20

Timestamp: 2026-08-20T02:33:29.0250603+10:00 (Australia/Brisbane)

Status: **accepted for clockwork publication at Continuity 339 / Compass 321**

## Outcome

The pinned `@deepseek-ai/dsh@0.1.0-rc.7` native Harness now has an attributable
provider-free startup proof. Its package-declared `lib/bin.js` ran through the
documented stock `--profile headless` surface with Node `--expose-internals`.
The initial composition disabled the stock model runner, code runtime and
telemetry. An in-process sentinel observed the real rc.7 HMR service only after
both stock user-patch registrations were present. The controller then changed
the watched profile patch atomically, HMR mounted the local custom runner, and
that runner requested exit 0.

The exact event sequence was `sentinel_activated`,
`stock_headless_hmr_ready`, `custom_runner_reached`,
`app_exit_requested`. The native process exited 0 in 10,597 ms with empty
stdout/stderr, zero network/model/broker/provider/session counts and complete
process/root cleanup.

## Exact sources and retained evidence

- Planning source: `f5a00279f428698b5ce789d022404335a54a7d95`
- Frozen deterministic candidate:
  `86af0a015c38a0be04b9c3dc5197612f2e390d20`
- Corrected source-preflight candidate:
  `f8dd18396814bb117f1c4b3d9b33d66647bebb25`
- Passing native-evidence candidate:
  `c2c4d33654b77a50ca86e79471841568bf7bcbcf`
- Independently reviewed exact candidate:
  `5c3325e9213afc5690453812e2078c61135c8a38`
- Gemini review binding source:
  `aae26552938c218b0b833f5e79b2d0eb07fd894e`
- Package SHA-1: `8a69013c06179d7af437de92fb4a9a2e1fd7d410`
- Package SHA-256:
  `2f8f0b763d611ac536f7a9411ee43c0afc067c1b8732c3102c04dbe398bcacc5`
- Protected local/origin `master` and `handoff/current`:
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`

The canonical evidence is
`orchestration/continuity/deepseek-native-harness-provider-free-stock-headless-to-custom-runner-hmr-boot-proof/provider-free-native-harness-hmr-boot-evidence.json`.
It retains only bounded facts and digests. Raw environment, logs, disposable
paths, npm cache, prompt or response data are absent.

## Preserved prelaunch rejection

The first controller invocation failed before native launch because its static
source predicate expected a quoted `headless` marker while the exact minified
CLI expresses the documented command in help text. The failure evidence is
retained separately with native boot count zero, no lifecycle/provider/network
activity and complete cleanup. The predicate was narrowed to the exact
documented text, tested against a synthetic exact package tree, and read back
against the real installed rc.7 source before native attempt 001.

This was a construction-gate correction, not a retry of a consumed native
terminal. Native attempt 001 ran exactly once.

## Verification and independent veto

- The focused Harness/broker/profile/no-database selection passed 39 tests.
- Ruff, Python compilation, contract validation and Git whitespace checks
  passed.
- The generated sentinel/runner executed the exact four-event lifecycle
  against a local mock HMR registry before the native attempt.
- No `dsh-hmr-proof-*` root or owned process remained after execution.
- The source-inspection directory was moved recoverably to the Windows Recycle
  Bin after exact-path verification.
- Gemini 3.7 Flash/high passed a fresh isolated read-only veto at exact
  candidate `5c3325e9213afc5690453812e2078c61135c8a38`.
- All ten verifier commands returned zero, 39/39 tests passed, the worktree
  stayed clean and no P0-P2 finding was reported.
- The review worktree and review branch are absent.

## Parallelism closeout

- DeepSeek was not invoked as a model worker or reviewer. Its native Harness
  was the provider-free system under test; Claude Code was not used as a
  fallback.
- Gemini owned one fresh exact-candidate independent veto and passed it.
- Native subagents were not used under current developer policy and because
  process launch, readiness, mutation, terminal capture and cleanup required
  one serial owner.

## What this proves and does not prove

This proves the pinned local rc.7 stock-headless/HMR startup path and gives a
traceable readiness/terminal/cleanup envelope for later separately frozen
work. It does not prove DeepSeek model quality, provider reliability, coding
completion, future Harness versions, production isolation or a general VM
network boundary. It does not itself authorise a model call, occupied worker,
attempt-004, product/runtime/data change, ordinary-practice activation,
deployment, Pages or protected-ref movement.

## Next operation

Proceed under Yuri's standing authority to
`raisa-provider-free-check-in-relay-free-recovery-attempt-004`. First freeze a
fresh exact plan and preexecution envelope for exactly one provider-free
disposable PostgreSQL recovery run. Attempts 001-003 and their terminal/cleanup
evidence remain immutable. The accepted call-site/pre-registry cleanup repair,
no-database admission interlock and this native-Harness startup proof must all
remain exact. Plan freezing opens no Docker object, database execution or
DeepSeek model call; any such execution requires its own full preexecution
admission, one-run latch and collision-free output namespace.
