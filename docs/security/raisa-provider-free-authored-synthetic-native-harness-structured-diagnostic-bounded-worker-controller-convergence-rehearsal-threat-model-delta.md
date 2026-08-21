# Threat-model delta: provider-free structured diagnostic bounded-worker controller convergence

Date: 2026-08-21

Status: `frozen`

This delta is limited to the controller seam. It adds no occupied execution,
provider, product, data, deployment or protected-integration authority.

| Threat | Fail-closed control | Deterministic evidence |
|---|---|---|
| Forged or stale sidecar upgrades an opaque failure to v2 | Require canonical bytes, exact in-root path and exact operation/attempt/full-Git identity | valid, wrong-identity, noncanonical and escaped fixtures |
| Missing diagnostic is mistaken for structured success | Build v1 first, retain it, emit only `structured_diagnostic_absent`, and make the future attempt fail closed | absent-sidecar fixture |
| Dynamic exception material leaks into durable evidence | Reuse the accepted closed-coordinate diagnostic validator; persist no raw text, stack, path or environment value | secret-shaped fixture and terminal byte inspection |
| Wrapper or sidecar escapes the disposable root | Fixed leaf paths plus resolved-root containment and symlink rejection | path and source-order checks |
| Direct entrypoint launch bypasses the diagnostic gear | Build argv only through the accepted wrapper launch-command builder before the controller's single `Popen` | controller source projection |
| Safe terminal is destroyed with raw evidence | Require exclusive validated terminal write outside the root before exact root removal | source ordering and isolated writer fixtures |
| Historical attempts are silently reclassified | Freeze byte digests for all consumed markers and terminals; read no historical raw streams | immutable-artifact digest projection |
| Integration accidentally exercises a provider | Acceptance runs only pure Python fixtures and source projections; subprocess launch is forbidden | zero-count process boundary and test guard |

Residual risk: a separately authorised occupied attempt is still required to
prove the converged controller against the native runtime. This tranche proves
source and lifecycle composition only.

