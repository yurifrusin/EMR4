# Ariadne agent-error register revision 47

Date: 2026-08-06

Status: durability count and rotation chronology recovery pending fresh veto

## AER-0050 remains open

The semantic recovery at
`62d0cc5402fe93c4f37cf23f587fc04a7daf01c3` closed the prior structural,
retention-authority and effect-graph defects. Its distinct fresh veto found two
remaining semantic gaps: a third coalesced cause advanced the lossy count bucket
to `FIVE_PLUS`, and a valid rotation revision could be reassigned to the first
audit while preserving the final lifecycle count.

Sol kept the same recovery lease active. Coalescing now derives the exact cause
count from the canonical minimized audit history and exports only the correct
closed bucket, remaining `TWO_TO_FOUR` through cause four. Durability state now
retains a minimal payload-free ordered rotation-revision ledger. Audit revisions
and rotation revisions must be unique, disjoint and together cover every
lifecycle revision exactly. Direct three/four/five-cause and rotation-revision
forgery tests pass locally. AER-0050 remains open until a fourth genuinely fresh
exact-head veto accepts the corrected candidate.

Revision 47 contains 50 bounded incidents: 38 agent-behaviour observations,
three harness failures, two repository defects and seven transport timeouts.
AER-0050 is the sole open incident. Counts remain workflow-improvement signals
and do not establish model, provider, transport or role causation.
