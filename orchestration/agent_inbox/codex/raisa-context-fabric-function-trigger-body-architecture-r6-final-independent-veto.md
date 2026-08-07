# R6 final exact-HEAD independent veto

Date: 2026-08-08

Candidate HEAD: `0bfd3e7545dfa1a7431f856b5eaf2aac32a9292d`

Contract:
`sha256:c8d27c85def134056598be7ef12cda3ae7b509b3d06b16a536459baea51bc24b`

Decision: `revision_required`

## P1 finding

`rotate_observation_key_v1` locks the recovery anchor at the current checkpoint
revision, but its new-rotation branch does not independently compare the
anchor's checkpoint state, contiguous position, observation digest,
checkpoint-integrity digest or seven controlling generation digests with the
locked checkpoint and generation. Its only assertions are the future-position
fence and interval order.

This violates immutable parent invariant
`anchor_fences_next_transition_v1`: no rotation begins until the latest anchor
has been independently reverified as exactly matching committed state.

A stale anchor at the correct locator and revision is therefore admitted. For
example, checkpoint position 10 with stale anchor position 9, prior key ending
at 10 and proposed interval 11–12 passes both existing assertions. The stale
anchor digest then seeds the new lifecycle and checkpoint integrity.

## Other review results

- Exact HEAD and branch were clean before and after review.
- Builder check returned the required contract hash; Ruff and diff checks
  passed.
- The prescribed packet reached 47% with no emitted failure, then was stopped
  because the material P1 made the remainder non-accepting. No complete test
  pass is claimed from review.
- R6A passed independent traversal of all 43 terminal paths; a hostile hoisted
  source read violated replay/conflict locality as expected.
- R6B anchor append retained complete lifecycle, previous-anchor,
  latest-prior-audit, timestamp, digest and replay evidence; hostile removal of
  latest-prior-audit proof was detected. The rotation-entry fence above is a
  separate omission.
- R6C rejected duplicate otherwise-valid key pairs in both set operations.
- R6D gave all 43 paths unique contiguous lock ordinals; a hostile primary lock
  collision invalidated 33 paths.
- No P0, P2 or P3 finding was reported.
- Parent, API Spine, application, migration, Diary, runtime and protected refs
  remained unchanged. Protected refs remain
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Terminal result: `RESULT: revision_required`
