# Threat-model delta — inert-task sentinel-readiness native boot proof

Date: 2026-08-21
Timestamp: 2026-08-21T17:30:02.4063086+10:00 (Australia/Brisbane)
Status: `frozen`

## New executable surface

One fresh disposable local rc7 Node/native-Harness process receives one fixed
inert authored-synthetic task while loading only the source-repaired sentinel
through the unchanged initial headless profile.

## Threats and controls

- Task ambiguity or command injection: the contract admits one exact static
  argument without whitespace or metacharacters; deterministic admission checks
  the complete six-element argv before process creation.
- Accidental worker activation: the headless runner stays disabled, with zero
  runner rows/files, broker tokens or changed-profile writes.
- Provider/network access: credential and proxy names are scrubbed and the
  accepted preload guard denies and records network primitives; any record fails
  closed.
- Reuse of a consumed attempt: operation, attempt ID, outputs and disposable
  prefix are fresh; exclusive creation consumes before `Popen`.
- Hidden retry: one inspected `Popen`, no retry loop and one immutable consumed
  record bind the sole process lease.
- Raw-output leakage: only byte counts and SHA-256 digests survive exact-root
  cleanup; messages, stacks, paths, environment and raw streams do not.
- False readiness: the event schema, sequence and vocabulary admit only
  `sentinel_activated` then `stock_headless_hmr_ready`.
- Overclaim: a pass proves pre-worker Harness readiness only, not DeepSeek model,
  worker, product-runtime or longitudinal reliability.

## Residual risk

The proof exercises one Windows process and one prerelease Harness build. It
does not exercise the runner or model path; later startup, worker or provider
defects can still exist and require separately frozen evidence.
