# Ariadne agent-error and correction register — revision 563

Date: 2026-08-19
Timestamp: 2026-08-19T11:53:31.2243631+10:00 (Australia/Brisbane)

## Revision scope

Revision 563 preserves AER-0653. The first terminal closeout suite correctly changed the live operation latch to `blocked`, then exposed that the accepted migration and predecessor focused suites still reused that mutable current latch as historical construction evidence. Eight paths rejected with `active_operation_mismatch`, and two assertions still required the old `in_progress` state.

The correction binds historical replay to each tranche's immutable admitted preplanning latch while retaining separate assertions over the current terminal latch. No migration engine or reviewed candidate behavior changed. The register contains 653 incidents, all corrected or contained and none open.

Final end-to-end rehearsal and closeout cost is twenty-one reruns. The exact corrected Gemini input remains sixteen; the post-review closeout reports the legacy register aggregate, terminal-current fixture, exact-stage, peer-link and incomplete latch-only replay corrections separately. Historical replay now loads all seven mutable canonical oracles from exact reviewed commit `d03cc6386fdf3e2714881089514380d93824e160`, not from live `current` paths. Projected clockwork-owned representative steady-state corrective reruns remain zero.

## Prevention

An accepted rehearsal's replay suite must bind every mutable canonical oracle to one immutable full Git commit. A `current` projection may be tested only as present state; it must never be historical construction evidence for a completed tranche.
