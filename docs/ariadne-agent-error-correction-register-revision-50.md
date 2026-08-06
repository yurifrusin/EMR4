# Ariadne agent-error register revision 50

Date: 2026-08-06

Status: migration/transaction admission-conflict recovery active

## AER-0051 remains open

The first fresh exact-head veto rejected candidate
`bea7d7193503c9176acea24395d3b7727f617454` for five architecture defects in
authenticated handoff, source-independent redelivery, recovery-anchor
representation, atomic lifecycle effects and key-schedule scope. Recovery
candidate `5de1ba511910335ea2ee73f12877ee886639c836` repaired those five defects.

The second genuinely fresh exact-head veto nevertheless found two residual P1
defects. A sole immutable admission row could not durably represent a conflicting
same-position packet or observation-digest reuse without overwrite, leaving the
stored-locator-only coordinator unable to see the conflict, especially after
source purge. The plan also ambiguously said a pending recovery anchor blocked
admission processing, when the intended fence applies to coordinator
consumption and next decision/rotation transitions.

Sol preserved both rejected candidates and extended the same recovery lease.
The second recovery retains the exact 18-relation catalogue but makes
`context_proofread_observation_admission` a bounded receiver-owned attempt
relation: at most one immutable `PRIMARY` plus one immutable `CONFLICT` sentinel
per generation/position. Retained-evidence-first comparison makes exact
duplicates inert, records the first mismatch/reuse with authenticated binding,
source coordinate, attempted digest and a closed reason, remains visible after
source purge and prevents unbounded conflict-row growth. The coordinator loads
the complete stored admission set by locator and any conflict forces atomic
rebase before redelivery success. Primary and conflict evidence are retained
together with receipt/checkpoint meaning.

Pending anchors now explicitly allow bounded receiver-owned admission appends
while fencing coordinator consumption and every next decision or rotation
lifecycle transition. A genuinely fresh exact-head veto remains required before
plan acceptance or the inert DDL rehearsal.

## AER-0052 corrected

The first review-worktree environment-bootstrap incident remains corrected. The
second veto used the proven absolute system interpreter with `--noconftest`, no
cache and no bytecode, passed 5/5 focused checks, and left its exact candidate
worktree unchanged. Future read-only reviewer packets continue to forbid `uv`,
`pip` and environment bootstrap.

Revision 50 contains 52 bounded incidents: 40 agent-behaviour observations,
three harness failures, two repository defects and seven transport timeouts.
AER-0051 is the sole open incident. Counts remain workflow-improvement signals
and do not establish model, provider, transport or role causation.
