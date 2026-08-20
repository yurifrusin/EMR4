# Provider-free pre-HMR startup terminal recovery report

Date: 2026-08-20

Timestamp: 2026-08-20T23:23:58.3235077+10:00 (Australia/Brisbane)

Result: `pass`

- Closed stages / causes: `2` / `11`
- Deterministic scenarios / rejected hostile mutations: `12` / `12`
- Immutable attempt artifacts checked: `17`
- Native processes / worker processes / provider requests: `0` / `0` / `0`
- Raw startup bytes persisted: `0`
- Controller ordering checks: `5/5`

The outer controller now hashes and classifies bounded local startup streams,
writes and validates one safe terminal outside the disposable root, then removes
the root and publishes only the sidecar digest in its ordinary terminal.

Efficacy: `promising_bounded_traceability_improvement`. This improves future pre-first-HMR attribution
without retaining raw output. It does not identify attempt 002's deleted stderr,
prove Harness reliability, measure DeepSeek, or authorize another occupied run.
