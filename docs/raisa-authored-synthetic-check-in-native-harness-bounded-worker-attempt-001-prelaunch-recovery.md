# Authored-synthetic native Harness bounded worker — attempt 001 prelaunch recovery

Date: 2026-08-20  
Timestamp: 2026-08-20T21:48:30.3784177+10:00

## Immutable result

Attempt `deepseek-native-synthetic-window-worker-001` is consumed and cannot be
resumed. Its terminal is `failed_closed`. It started zero native Harness
processes, made zero model/provider requests, invoked zero tools and changed no
candidate bytes. No DeepSeek performance evidence was produced.

The terminal's visible coordinate is `attempt_root_cleanup_failed`. The exact
post-terminal recovery cleared read-only bits from three Git object files in the
disposable authored-synthetic repository and removed only the verified attempt
root. No owned process remained. The original terminal is immutable; the
separate cleanup-recovery receipt records final root absence.

## Initiating defect

Static comparison of the controller and broker established the prelaunch
handshake mismatch:

- the controller set `EMR4_BROKER_WORK_ORDER_SHA256` to SHA-256 over canonical
  JSON with a trailing newline;
- the broker verifies its parsed work order using the transactional clock's
  canonical-object digest without that newline; and
- existing tests exercised the broker with the correct object digest and the
  controller independently, but did not launch the real broker from the
  controller-produced environment.

The broker therefore rejected the work order before `broker-ready`; the
controller never launched Harness and never contacted DeepSeek. Cleanup then
masked that initiating coordinate in the immutable terminal.

## Recovery

The provider-free repair:

1. uses the clockwork's canonical-object SHA-256 directly in the controller;
2. launches the real broker from the controller-produced environment and
   requires the exact `broker-ready` contract in a provider-free regression;
3. clears Windows read-only bits through a tightly scoped `shutil.rmtree`
   callback and retains bounded cleanup attempts; and
4. preserves the initiating coordinate alongside any later cleanup failure
   instead of overwriting it.

Focused and neighbouring provider-free validation passes. This repair does not
authorise a second attempt. The frozen plan requires a distinct user-attention
decision before any new worker identity, checkpoint, native process or provider
request. No automatic retry or fallback exists.

## Boundaries retained

The repair changes no EMR4 product source, route, API/schema, feature flag,
ordinary-practice allowlist, `Arrived` status, action grammar, first-party
client, waiting-area behavior, product/patient/clinical data, database,
production runtime, deployment, release, Pages or protected ref.
