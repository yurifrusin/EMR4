# Synthetic Silver All-192 Coherence Audit — Sol Acceptance

Date: 2026-07-17

## Decision

`accept_partial_pass_with_quarantine`

Sol accepts the final audit report hash
`sha256:4e2f3a5dd3632a8d5f927a2d42a203a909673d89d6406ded886eb37bbbfabd80`
and current coherent admission hash
`sha256:55b5c968fa066fc0830e9c80781b0ded1e13520b6f206a41fee9dd0e027687cd`.

## Acceptance basis

- All 192 originally admitted rows were audited against their exact candidate,
  seed, and historical admission bindings.
- Product-parser output did not influence coherence decisions.
- Exactly 12 text-only defects were repaired; IDs, evidence coordinates,
  semantics, provenance, and authority remain unchanged.
- Final current admission is 90 coherent, 102 quarantined, and zero rejected.
- Quarantined rows retain exact reason bindings; no contradiction was hidden by
  changing parser, policy, replay, scorer, or frozen oracle behavior.
- The admitted 90 run twice with 4/90 product complete, safety 180/180, and
  zero variance.
- 536 active focused and preservation tests pass, with exactly two immutable
  historical report-regeneration assertions excluded from the broader active
  gate.
- Fresh Gemini independently reproduced and conceptually accepted the result
  and returned `DECISION: pass` with `PROTECTED_ACCESS: false`.

## Meaning

This is an admission-quality partial pass. It produces a smaller trustworthy
development Silver set; it is not a product robustness pass, Gold promotion,
certification result, or authorization to tune the parser automatically.

The 102 quarantined rows cannot be safely regenerated from their existing
anchors. Restoring balanced 192-row coverage requires a new coherent v2 anchor
contract, especially for clarification and true reversal semantics.

## Boundary

V1-V10 remain sealed. No historical diary, external corpus, provider, runtime,
route, API, database, UI, confirmation, deployment, release, or write authority
was accessed or changed.

DECISION: accept_partial_pass_with_quarantine
ACCEPT: 90
QUARANTINE: 102
REJECT: 0
ACCEPTED_ROBUSTNESS_COMPLETE: 4/90
SAFETY_PASS: 180/180
VARIANCE: 0
PROTECTED_ACCESS: false
