# DeepSeek native Harness provider-free pre-HMR startup terminal recovery closeout

Date: 2026-08-20

Timestamp: 2026-08-20T23:49:08.9636913+10:00 (Australia/Brisbane)

Status: `accepted_provider_disabled_recovery`

Reviewed candidate:
`12c289e28490fcef50f95d50a299e186b4b78847`

## Outcome

Future native-Harness failures before the first HMR event now have a bounded
safe terminal instead of only `native_harness_terminal_failure` plus stream
digests. The controller incrementally hashes local stdout/stderr, retains at
most 64 KiB from each only in memory, selects one of two stages and eleven
closed causes, writes the sanitized sidecar exclusively outside the disposable
root, validates its readback, then removes the raw streams with that root. Its
ordinary terminal carries only the sidecar digest.

Zero matches remain `unclassified_nonzero_exit`; multiple cause groups remain
`ambiguous_startup_signatures`; over-limit streams cannot receive a semantic
text classification. Raw lines, paths, exception messages, environment values,
prompts, reasoning and credentials are absent from the durable schema.

## Evidence and verification

- 12 deterministic semantic scenarios and 12 hostile mutations pass.
- Every fixed signature, mixed case, ambiguity, unclassified text, binary and
  secret-shaped bytes, both stream-size boundaries, stale/escaped/disposable
  paths, simulated symlink paths and exact terminal relationships are covered.
- All five required controller-ordering assertions pass.
- Forty-nine provider-disabled focused tests pass; subprocess entry points are
  monkeypatched to reject invocation.
- The evidence builder/checker, Ruff and Python compilation pass.
- Seventeen retained attempt-001/002 artifacts are byte-identical to their
  frozen hashes.
- No native Harness, worker or provider request was used by the accepted
  validation path.

One earlier broad development-test selection accidentally included the legacy
local broker-ready regression. It started and terminated one provider-free
test broker without a request; exact readback immediately afterwards found
zero matching broker processes and the disposable attempt root absent. The
boundary breach, eight other rejected technical drafts and one successor-latch
vocabulary omission are preserved in register revision 577, AER-0716 through
AER-0725. The first blocked generation was rolled back byte-exactly before
corrected republication.

## Acceptance boundary

This recovery proves bounded future pre-first-HMR attribution and cleanup
ordering. It does not recover the deleted attempt-002 stderr, identify that
attempt's exact cause, make the Harness reliable, measure DeepSeek performance,
or authorize another occupied worker.

No product source or configuration, API/OpenAPI/GraphQL, database/schema,
route/adapter, feature flag, allowlist, action grammar, first-party client,
ordinary-practice posture, generic-status `Arrived`, waiting-area behavior,
product/patient/clinical data, production runtime, deployment, release, Pages
or protected ref changed. Local/origin `master` and `handoff/current` remain
exact `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

## Next gate

The mechanism is ready to support a more informative occupied rehearsal, but
the active plan explicitly leaves any new occupied native worker as a distinct
Yuri decision. Until that decision, no Harness, broker, worker or provider
process may launch.
