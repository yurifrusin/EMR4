# Synthetic Silver Action/Temporal Tranche — Sol Acceptance

Date: 2026-07-17

## Decision

`accept_partial_pass`

Sol accepts the bounded parser candidate reviewed at code head `13214dab` and
the exact final tranche report hash
`sha256:6a4c89992e7a791164bda581b04ae2216a3c7e2661b4a9f29963b220d90b9db2`.

## Acceptance basis

- The 24-candidate selection was frozen before parser changes and binds the
  accepted 192-record Silver corpus and immutable baseline report.
- Candidate adaptation changes dialogue/evidence and benign metadata only;
  interpretation receives dialogue plus reference date, never expected fields.
- Eleven action and ten temporal assertions now pass without scorer leakage.
- The parser does not invent duration or time values absent from dialogue.
- The exact tranche is 2/24 complete, safety 48/48, and zero variance.
- The full Silver set improves from 2/192 to 11/192, remains safety 384/384,
  and has zero variance.
- Exact parent comparison changes only 32 ordinary-development scenarios, all
  authored resize cases formerly read as create; none intersects LC4R10.
- 530 active focused and preservation nodes pass across the recorded serial
  gates, with exactly two immutable historical report-regeneration nodes
  excluded from the active preservation set.
- Fresh Gemini independently reproduced all material claims and returned
  `DECISION: pass` with `PROTECTED_ACCESS: false`.

## Residual disposition

The 22 remaining selected failures are not accepted as additional parser
targets. They expose candidate/source-oracle evidence omissions,
clarification-policy inconsistencies, entity-transition labels, or replay
delta vocabulary/shape gaps. No scorer weakening or hidden-value invention is
accepted.

The next material choice is a corpus/admission coherence audit, not automatic
parser or replay repair.

## Boundary

V1-V10 remain sealed. No historical diary, external corpus, provider, runtime,
route, API, database, UI, confirmation, deployment, release, or write authority
was accessed or changed.

DECISION: accept_partial_pass
TRANCHE_COMPLETE: 2/24
FULL_SILVER_COMPLETE: 11/192
SAFETY_PASS: 384/384
VARIANCE: 0
PROTECTED_ACCESS: false
