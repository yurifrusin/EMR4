# Threat-model delta — pure check-in environment evidence-gate evaluator

Date: 2026-08-23

Timestamp: 2026-08-23T11:42:25.0002138+10:00 (Australia/Brisbane)

Status: `frozen_narrow_delta`

## New asset and trust boundary

The new asset is a capability-free typed reading derived solely from two
accepted in-memory normalization results and an explicit evaluation time. The
normalization-result dataclasses are caller-constructible data, not capability
tokens, so the evaluator rechecks their critical shape and bindings.

## Threats and controls

- Ambient-time or last-known-good authority: accept only an explicit aware
  `datetime`; never call a clock; use half-open freshness windows.
- Ambiguous manifest selection: accept an exact tuple, deny zero and more than
  one valid manifest distinctly, and never choose on behalf of the caller.
- Forged normalized object: require exact classes, closed constants, full
  lowercase Git-object and digest syntax, slot order, positive generations and
  parseable normalized times.
- Cross-environment or replayed evidence: bind environment, generation and
  authority object across every record and deny any mismatch before role or
  rotation satisfaction.
- Self-asserted role posture: require closed categorical observations, a fresh
  artifact and a verifier reference separate from every evidence reference.
- Old-key or duplicated-evidence reuse: bind each row to exact slot/key/version/
  reference metadata and require distinct evidence references and artifacts.
- Emergency bypass: only matching fresh `deny_only` / `inactive` posture may
  continue; every other state denies and no result has an effect method.
- Satisfied-reading escalation: keep the module unmounted and return no
  admission, command, route, secret, credential or database capability.

## Residual risk

The evaluator cannot establish that a supplied artifact, Git object,
environment or verifier exists or is trustworthy. Those remain external
operational facts. A future admission seam must consume only authorized facts
and must independently retain default denial; this tranche does not authorize
that seam.
