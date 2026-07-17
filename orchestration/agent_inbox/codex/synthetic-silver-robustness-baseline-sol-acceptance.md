# Synthetic Silver Robustness Baseline Sol Acceptance

Date: 2026-07-17

## Decision

`accept_diagnostic_baseline`

Sol accepts the exact report hash
`sha256:18501cf5c8d28c0e660a9f5c7b15f7690622e44c90b248d51301c6ece03973c5`
as complete ordinary-development diagnostic evidence.

## Acceptance basis

- The evaluator binds the admitted 192-candidate corpus, 96 semantic seeds,
  admission decision, original ordinary-development scenarios, and frozen
  interpreter source.
- Candidate adaptation changes dialogue/evidence and benign metadata only.
- Interpretation receives dialogue turns and reference date only; expected
  semantics, outcomes, tools, and deltas remain scorer/replay oracle fields.
- All 192 candidates ran twice for 384 observations.
- The report regenerates exactly, repeat variance is zero, and safety is
  384/384.
- Four evaluator tests plus the existing synthetic corpus and handover archive
  checks pass in the 21-node focused serial gate.
- Fresh Gemini independently reproduced the exact report and returned
  `DECISION: pass` with no protected access.

## Product result and disposition

Only 2/192 candidates pass every dimension; 190 fail. The primary candidate
failures are action extraction 114, temporal/normalization 68, entity semantics
6, and replay-only 2. Raw policy/replay failure counts include upstream
cascades and do not authorize broad policy or replay repair.

The result is accepted as a failure map, not a product pass. No parser or
product change is accepted or authorized in this sprint. The material choice
between a bounded remediation diagnostic and revising/expanding the synthetic
distribution returns to Yuri.

## Boundary

V1-V10 remain sealed. No protected content, historical diary, external corpus,
provider, runtime, route, API, database, UI, confirmation, deployment,
release, or write authority was accessed or changed. The metadata-only
filename incident is recorded and contained.

DECISION: accept_diagnostic_baseline
PRODUCT_COMPLETE: 2
PRODUCT_FAILED: 190
SAFETY_PASS: 384
VARIANCE: 0
PROTECTED_CONTENT_ACCESS: false
