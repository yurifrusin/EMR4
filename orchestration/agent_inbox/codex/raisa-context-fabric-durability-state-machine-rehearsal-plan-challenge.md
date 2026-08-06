# Durability state-machine rehearsal plan challenge

Date: 2026-08-06

Exact reviewed head: `e07cb708bd1b36e01b22cae0911ee75829110681`

Decision: `revision_required`

## Findings

- P0: none.
- P1: retention accepted a caller-supplied eligible-generation checkpoint
  population without proving that it was the complete non-consumed-generation
  census, so omission of the slowest generation could authorize purge.
- P1: restart proposed deriving a rebase successor and its prior contiguous
  coordinate from a candidate whose integrity digest had failed; corrupt state
  cannot supply a trusted recovery coordinate.
- P1: the plan modeled static key intervals but not the parent architecture's
  atomic future-position-fenced routine rotation with predecessor-key
  availability through the required overlap.
- P2: none.

## Deterministic reconciliation and postconditions

The reviewer ran the two exact plan/parent test files serially: 62 passed.
Before and after review, HEAD was
`e07cb708bd1b36e01b22cae0911ee75829110681`, branch was
`codex/review-durability-state-machine-plan-e07cb708`, and the tracked review
worktree/index were clean. Local/origin `master` and `handoff/current` remained
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. No file, ref, provider, network,
database, source or runtime state was changed.

The findings block implementation admission until Sol freezes a complete
census proof, an independently trusted recovery anchor with terminal corrupt-
state handling, and an atomic position-fenced key-rotation transition, followed
by a fresh no-finding review.
